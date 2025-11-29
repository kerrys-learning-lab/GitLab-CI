import logging
import pandas as pd

RANDOM_SEED=42

LOGGER = logging.getLogger('ml.jupyter')

def init(level: int = logging.INFO, max_pandas_rows:int=100, random_seed:int=42):
  global RANDOM_SEED
  RANDOM_SEED = random_seed

  for lgr in ['botocore', 'boto3', 's3transfer', 'urllib3']:
    logging.getLogger(lgr).setLevel(logging.ERROR)

  logging.basicConfig(format='%(asctime)s - %(levelname)-6s - %(name)10s - %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S',
                      level=level)

  pd.set_option('display.max_rows', max_pandas_rows)
