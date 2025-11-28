import argparse
import rich_argparse

from . import prepare


DEFAULT_DATA_DIR = './.data'

CLI_STAKEHOLDERS = [
    prepare
]

def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
    local_parser = kwargs['subparsers'].add_parser('data',
                                                  formatter_class=rich_argparse.RichHelpFormatter)

    subparsers = local_parser.add_subparsers()

    for cli in CLI_STAKEHOLDERS:
        cli.add_cli_options(parser, subparsers=subparsers)

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
    for cli in CLI_STAKEHOLDERS:
        cli.process_cli_options(parser, args, **kwargs)
