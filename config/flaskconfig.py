import logging
import os

# logging configurations
logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p',
                    level=logging.DEBUG)

# data source
data_source = 'http://openpsychometrics.org/_rawdata/16PF.zip'

# mysql rds credentials
conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
db_name = os.environ.get("DATABASE_NAME")

# sqlalchemy database engine string; user env variable > rds engine string > local sqlite
sql_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
if sql_uri is None:
    if host is None:
        sql_uri = f'sqlite:///data/data.db'
    else:
        sql_uri = f"{conn_type}://{user}:{password}@{host}:{port}/{db_name}"

# other configurations from the template repo
DEBUG = True
PORT = 5000
APP_NAME = "TBA"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100
