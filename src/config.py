import logging
import os

# logging configurations
logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p',
                    level=logging.INFO)
#logger = logging.getLogger(__name__)

# data source
data_source = 'http://openpsychometrics.org/_rawdata/16PF.zip'

# mysql rds credentials
conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
db_name = os.environ.get("DATABASE_NAME")
engine_string = f"{conn_type}://{user}:{password}@{host}:{port}/{db_name}"
