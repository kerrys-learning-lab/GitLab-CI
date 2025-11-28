import abc
import argparse
import importlib
import logging
import numpy as np
import numpy.typing
import pandas as pd
import rich_argparse

from .load import TrainTestDataLoader
from .utils import *

LOGGER = logging.getLogger('ml.data')
DEFAULT_OUTPUT_FILE: pathlib.Path = pathlib.Path('./.data/train-test-data.npz')

class TrainTestDataPreparer(TrainTestData):

  @staticmethod
  @abc.abstractmethod
  def create(**kwargs) -> 'TrainTestDataPreparer':
    ''' Create and return a TrainTestDataPreparer which loads data (possibly
        from remote) and splits the data into train and test segments.

        Concrete classes may perform additional data modifications as necessary
        such as inferring missing data, transforming the data via pipelines,
        etc. '''

  def __init__(self, df:pd.DataFrame, **kwargs) -> None:
    self.df: pd.DataFrame = df
    self._X_train: numpy.typing.ArrayLike|None = None
    self._X_test: numpy.typing.ArrayLike|None = None
    self._y_train: numpy.typing.ArrayLike|None = None
    self._y_test: numpy.typing.ArrayLike|None = None

  def _train_test_split(self):
    self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(self.X, self.y)

  @property
  def X_train(self) -> numpy.typing.ArrayLike:
    if not self._X_train:
      self._train_test_split()

    assert(self._X_train is not None)
    return self._X_train

  @property
  def X_test(self) -> numpy.typing.ArrayLike:
    if not self._X_test:
      self._train_test_split()

    assert(self._X_test is not None)
    return self._X_test

  @property
  def y_train(self) -> numpy.typing.ArrayLike:
    if self._y_train is None:
      self._train_test_split()

    assert(self._y_train is not None)
    return self._y_train

  @property
  def y_test(self) -> numpy.typing.ArrayLike:
    if self._y_test is None:
      self._train_test_split()

    assert(self._y_test is not None)
    return self._y_test

  @property
  @abc.abstractmethod
  def X(self) -> numpy.typing.ArrayLike:
    ''' '''

  @property
  @abc.abstractmethod
  def y(self) -> numpy.typing.ArrayLike:
    ''' '''


def prepare_data(args: argparse.Namespace):
  ''' '''
  module, clazz = args.clazz.rsplit('.', 1)
  module = importlib.import_module(module)
  clazz = getattr(module, clazz)
  instance: TrainTestDataPreparer = clazz.create()

  instance.log()

  save_path: pathlib.Path = pathlib.Path(getattr(args, 'data-output-file'))
  save_path.parent.mkdir(exist_ok=True, parents=True)
  np.savez_compressed(save_path,
                      X_train=instance.X_train,
                      X_test=instance.X_test,
                      y_train=instance.y_train,
                      y_test=instance.y_test)
  LOGGER.info(f'Train/Test data saved to {save_path}')

  if args.verify:
    TrainTestDataLoader.load(save_path)
    LOGGER.info(f'Verified ability to load train/test data from {save_path}')

def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
  local_parser = kwargs['subparsers'].add_parser('prepare',
                                                 formatter_class=rich_argparse.RichHelpFormatter)
  local_parser.set_defaults(func=prepare_data)

  local_parser.add_argument('--verify',
                            action='store_true',
                            help='If specified, verify the ability to load the prepared data file')
  local_parser.add_argument('clazz',
                            help='The fully scoped name (module.submodule.class) of the data preparation class (must extend gitlabci.ml.model.TrainTestData)')
  local_parser.add_argument('data-output-file',
                            default=DEFAULT_OUTPUT_FILE,
                            nargs='?',
                            help=f'The file name to save the data.  Default: {DEFAULT_OUTPUT_FILE}')

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
  ''' '''