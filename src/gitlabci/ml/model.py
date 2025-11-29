import abc
import logging
import mlflow
import mlflow.exceptions
import numpy.typing
import pandas as pd
import typing

LOGGER = logging.getLogger('ml.model')

class ModelCandidate:

  def __init__(self, model, **kwargs) -> None:
    self.kwargs = kwargs
    self.model = model

  @property
  @abc.abstractmethod
  def parameters(self) -> dict:
    pass

  def fit(self, X: pd.DataFrame, y:pd.DataFrame):
    self.model.fit(X, y)

  def predict(self, X: pd.DataFrame):
    return self.model.predict(X)

  @abc.abstractmethod
  def metrics(self, y_true: pd.DataFrame, y_pred: pd.DataFrame) -> dict:
    ''' '''

class ModelCandidateGenerator:

  def __init__(self, name: str, description: str, version:str|None=None, register=True):
    self.name = name
    self.description = description

    if register:
      client = mlflow.MlflowClient()
      try:
        client.create_registered_model(self.name, description=self.description)
        LOGGER.info(f'Registered model exists: {self.name}')
      except mlflow.exceptions.RestException:
        LOGGER.debug(f'Model exists: {self.name}')

      if version:
        client.create_model_version(self.name, version, description=description)

  @abc.abstractmethod
  def generate(self) -> typing.Generator[ModelCandidate, None, None]:
    ''' '''
