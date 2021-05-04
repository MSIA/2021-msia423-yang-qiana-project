import argparse
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker

from config import logging, engine_string

Base = declarative_base()
logger = logging.getLogger(__name__)


class Survey(Base):
    """Create a data model for the database to be set up for user survey"""

    __tablename__ = 'survey'

    user = Column(Integer, primary_key=True, nullable=False)
    question = Column(String(10), primary_key=True, nullable=False)
    answer = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return f'<Survey user {self.user} question {self.question}'


class Metadata(Base):
    """Create a data model for the database to be set up for user metadata"""

    __tablename__ = 'metadata'

    user = Column(Integer, primary_key=True, nullable=False)
    age = Column(Integer, unique=False, nullable=True)
    gender = Column(Integer, unique=False, nullable=True)
    accuracy = Column(Integer, unique=False, nullable=True)
    country = Column(String(10), unique=False, nullable=True)
    source = Column(Integer, unique=False, nullable=True)
    elapsed = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return f'<Metadata user {self.user}'


def create_new_db(eng_str=engine_string):
    """create new (empty) tables in AWS RDS"""
    try:
        engine = sqlalchemy.create_engine(eng_str)
        Base.metadata.create_all(engine)
        logger.info("database created - run docker mysql to examine the new tables.")
    except sqlalchemy.exc.OperationalError:
        # Checking for correct credentials
        logger.error("create_db: Access denied! Please enter correct credentials")


if __name__ == '__main__':
    # allow user to specify custom function arguments
    ap = argparse.ArgumentParser(description="Pass custom engine string to create new database.")
    ap.add_argument("-e", "--engine", required=False, type=str, help="rds_mysql_engine_string")
    arg = ap.parse_args()

    # pass custom arguments to upload_data_to_s3
    if arg.engine is None:
        create_new_db()
    else:
        create_new_db(arg.engine)
