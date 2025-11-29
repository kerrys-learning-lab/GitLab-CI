import enum
import gzip
import logging
import math
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
