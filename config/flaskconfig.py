import logging
import os

# logging configurations
logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p',
                    level=logging.INFO)

# data source
DATA_SOURCE = 'http://openpsychometrics.org/_rawdata/16PF.zip'

# s3 credentials
S3_BUCKET = os.environ.get("S3_BUCKET")

# mysql rds credentials
conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
db_name = os.environ.get("DATABASE_NAME")

# sqlalchemy database engine string; user env variable > rds engine string > local sqlite
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI is None:
    if host is None:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///data/data.db'
    else:
        SQLALCHEMY_DATABASE_URI = f"{conn_type}://{user}:{password}@{host}:{port}/{db_name}"

DEBUG = True
PORT = 5000
APP_NAME = "A Fun App"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 10
LOGGING_CONFIG = 'config/logging/logging.conf'
SECRET_KEY = b'123'
MAX_CONTENT_LENGTH = 20500  # limit file size to 20KB
UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']

# file paths
CODEBOOK_PATH = os.environ.get('CODEBOOK_PATH')
if CODEBOOK_PATH is None:
    CODEBOOK_PATH = 'raw/codebook.txt'
DATA_PATH = os.environ.get('DATA_PATH')
if DATA_PATH is None:
    DATA_PATH = 'raw/data.csv'
FA_PATH = os.environ.get('FA_PATH')
if FA_PATH is None:
    FA_PATH = 'model/fa.pkl'
CA_PATH = os.environ.get('CA_PATH')
if CA_PATH is None:
    CA_PATH = 'model/ca.pkl'
