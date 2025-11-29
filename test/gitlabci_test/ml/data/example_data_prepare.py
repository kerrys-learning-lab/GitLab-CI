import numpy.typing
import pandas as pd
import sklearn.compose
import sklearn.pipeline
import sklearn.preprocessing
import gitlabci.ml.data

COLUMNS = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'num']
NUMERICAL_COLUMNS = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']
CATEGORICAL_COLUMNS = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']

class TrainTestData(gitlabci.ml.data.TrainTestDataPreparer):

  @staticmethod
  def create(**kwargs) -> gitlabci.ml.data.TrainTestDataPreparer:
    heart_disease_path = gitlabci.ml.data.fetch('heart+disease', scope='uc-irvine')
    df = pd.read_csv(str(heart_disease_path / 'processed.cleveland.data'),
                         names=COLUMNS)

    for c in ['thal', 'ca']:
      gitlabci.ml.data.fill_with_median(df, c)

    return TrainTestData(df, **kwargs)

  def __init__(self, df: pd.DataFrame, **kwargs) -> None:
    super().__init__(df, **kwargs)

    self.pipeline = sklearn.pipeline.Pipeline([
        ('ColumnTransformer', sklearn.compose.ColumnTransformer(transformers=[
            ('Scaler',  sklearn.preprocessing.MinMaxScaler(),  [df.columns.tolist().index(c) for c in NUMERICAL_COLUMNS]),
            ('Encoder', sklearn.preprocessing.OneHotEncoder(), [df.columns.tolist().index(c) for c in CATEGORICAL_COLUMNS])
        ], remainder='passthrough')),
    ])

    self._train_test_split()
    self.pipeline.fit(self._X_train)

  @property
  def label_column(self):
    return 'num'

  @property
  def feature_columns(self):
    return [c for c in self.df.columns if c != self.label_column]

  @property
  def X(self) -> numpy.typing.ArrayLike:
    return self.df[self.feature_columns].values

  @property
  def y(self) -> numpy.typing.ArrayLike:
    return self.df[self.label_column].values

  @property
  def X_train(self) -> numpy.typing.ArrayLike:
    return self.pipeline.transform(self._X_train)

  @property
  def X_test(self) -> numpy.typing.ArrayLike:
    return self.pipeline.transform(self._X_test)

# class ModelCandidate(ml.model.ModelCandidate):

#   def __init__(self, n_neighbors, **kwargs) -> None:
#     kwargs['n_neighbors'] = n_neighbors
#     super().__init__(sklearn.neighbors.KNeighborsClassifier(**ModelCandidate._parameters_from_kwargs(**kwargs)),
#                      **kwargs)

#   @property
#   def parameters(self):
#     return ModelCandidate._parameters_from_kwargs(**self.kwargs)

#   def metrics(self, y_true: pd.DataFrame, y_pred: pd.DataFrame) -> dict:
#     precision = sklearn.metrics.precision_score(y_true, y_pred, average='micro')
#     recall = sklearn.metrics.recall_score(y_true, y_pred, average='micro')
#     f1 = sklearn.metrics.f1_score(y_true, y_pred, average='micro')

#     return { 'precision': precision, 'recall': recall, 'f1': f1 }

#   @staticmethod
#   def _parameters_from_kwargs(**kwargs):
#     return {
#       'weights': kwargs.get('weights', 'distance'),
#       'metric': kwargs.get('metric', 'minkowski'),
#       'p': kwargs.get('p', 2),
#       'n_neighbors': kwargs.get('n_neighbors', 2),
#     }
