import argparse
import logging
import pathlib
import rich_argparse
import gitlabci.pipeline

LOGGER = logging.getLogger('gitlabci.version')

def version_main(args: argparse.Namespace):
    info: gitlabci.pipeline.Info = gitlabci.pipeline.Info.create()
    version: gitlabci.pipeline.Version = gitlabci.pipeline.VersionFactory.create()

    semver = str(version.semanticVersion)
    protected = 'Yes' if info.commitRefProtected else 'No'
    defaultBranch = 'Yes' if info.commitBranch == info.defaultBranch else 'No'

    LOGGER.info('')
    LOGGER.info( '+-------------------------+--------------------------------+')
    LOGGER.info(f'| Commit Ref Protected?   | {protected or "":<50} |')
    LOGGER.info(f'| Commit Branch           | {info.commitBranch or "":<50} |')
    LOGGER.info(f'| Commit Branch Default?  | {defaultBranch or "":<50} |')
    LOGGER.info(f'| Commit Tag              | {info.commitTag or "":<50} |')
    LOGGER.info( '+-------------------------+--------------------------------+')
    LOGGER.info(f'| Version                 | {version.version:<50} |')
    LOGGER.info(f'| Semantic Version        | {semver:<50} |')
    LOGGER.info(f'| Python Language Version | {version.langPythonVersion:<50} |')
    LOGGER.info(f'| PHP Language Version    | {version.langPhpVersion:<50} |')
    LOGGER.info( '+-------------------------+--------------------------------+')
    LOGGER.info('')


    if args.to_file:
        try:
            writtenPath = version.write(args.to_file, format=args.to_format)
            LOGGER.info(f'Wrote version information to: {writtenPath}')
        except FileExistsError as e:
            LOGGER.error(str(e))

def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
    version_parser = kwargs['subparsers'].add_parser('version',
                                                     formatter_class=rich_argparse.RichHelpFormatter)
    version_parser.add_argument('--to-file',
                                type=pathlib.Path,
                                help='Path to write pipeline version information to')
    version_parser.add_argument('--to-format',
                                type=str,
                                default='env',
                                help='Format to use when writing pipeline version information (default: env)')
    version_parser.add_argument('--force',
                                action='store_true',
                                help='If the specified to-file already exists, overwrite it')
    version_parser.set_defaults(func=version_main)

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
    pass
