import argparse
import datetime
import enum
import logging
import os
import pathlib
import subprocess
import rich_argparse
from rich.console import Console as RichConsole
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree
import sys

from . import base
from ..pipeline.info import Info
from ..pipeline.version import VersionFactory, PipelineVersion
from .. import utils

LOGGER = logging.getLogger('gitlabci.image')

class SaveType(enum.StrEnum):
  FILE = 'file'
  REMOTE = 'remote'

class ImageBuildError(RuntimeError):
  ''' Raised when an error occurs while building an image '''

class ImageBuilder:
  DEFAULT_COMPONENT_SEPARATOR='--'
  DEFAULT_BUILD_CONTEXT = '.'
  DEFAULT_DOCKERFILE = 'Dockerfile'
  DEFAULT_TARGET = '<default>'
  DEFAULT_BUILD_SECRET_NAME = 'gitlab-pat'

  DEFAULT_LOGGABLE_ATTRS = [
    'dockerfile',
    'target',
    'context',
    'labels',
  ]

  DEFAULT_IMAGE_NAME_COMPONENTS = [
     ('context', DEFAULT_BUILD_CONTEXT),
     ('dockerfile', DEFAULT_DOCKERFILE),
     ('target', DEFAULT_TARGET),
  ]

  def __init__(self, info: Info, version: PipelineVersion,
               context=None,
               dockerfile=None,
               target=None,
               component_separator=None):
    self.info = info
    self.version = version
    self.context = context or ImageBuilder.DEFAULT_BUILD_CONTEXT
    self.dockerfile = dockerfile or ImageBuilder.DEFAULT_DOCKERFILE
    self.target = target or ImageBuilder.DEFAULT_TARGET
    self.component_separator = component_separator or ImageBuilder.DEFAULT_COMPONENT_SEPARATOR
    self.imageName = self._createImageName(info, version)
    self.fullyQualifiedImageName = f'{self.info.registryImage}/{self.imageName}:{version.version}'
    self.labels = self._createImageLabels(info, version)

  def build(self, dry_run=False) -> base.Image:
    LOGGER.info(f'Building image: {self.fullyQualifiedImageName}')

    command = self._createBuildCommand()

    if dry_run:
      LOGGER.info(f'Command will be: {command}')
      return

    LOGGER.debug(f'Command will be: {command}')

    with subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          cwd=self.context,
                          encoding='utf-8') as proc:
      utils.ProcessPrinter.follow(proc, logger=LOGGER)

      if proc.returncode != 0:
        raise ImageBuildError(f'Error occured while building {self.fullyQualifiedImageName}')

    return base.Image(self.fullyQualifiedImageName)

  def saveManifest(self, path: pathlib.Path, destinations = None) -> pathlib.Path:
    filename = f'{utils.slugify(self.fullyQualifiedImageName)}.yaml'
    filepath = path / filename

    yamlContent = {
      'image': {
        'name': self.fullyQualifiedImageName,
        'build': self.toDict(),
        'destinations': destinations or {}
      }
    }
    utils.saveYaml(filepath, yamlContent)
    LOGGER.info(f'Wrote manifest {filepath}')


  def logToConsole(self, format: utils.ResultsFormat = None):
    console = RichConsole()

    if format == utils.ResultsFormat.TABLE:
      console.print(self.table)
    if format == utils.ResultsFormat.TREE:
      console.print(self.tree)

  def _createImageName(self, info:Info, version: PipelineVersion) -> str:
    components = [info.projectName]

    context = pathlib.Path(self.context)
    if context.parts:
       components.append('-'.join(context.parts))

    dockerfile = os.path.basename(self.dockerfile)
    dockerfile = dockerfile.replace(ImageBuilder.DEFAULT_DOCKERFILE, '')
    dockerfile = dockerfile.replace('.', '')
    if dockerfile:
       components.append(dockerfile)

    target = self.target
    target = target.replace(ImageBuilder.DEFAULT_TARGET, '')
    if target:
       components.append(target)

    return self.component_separator.join(components)

  def _createImageLabels(self, info: Info, version: PipelineVersion):
    now = datetime.datetime.now(datetime.timezone.utc)
    return [
        f'org.opencontainers.image.created={now.isoformat()}',
        f'org.opencontainers.image.authors={info.commitAuthor}',
        f'org.opencontainers.image.url={info.projectUrl}',
        f'org.opencontainers.image.documentation={info.projectUrl}',
        f'org.opencontainers.image.source={info.projectUrl}',
        f'org.opencontainers.image.version={version.version}',
        f'org.opencontainers.image.revision={info.commitSha}',
        f'org.opencontainers.image.title={info.projectName}',
        f'org.opencontainers.image.description={info.projectDescription}'
    ]

  def _createBuildCommand(self) -> list[str]:
    command = [ 'podman', 'image', 'build']
    command.extend(['--tag', self.fullyQualifiedImageName])
    command.extend(['--file', self.dockerfile])
    command.extend(['--secret', f'id={ImageBuilder.DEFAULT_BUILD_SECRET_NAME},env=GITLAB_PAT'])

    if self.target != ImageBuilder.DEFAULT_TARGET:
      command.extend(['--target', self.target])

    for lbl in self.labels:
      command.extend(['--label', lbl])

    # Context is always current directory... but, the subprocess CWD will be
    # set appropriately
    command.append('.')

    return command

  def toDict(self):
    ret = {}
    for attrName in ImageBuilder.DEFAULT_LOGGABLE_ATTRS:
      ret[attrName] = getattr(self, attrName)

    ret['tags'] = [str(self.version.version)]
    if str(self.version.semanticVersion) not in ret['tags']:
      ret['tags'].append(str(self.version.semanticVersion).replace('+', '--build-'))

    return ret

  @property
  def table(self) -> RichTable:
    table = RichTable(title=self.fullyQualifiedImageName)

    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column('Value', justify='left')

    for attrName in ImageBuilder.DEFAULT_LOGGABLE_ATTRS:
      attrValue = getattr(self, attrName)

      for v in attrValue if isinstance(attrValue, list) else [attrValue]:
        table.add_row(attrName.capitalize(), v)

    return table

  @property
  def tree(self) -> RichTree:
    tree = RichTree(self.fullyQualifiedImageName)

    for attrName in ImageBuilder.DEFAULT_LOGGABLE_ATTRS:
      attrValue = getattr(self, attrName)

      root = tree.add(attrName.capitalize())

      for v in attrValue if isinstance(attrValue, list) else [attrValue]:
        root.add(v)

    return tree

def main(args: argparse.Namespace):
  info: Info = Info.create()
  version: PipelineVersion = VersionFactory.create()

  context = args.context or os.environ.get('GITLABCI_BUILD_IMAGE_CONTEXT', ImageBuilder.DEFAULT_BUILD_CONTEXT)
  dockerfile = args.dockerfile or os.environ.get('GITLABCI_BUILD_IMAGE_DOCKERFILE', ImageBuilder.DEFAULT_DOCKERFILE)
  target = args.target or os.environ.get('GITLABCI_BUILD_IMAGE_TARGET', ImageBuilder.DEFAULT_TARGET)

  try:
    builder = ImageBuilder(info,
                           version,
                           context=context,
                           dockerfile=dockerfile,
                           target=target)

    if args.name_only:
      print(builder.fullyQualifiedImageName)
      sys.exit(0)

    if args.dry_run:
      builder.logToConsole(utils.ResultsFormat.TREE)

    outputPath = pathlib.Path(args.output_dir)
    outputPath.mkdir(parents=True, exist_ok=True)

    image: base.Image = builder.build(dry_run=args.dry_run)

    destinations = {}

    if args.save_file:
      destinations[str(SaveType.FILE)] = str(image.save(outputPath,
                                                        compress=not args.save_uncompressed))

    if args.push_registry:
      image.registry = args.push_registry
      destinations[str(SaveType.REMOTE)] = image.push()

    builder.saveManifest(outputPath, destinations=destinations)
  except ImageBuildError as ex:
    LOGGER.error(str(ex))
    sys.exit(-1)

def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
  local_parser = kwargs['subparsers'].add_parser('build',
                                                 formatter_class=rich_argparse.RichHelpFormatter)

  output_group = local_parser.add_argument_group('Output options')
  output_group.add_argument('--output-dir',
                            type=str,
                            metavar='PATH',
                            default='.',
                            help=f'Directory to save the generated manifest (and, optionally, the image tar).')
  output_group.add_argument('--name-only',
                            action='store_true',
                            help='Don\'t build.  Calculate and print the image name based on the given settings')
  output_group.add_argument('--component-separator',
                            type=str,
                            default=ImageBuilder.DEFAULT_COMPONENT_SEPARATOR,
                            help=f'Separator used between components of the auto-generated image name.  Default: \'{ImageBuilder.DEFAULT_COMPONENT_SEPARATOR}\'')
  output_group.add_argument('--push-registry',
                            type=str,
                            metavar='host[:port]',
                            help=f'Push to the specified image registry instead of $CI_REGISTRY.')
  output_group.add_argument('--save-file',
                            action='store_true',
                            help=f'Save the image to the destination path (see --output-dir) instead of $CI_REGISTRY.')
  output_group.add_argument('--save-uncompressed',
                            action='store_true',
                            help=f'Don\'t compress the saved image file.  Default: False')

  build_group = local_parser.add_argument_group("Build options")
  build_group.add_argument('--dry-run',
                            action='store_true',
                            help='Don\'t build.  Instead log the image build attributes and resulting command')
  build_group.add_argument('--dockerfile',
                           type=str,
                           help=f'Specify build Dockerfile.  Default: {ImageBuilder.DEFAULT_DOCKERFILE}')
  build_group.add_argument('--context',
                           type=str,
                           help=f'Specify build context directory.  Default: {ImageBuilder.DEFAULT_BUILD_CONTEXT}')
  build_group.add_argument('--target',
                           type=str,
                           help=f'Specify the target build stage.  Default: {ImageBuilder.DEFAULT_TARGET}')


  local_parser.set_defaults(func=main)

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
  pass
