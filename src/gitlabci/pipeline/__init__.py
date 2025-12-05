import argparse
import rich_argparse
from . import info as info_module
from . import version

CLI_STAKEHOLDERS = [
    info_module,
    version,
]

def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
    subparsers = kwargs['subparsers'].add_parser('pipeline',
                                                  formatter_class=rich_argparse.RichHelpFormatter)

    subparsers = subparsers.add_subparsers()

    for cli in CLI_STAKEHOLDERS:
        cli.add_cli_options(parser, subparsers=subparsers)

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
    for cli in CLI_STAKEHOLDERS:
        cli.process_cli_options(parser, args, **kwargs)

Info = info_module.Info
Version = version.PipelineVersion
VersionFactory = version.VersionFactory
