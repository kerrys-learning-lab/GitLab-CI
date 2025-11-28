import argparse
import logging
import rich_argparse
import yaml
from . import enforcer
from .. import api
from .. import utils

LOGGER = logging.getLogger('gitlabci.project')


def main(args: argparse.Namespace):
   COLORS = {
      'success': 'green',
      'failure': 'red',
      'error': 'yellow',
   }

   config = yaml.safe_load(args.expectations) if args.expectations else {}

   apiInstance = api.Api()
   project = apiInstance.project(args.id)
   e = enforcer.Factory.create('project-settings',
                               f"Project \'{project.name}\' Configuration Status",
                               project=project,
                               **config['project'])

   status = e.enforce(project, subject=f'Project \'{project.name}\'', fix=args.fix)
   status.logToConsole(format=args.format)
   status.exit()


def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
   local_parser = kwargs['subparsers'].add_parser('project',
                                                  formatter_class=rich_argparse.RichHelpFormatter)
   local_parser.add_argument('--format',
                             choices=[ rformat.value for rformat in utils.ResultsFormat],
                             default=utils.ResultsFormat.TABLE,
                             help=f'Display results in the specified format.  Default: {utils.ResultsFormat.TABLE}')
   local_parser.add_argument('--fix',
                             action='store_true',
                             help='Attempt to fix settings')
   local_parser.add_argument('--expectations',
                             type=argparse.FileType('r'),
                             default='/opt/gitlab-ci/data/project-expectations.yaml',
                             help='Path to expectations file (YAML)')
   local_parser.add_argument('id',
                             help='Project ID(s) to interrogate')
   local_parser.set_defaults(func=main)

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
    pass
