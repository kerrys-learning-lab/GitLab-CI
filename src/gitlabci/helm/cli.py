import argparse
import logging
import os
import pathlib
import requests
import rich_argparse
import subprocess
import yaml
from .helm import Helm
from ..pipeline.info import Info
from ..pipeline.version import VersionFactory, PipelineVersion
from .. import utils

LOGGER = logging.getLogger('gitlabci.helm')

PACKAGE_REGISTRY_HELM_REPO_URL_FMT='{api_url}/projects/{id}/packages/helm/{channel}'
PACKAGE_REGISTRY_UPLOAD_URL_FMT='{api_url}/projects/{id}/packages/helm/api/{channel}/charts'

def build(args: argparse.Namespace):
  info: Info = Info.create()
  version: PipelineVersion = VersionFactory.create()

  _add_helm_repos(info, args)

  chartDir = pathlib.Path(args.chart_dir)

  helm = Helm(chartDir, version)
  chartPackagePath = helm.build(pathlib.Path(args.output_dir))

  LOGGER.info(f'Wrote Helm chart package: {chartPackagePath}')

def push(args: argparse.Namespace):
  info: Info = Info.create()
  url = PACKAGE_REGISTRY_UPLOAD_URL_FMT.format(api_url=info.apiUrl,
                                        id=info.projectId,
                                        channel=args.channel)

  LOGGER.debug(f'Chart API URL: {url}')

  auth = (info.registryUser, info.registryPassword.get_secret_value())

  for chartPackageFile in args.package:
    LOGGER.debug(f'Preparing to send {chartPackageFile}')
    with open(chartPackageFile, 'rb') as fd:
      req = requests.post(url, files={'chart': fd}, auth=auth)
      req.raise_for_status()
      LOGGER.info(f'Uploaded {chartPackageFile}')


def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
  local_parser = kwargs['subparsers'].add_parser('helm',
                                                 formatter_class=rich_argparse.RichHelpFormatter)

  local_subparsers =local_parser.add_subparsers()
  local_parser.add_argument('--dependencies',
                             type=argparse.FileType('r'),
                             default='/opt/gitlab-ci/data/helm-repo-dependencies.yaml',
                             help='Path to Helm dependencies file (YAML)')


  build_subparser = local_subparsers.add_parser('build',
                                                formatter_class=rich_argparse.RichHelpFormatter)
  build_subparser.add_argument('--chart-dir',
                               type=str,
                               default='.',
                               help='The directory containing the chart artifacts (i.e., Chart.yaml, etc.).  Default: .')
  build_subparser.add_argument('--output-dir',
                               type=str,
                               default='.',
                               help='Location to write the chart.  Default: .')

  build_subparser.set_defaults(func=build)
  push_subparser = local_subparsers.add_parser('push',
                                               formatter_class=rich_argparse.RichHelpFormatter)
  push_subparser.add_argument('--channel',
                              type=str,
                              default='stable',
                              help='Channel to publish the package (i.e., \'stable\', \'devel\', etc.).  Default: \'stable\'')
  push_subparser.add_argument('package',
                              nargs='+',
                              help='The chart package(s) to push to the registry')
  push_subparser.set_defaults(func=push)


def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
  pass

def _add_helm_repos(info: Info, args: argparse.Namespace):
  config = yaml.safe_load(args.dependencies) if args.dependencies else {}

  for key, value in config.get('helm', {}).items():
    project = value.get('project')

    if not project:
        raise RuntimeError(f'Currently, only internal Helm repositories are supported for dependencies (missing \'project\')')

    command = [
        'helm',
        'repo',
        'add',
        '--username', 'token',
        '--password', os.environ['GITLAB_PAT'],
        key,
        PACKAGE_REGISTRY_HELM_REPO_URL_FMT.format(api_url=info.apiUrl,
                                                  id=project,
                                                  channel=value.get('channel', 'stable'))
    ]
    with subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          encoding='utf-8') as proc:
        utils.ProcessPrinter.follow(proc, logger=LOGGER, method='debug')

        if proc.returncode != 0:
            raise RuntimeError(f'Unable to add dependency: \'{key}\'')
