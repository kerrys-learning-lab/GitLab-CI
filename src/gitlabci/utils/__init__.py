import enum
import gzip
import hashlib
import logging
import pathlib
import re
import select
import shutil
import subprocess
import yaml

LOGGER = logging.getLogger('gitlabci.utils')

class StorageSizeUnits(enum.StrEnum):
  KB = 'kilobytes'
  MB = 'megabytes'
  GB = 'gigabytes'
  TB = 'terabytes'

class ResultsFormat(enum.StrEnum):
  TABLE = 'table'
  TREE = 'tree'

def truncate(value: str, limit: int = 80, ellipses: str = '..') -> str:
  if limit <= 0:
    return value
  return value[:(limit - len(ellipses))] if len(value) > limit else value

def slugify(value, sub:str = '--') -> str:
    value = value.lower().strip()
    value = re.sub(r"[/:]", sub, value)
    return value

def compress(path: pathlib.Path, removeOriginal=True) -> pathlib.Path:
  compressedFilepath = pathlib.Path(f'{path}.gz')
  with open(path, 'rb') as inFile:
    with gzip.open(compressedFilepath, 'wb') as outFile:
      shutil.copyfileobj(inFile, outFile)

      if removeOriginal:
        path.unlink()

      return compressedFilepath

def saveYaml(path: pathlib.Path, data: list|dict) -> pathlib.Path:
  with open(path, 'w') as outFile:
    yaml.safe_dump(data, outFile, default_flow_style=False)

    return path

class ProcessPrinter:

  @staticmethod
  def follow(proc: subprocess.Popen, logger: logging.Logger=None, method = 'info'):
    logger = logger or LOGGER
    poll = None
    hasError = False
    while poll is None:
      readFds, _, _ = select.select([proc.stdout], [], [], 0.5)

      for fd in readFds:
        line = fd.readline().strip()
        if line:
            hasError = hasError or 'ERROR' in line
            logMethod = getattr(logger, 'error') if hasError else getattr(logger, method)
            logMethod(line)
      poll = proc.poll()


def sha256_checksum(filepath, block_size=65536):
    """
    Calculates the SHA256 checksum of a file efficiently by reading it in
    chunks.

    Args:
        filepath (str or pathlib.Path): The path to the file.
        block_size (int): The size of chunks to read the file in bytes (default 65536).

    Returns:
        str: The hexadecimal representation of the file's SHA256 hash.
    """
    # Create a new SHA256 hash object
    sha256 = hashlib.sha256()

    # Open the file in binary mode ('rb')
    with open(filepath, 'rb') as f:
        # Read the file in chunks and update the hash object
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)

    # Return the hexadecimal digest of the hash
    return sha256.hexdigest()