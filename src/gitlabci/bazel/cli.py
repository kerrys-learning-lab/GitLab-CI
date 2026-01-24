import argparse
import logging
import rich_argparse
from .module import Module

LOGGER = logging.getLogger('gitlabci.bazel')

def update_bazel_module(args: argparse.Namespace):
  bazel_module = Module(args.name, args.module_base, args.module_template)
  bazel_module.create_version(args.version,
                              args.url,
                              strip_prefix=args.src_strip_prefix)

def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
  local_parser = kwargs['subparsers'].add_parser('bazel',
                                                 formatter_class=rich_argparse.RichHelpFormatter)

  local_subparsers =local_parser.add_subparsers()
  module_subparser = local_subparsers.add_parser('module',
                                                formatter_class=rich_argparse.RichHelpFormatter)
  module_subparser.add_argument('--module-base',
                                type=str,
                                default='modules',
                                help='The path to the registry modules directory')

  module_subparser.add_argument('--module-template',
                                type=str,
                                default=None,
                                help='The template file to use for the module\'s MODULE.bazel file.')

  module_subparser.add_argument('--src-strip-prefix',
                                type=str,
                                default=None,
                                help='The directory prefix to strip from the retrieved source distribution archive, if applicable')

  module_subparser.add_argument('name',
                                type=str,
                                help='The name of the module')
  module_subparser.add_argument('version',
                                type=str,
                                help='The (new) version of the module')
  module_subparser.add_argument('url',
                                type=str,
                                help='The URL to the module\'s (new) source distro')

  module_subparser.set_defaults(func=update_bazel_module)

def process_cli_options(parser: argparse.ArgumentParser,
                        args: argparse.Namespace,
                        **kwargs):
  pass
