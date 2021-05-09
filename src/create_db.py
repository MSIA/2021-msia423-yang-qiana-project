import argparse

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from config.flaskconfig import logging, sql_uri

Base = declarative_base()
logger = logging.getLogger('create_db')


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


def create_new_db(eng_str=sql_uri):
    """create new (empty) tables in AWS RDS"""
    try:
        engine = sqlalchemy.create_engine(eng_str)
        Base.metadata.create_all(engine)
        logger.info(f"database created at {eng_str}.")
    except sqlalchemy.exc.OperationalError:
        # Checking for correct credentials
        logger.error(f"create_db: Access to {eng_str} denied! Please enter correct credentials or check your VPN")


if __name__ == '__main__':
    # allow user to specify custom engine strings; if not provided, default will be used
    ap = argparse.ArgumentParser(description="Pass custom engine string to create new database.")
    ap.add_argument("-g", "--eng_str", required=False, type=str, help="engine_string")
    arg = ap.parse_args()

    # if rds engine string not provided, system first searches sqlalchemy env variable for engine string
    # then, system searches mysql credentials for engine string
    # finally, system uses a default local sqlite credential for engine string
    if arg.eng_str is None:
        create_new_db()
    else:
        create_new_db(arg.eng_str)
