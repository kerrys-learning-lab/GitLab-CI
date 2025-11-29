import argparse
import rich_argparse
from . import build
from . import push

CLI_STAKEHOLDERS = [
  build,
  push,
]


def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
  local_parser = kwargs['subparsers'].add_parser('image',
                                                 formatter_class=rich_argparse.RichHelpFormatter)
  local_subparser =local_parser.add_subparsers()
  for stakeholder in CLI_STAKEHOLDERS:
      stakeholder.add_cli_options(local_parser, subparsers=local_subparser)

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
  for stakeholder in CLI_STAKEHOLDERS:
      stakeholder.process_cli_options(parser, args)
