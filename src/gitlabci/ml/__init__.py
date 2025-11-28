import abc
import argparse
import importlib
import gitlabci.ml.model
import numpy.typing
import typing
import rich_argparse
from . import data
from ..pipeline.info import Info
from ..pipeline.version import VersionFactory, PipelineVersion

CLI_STAKEHOLDERS = [
    data,
]

def add_cli_options(parser: argparse.ArgumentParser, **kwargs):
    local_parser = kwargs['subparsers'].add_parser('machine-learning',
                                                   aliases=['ml'],
                                                   formatter_class=rich_argparse.RichHelpFormatter)

    subparsers = local_parser.add_subparsers()

    for cli in CLI_STAKEHOLDERS:
        cli.add_cli_options(parser, subparsers=subparsers)

def process_cli_options(parser: argparse.ArgumentParser, args: argparse.Namespace, **kwargs):
    for cli in CLI_STAKEHOLDERS:
        cli.process_cli_options(parser, args, **kwargs)

class SupervisedModelCandidateListener:
  def onStartRun(self, candidate):
    ''' '''

  def preFit(self, candidate, X_train: numpy.typing.ArrayLike, y_train: numpy.typing.ArrayLike):
    return X_train, y_train

  def postPredict(self, candidate, X_test: numpy.typing.ArrayLike, y_pred: numpy.typing.ArrayLike):
    return X_test, y_pred

def supervised(name, clazz, listener: SupervisedModelCandidateListener|None=None):
  import mlflow
  import mlflow.models
  import mlflow.sklearn
  module, clazz = clazz.rsplit('.', 1)
  module = importlib.import_module(module)
  clazz = getattr(module, clazz)
  data: gitlabci.ml.data.TrainTestData = clazz.create()

  listener = listener or SupervisedModelCandidateListener()

  mlflow.set_experiment(experiment_name=name)

  for candidate in module.generator():
    with mlflow.start_run():
      try:
        info: Info = Info.create()
        version: PipelineVersion = VersionFactory.create()

        mlflow.set_tag('release.version', version.version)
        mlflow.set_tag('gitlab.CI_JOB_ID', info.jobId)
        mlflow.set_tag('gitlab.CI_PIPELINE_ID', info.pipelineId)
      except:
         pass

      listener.onStartRun(candidate)

      for p_name, p_value in candidate.parameters.items():
        mlflow.log_param(key=p_name, value=p_value)

      X_train, y_train = listener.preFit(candidate, data.X_train, data.y_train)

      candidate.fit(X_train, y_train)

      y_pred = candidate.predict(data.X_test)

      listener.postPredict(candidate, data.X_test, y_pred)

      for key, value in candidate.metrics(data.y_test, y_pred).items():
        mlflow.log_metric(key=key, value=value)

      mlflow.sklearn.log_model(candidate.model,
                               artifact_path="",
                               signature=mlflow.models.infer_signature(data.X_test, data.y_test))
