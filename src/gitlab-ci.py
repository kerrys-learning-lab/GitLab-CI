#! /usr/bin/env python3

import argparse
import logging
import rich_argparse
import sys
import gitlabci.api
import gitlabci.helm
import gitlabci.image
import gitlabci.ml
import gitlabci.pipeline
import gitlabci.project
import gitlabci.python
import gitlabci.utils.logging_utils

LOGGER = logging.getLogger('gitlab-ci')

# Order is important
# - utils.logging_utils *should* be early in order to facilitate debugging
CLI_STAKEHOLDERS = [
  gitlabci.utils.logging_utils,
  gitlabci.api,
  gitlabci.helm,
  gitlabci.image,
  gitlabci.ml,
  gitlabci.pipeline,
  gitlabci.python,
  gitlabci.project,
]

def main(args: argparse.Namespace):
  pass

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Calculates version information for a given Pipeline',
                                    formatter_class=rich_argparse.RichHelpFormatter)

  subparsers = parser.add_subparsers()

  for stakeholder in CLI_STAKEHOLDERS:
      stakeholder.add_cli_options(parser, subparsers=subparsers)

  args = parser.parse_args()

  if 'func' not in args:
      parser.print_help()
      sys.exit(-1)

  for stakeholder in CLI_STAKEHOLDERS:
      stakeholder.process_cli_options(parser, args)

  args.func(args)
