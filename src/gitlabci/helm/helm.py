import logging
import pathlib
import subprocess
import yaml
from .. import utils
from ..pipeline.version import PipelineVersion

LOGGER = logging.getLogger('gitlabci.helm')

class ChartBuildError(RuntimeError):
  ''' Raised when an error occurs while building (packaging) a Helm chart '''

class Helm:

  def __init__(self, chartDir: pathlib.Path, version:PipelineVersion):
    self.chartDir = chartDir
    with open(chartDir / 'Chart.yaml', 'r') as chartYamlFileObj:
      self.chart = yaml.safe_load(chartYamlFileObj)
    self.name = self.chart['name']
    self.version = version

  def build(self, outputDir:pathlib.Path) -> pathlib.Path:
    outputDir.mkdir(parents=True, exist_ok=True)

    command = [
      'helm',
      'package',
      '--dependency-update',
      '--version', str(self.version.semanticVersion),
      '--destination', outputDir,
      self.chartDir]
    with subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          encoding='utf-8') as proc:
      utils.ProcessPrinter.follow(proc, logger=LOGGER, method='debug')

      if proc.returncode != 0:
        raise ChartBuildError(f'Error occured while building {self.name}:{self.version}')

    return outputDir.resolve() / f'{self.name}-{self.version.semanticVersion}.tgz'