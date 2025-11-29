import argparse
import gitlab
import logging
import os
import rich_argparse
from rich.console import Console as RichConsole
from rich.table import Table as RichTable

class Api:

    def __init__(self, token=None, url=None):
        self.impl = gitlab.Gitlab(url=url or 'https://gitlab.westsidestreet.net',
                                  private_token=token or os.environ['GITLAB_PAT'])
        self.impl.auth()

    def logToConsole(self):
        table = RichTable(title="GitLab CI Pipeline Information")

        table.add_column("Name", justify="left", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="green")

        for p in self.impl.projects.list(iterator=True):
            table.add_row('Project', f'{p.name} ({p.id})')

        console = RichConsole()
        console.print(table)

    def project(self, id):
        return self.impl.projects.get(id)

LOGGER = logging.getLogger('gitlabci.api')

def api_main(args: argparse.Namespace):
    _ = Api()
    _.logToConsole()

    project = _.impl.projects.get(13)

    found = False
    expected = f'{project.name}-*'
    for branch in project.protectedbranches.list(iterator=True):
        if branch.name == expected:
            expected = branch
            found = True
            break


def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
    version_parser = kwargs['subparsers'].add_parser('api',
                                                     formatter_class=rich_argparse.RichHelpFormatter)
    version_parser.set_defaults(func=api_main)

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
    pass
