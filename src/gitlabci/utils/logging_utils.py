"""
Configures logging.
"""
import argparse
import logging
import logging.config
import rich.logging

CONSOLE_WIDTH=150

def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
    """
    Attaches logging-specific command-line interface (CLI) arguments to the given
    CLI parser.
    """
    logging_group = parser.add_argument_group('Logging')
    verbosity_group = logging_group.add_mutually_exclusive_group()
    verbosity_group.add_argument('-v', '--verbose', action='store_true')
    verbosity_group.add_argument('-s', '--silent', action='store_true')

    logging_group.add_argument('--logging-console-width',
                               type=int,
                               default=CONSOLE_WIDTH,
                               help='Maximum width (in columns) of logging output')

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
    """
    Configures this module according to the provided CLI arguments and keyword
    arguments.
    """
    logging_level = logging.DEBUG if args.verbose else logging.ERROR if args.silent else logging.INFO
    logging_config = kwargs.get('logging')

    global CONSOLE_WIDTH
    CONSOLE_WIDTH=args.logging_console_width

    for logger in ['urllib3.connectionpool']:
        logger = logging.getLogger(logger)
        logger.setLevel(logging.ERROR)

    if logging_config:
        logging_config['loggers'][''] = {
            'handlers': ['stdout' if args.no_color else 'colorized_stdout'],
            'level': logging_level
        }
        logging.config.dictConfig(logging_config)
    else:
        console = rich.console.Console(width=args.logging_console_width)
        logging.basicConfig(format='%(name)15s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging_level,
                            handlers=[rich.logging.RichHandler(console=console)])

