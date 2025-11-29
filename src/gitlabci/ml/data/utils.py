import abc
import boto3
import boto3.session
import botocore.exceptions
import logging
import numpy.typing
import os
import pandas as pd
import pathlib
import tarfile
import zipfile
import sklearn.model_selection

RANDOM_SEED = 42
EXTENSIONS = [None, 'tgz', 'tar.gz', 'tar', 'zip']
LOGGER = logging.getLogger('ml.data')

class TrainTestData:

  @property
  @abc.abstractmethod
  def X_train(self) -> numpy.typing.ArrayLike:
    '''  '''

  @property
  @abc.abstractmethod
  def X_test(self) -> numpy.typing.ArrayLike:
    ''' '''

  @property
  @abc.abstractmethod
  def y_train(self) -> numpy.typing.ArrayLike:
    ''' '''

  @property
  @abc.abstractmethod
  def y_test(self) -> numpy.typing.ArrayLike:
    ''' '''

  def log(self):
    LOGGER.info(f'X_train.shape ==> {self.X_train.shape[0]} rows x {self.X_train.shape[1]} cols')
    LOGGER.info(f'X_test.shape  ==> {self.X_test.shape[0]}  rows x {self.X_test.shape[1]} cols')

    LOGGER.info(f'y_train.shape ==> {self.y_train.shape[0]} rows')
    LOGGER.info(f'y_test.shape  ==> {self.y_test.shape[0]}  rows')


def train_test_split(X, y, test_size=0.2, random_state=None):
  # This will randomly split the data according to the provided ratio (0.2)
  X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X,
                                                                              y,
                                                                              test_size=test_size,
                                                                              random_state=random_state or RANDOM_SEED)

  return X_train, X_test, y_train, y_test

def fetch(name, scope=None) -> pathlib.Path:
  session = boto3.session.Session(aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                                  aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

  endpoint_url = os.environ['ML_DATA_S3_ENDPOINT_URL']
  use_ssl = os.environ['ML_DATA_S3_USE_SSL'].lower() == 'true' if 'ML_DATA_S3_USE_SSL' in os.environ else True
  verify = os.environ['ML_DATA_S3_VERIFY'].lower() == 'true' if 'ML_DATA_S3_VERIFY' in os.environ else True

  LOGGER.debug(f'Connecting to S3 at {endpoint_url}')

  s3 = session.client('s3',
                      endpoint_url=endpoint_url,
                      use_ssl=use_ssl,
                      verify=verify)

  data_path = pathlib.Path('.data')
  data_path.mkdir(parents=True, exist_ok=True)

  for ext in EXTENSIONS:
    object_name = f'{scope}/{name}' if scope else name
    object_name = f'{object_name}.{ext}' if ext else object_name
    LOGGER.debug(f'Trying {object_name}...')

    object_download_path = data_path / scope if scope else data_path
    object_download_path = object_download_path / name
    object_download_path = object_download_path / (f'{name}.{ext}' if ext else name)
    object_download_path.parent.mkdir(parents=True, exist_ok=True)

    try:
      with object_download_path.open('wb') as f:
        s3.download_fileobj(os.environ['ML_DATA_BUCKET_NAME'], object_name, f)
        LOGGER.debug(f'Downloaded {object_download_path}')

        result = _extract(object_download_path, object_download_path.parent)
        LOGGER.info(f'Data is downloaded and available at {result}')
        return result
    except botocore.exceptions.ClientError as ex:
      object_download_path.unlink()
      if '404' not in str(ex):
        raise ex
      # If the error is a '404', then we continue on to the next file extension

  raise RuntimeError()

def _extract(file: pathlib.Path, destination: pathlib.Path) -> pathlib.Path:
  for func in [_extract_tar, _extract_tar_gz, _extract_zip]:
    try:
      return func(file, destination)
    except (zipfile.BadZipFile, tarfile.ReadError):
      pass

  raise RuntimeError()

def _extract_tar(tar_file: pathlib.Path, destination: pathlib.Path) -> pathlib.Path:
  with tarfile.open(str(tar_file), 'r') as tar_ref:
    tar_ref.extractall(destination)

    return destination

def _extract_tar_gz(tar_file: pathlib.Path, destination: pathlib.Path) -> pathlib.Path:
  with tarfile.open(str(tar_file), 'r:gz') as tar_ref:
    tar_ref.extractall(destination)

    return destination

def _extract_zip(zip_file: pathlib.Path, destination: pathlib.Path) -> pathlib.Path:
  with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(destination)

    return destination


def fill_with_median(df, column_name, filter_by_col = None):
  ''' A user-defined function to return a new Pandas Series with the
      median column value (depending on the passed 'column_name'),
      if the field is NaN

      column_name -   the name of the column to be updated ... obviously, this
                      column is also used to derive the median value
      filter_by_col - an option column name to filter by.  If specified, the
                      column will be filtered to match the current
                      row's value for that column prior to calculating the
                      median.
  '''
  df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
  median = df[column_name].median()
  df[column_name] = df[column_name].fillna(median)
