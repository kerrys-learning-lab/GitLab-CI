import argparse
import logging
import os
import yaml
import rich_argparse
from . import base

LOGGER = logging.getLogger('gitlabci.image')

class ImagePusher:

  def __init__(self, registry=None):
    super().__init__()
    self.registry = registry

  def push(self, imageManifest: dict):
    image = base.Image.fromManifest(imageManifest)

    if not image:
      return

    if self.registry:
      image.registry = self.registry

    for tag in imageManifest.get('build', {}).get('tags', []):
      image.tag = tag
      image.push()


def main(args: argparse.Namespace):
  pusher = ImagePusher(registry=args.registry)

  for manifest in args.manifest:
    manifest = yaml.safe_load(manifest)
    imageManifest = manifest['image']
    pusher.push(imageManifest)

def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
  local_parser: argparse.ArgumentParser = kwargs['subparsers'].add_parser('push',
                                                                          formatter_class=rich_argparse.RichHelpFormatter)

  local_parser.add_argument('--registry',
                            type=str,
                            default=os.environ.get('CI_REGISTRY'),
                            help=f'Specify the address for the target registry.  Defaults to $CI_REGISTRY if present.')
  local_parser.add_argument('manifest',
                            type=argparse.FileType('r', encoding='utf-8'),
                            nargs='+',
                            help=f'Push the images described by the given manifest(s).  May be specified multiple times.')

  local_parser.set_defaults(func=main)

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
  if args.func == main:
    if not args.registry:
      parser.error(f'Registry must be specified using --password or $CI_REGISTRY')
