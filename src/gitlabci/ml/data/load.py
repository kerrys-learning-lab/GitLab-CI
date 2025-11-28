import numpy as np
import numpy.typing
from .utils import *

class TrainTestDataLoader(TrainTestData):

  @staticmethod
  def load(path: pathlib.Path) -> TrainTestData:
    with np.load(path) as data:
      return TrainTestDataLoader(data['X_train'],
                                 data['X_test'],
                                 data['y_train'],
                                 data['y_test'])

  def __init__(self, X_train, X_test, y_train, y_test) -> None:
    self._X_train = X_train
    self._X_test = X_test
    self._y_train = y_train
    self._y_test = y_test

  @property
  def X_train(self) -> numpy.typing.ArrayLike:
    return self._X_train

  @property
  def X_test(self) -> numpy.typing.ArrayLike:
    return self._X_test

  @property
  def y_train(self) -> numpy.typing.ArrayLike:
    return self._y_train

  @property
  def y_test(self) -> numpy.typing.ArrayLike:
    return self._y_test
