import humanize
import logging
import pathlib
import re
import subprocess
from .. import utils

LOGGER = logging.getLogger('gitlabci.image')

class ImageNotExistsError(RuntimeError):
  ''' Raised when an error occurs while saving an image '''

class ImageSaveError(RuntimeError):
  ''' Raised when an error occurs while saving an image '''

class ImageLoadError(RuntimeError):
  ''' Raised when an error occurs while loading an image '''

class ImagePushError(RuntimeError):
  ''' Raised when an error occurs while pushing an image '''

class ImagePullError(RuntimeError):
  ''' Raised when an error occurs while pulling an image '''

class Image:

  def __init__(self, fullyQualifiedImageName: str):
    self._fullyQualifiedImageName = None
    self.existsLocally = False

    self._checkExistsLocally(value=fullyQualifiedImageName)
    self.fullyQualifiedImageName = fullyQualifiedImageName

  @staticmethod
  def fromManifest(manifest: dict) -> 'Image':
    name = manifest['name']
    remote = manifest.get('destinations', {}).get('remote')
    path = manifest.get('destinations', {}).get('path')

    if not remote and not path:
      return None

    image = Image.fromRemote(remote) if remote else Image.fromFile(name, path)
    image.fullyQualifiedImageName = name
    return image


  @staticmethod
  def fromRemote(fullyQualifiedImageName: str) -> 'Image':
    img = Image(fullyQualifiedImageName)
    img.pull()
    return img

  @staticmethod
  def fromFile(fullyQualifiedImageName: str, path: pathlib.Path) -> 'Image':
    img = Image(fullyQualifiedImageName)
    img.load(path)
    return img

  @property
  def name(self):
    return self._fullyQualifiedImageName[len(self.registry)+1:-len(self.tag)]

  @property
  def fullyQualifiedImageName(self) -> str:
    return self._fullyQualifiedImageName

  @fullyQualifiedImageName.setter
  def fullyQualifiedImageName(self, value):
    if self.fullyQualifiedImageName and value != self.fullyQualifiedImageName and self.existsLocally:
      LOGGER.debug(f'Re-tagging {self.fullyQualifiedImageName} -> {value}')
      subprocess.check_call(['podman', 'image', 'tag', self.fullyQualifiedImageName, value])
    self._fullyQualifiedImageName = value
    self._checkExistsLocally()

  @property
  def registry(self):
    return self.fullyQualifiedImageName.split('/', 1)[0]

  @registry.setter
  def registry(self, value):
    self.fullyQualifiedImageName = value + self.fullyQualifiedImageName[len(self.registry):]

  @property
  def tag(self) -> str:
    return self.fullyQualifiedImageName.rsplit(':', 1)[1]

  @tag.setter
  def tag(self, value):
    self.fullyQualifiedImageName = self.fullyQualifiedImageName[:-len(self.tag)] + value

  def pull(self):
    command = ['podman', 'image', 'pull', self.fullyQualifiedImageName]
    with subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          encoding='utf-8') as proc:
      utils.ProcessPrinter.follow(proc, logger=LOGGER, method='debug')

      if proc.returncode != 0:
        raise ImagePullError(f'Error occured while pulling {self.fullyQualifiedImageName}')

    self._checkExistsLocally(required=True)

  def push(self):
    if not self.existsLocally:
      raise ImagePullError(f'Attempting to push non-existant image: {self.fullyQualifiedImageName}')

    LOGGER.info(f'Pushing {self.fullyQualifiedImageName}')

    command = ['podman', 'image', 'push', self.fullyQualifiedImageName]
    with subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          encoding='utf-8') as proc:
      utils.ProcessPrinter.follow(proc, logger=LOGGER, method='debug')

      if proc.returncode != 0:
        raise ImagePushError(f'Error occured while pushing {self.fullyQualifiedImageName}')

    return self.fullyQualifiedImageName

  def load(self, path: pathlib.Path):
    LOGGER.info(f'Loading {self.fullyQualifiedImageName}')

    command = ['podman', 'image', 'load', '--input', str(path)]
    with subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          encoding='utf-8') as proc:
      utils.ProcessPrinter.follow(proc, logger=LOGGER, method='debug')

      if proc.returncode != 0:
        raise ImageLoadError(f'Error occured while pushing {self.fullyQualifiedImageName}')

    self._checkExistsLocally(required=True)

  def save(self, path: pathlib.Path, compress: bool = True,) -> pathlib.Path:
    if not self.existsLocally:
      raise ImageSaveError(f'Attempting to save non-existant image: {self.fullyQualifiedImageName}')

    filename = f'{utils.slugify(self.fullyQualifiedImageName)}.tar'
    filepath = path / filename

    command = [ 'podman', 'image', 'save']
    command.extend(['--output', filepath])
    command.extend([self.fullyQualifiedImageName])

    with subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          encoding='utf-8') as proc:
      utils.ProcessPrinter.follow(proc, logger=LOGGER)

      if proc.returncode != 0:
        raise ImageSaveError(f'Error occured while saving {filepath}')

      LOGGER.info(f'Saved {filepath} ({humanize.naturalsize(filepath.stat().st_size)})')

    if compress:
      filepath = utils.compress(filepath)
      LOGGER.info(f'Compressed {filepath} ({humanize.naturalsize(filepath.stat().st_size)})')

    return filepath

  def _checkExistsLocally(self, value = None, required = False):
    try:
      command = ['podman', 'image', 'inspect', value or self.fullyQualifiedImageName]
      subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
      self.existsLocally = True
    except subprocess.CalledProcessError:
      if required:
        raise ImageNotExistsError(value or self.fullyQualifiedImageName)
      self.existsLocally = False
