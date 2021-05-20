import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

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
    """create database from provided engine string

        Args:
            eng_str: str - Engine string

        Returns: None
    """
    try:
        engine = sqlalchemy.create_engine(eng_str)
        Base.metadata.create_all(engine)
        logger.info(f"database created at {eng_str}.")
    except sqlalchemy.exc.OperationalError:
        # Checking for correct credentials
        logger.error(f"create_db: Access to {eng_str} denied! Please enter correct credentials or check your VPN")


class SurveyManager:

    def __init__(self, app=None, engine_string=sql_uri):
        """
        Args:
            app: Flask - Flask app
            engine_string: str - Engine string
        """
        if app:
            self.db = SQLAlchemy(app)
            self.session = self.db.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        else:
            raise ValueError("Need either an engine string or a Flask app to initialize")

    def close(self):
        """Closes session"""
        self.session.close()

    def add_user_survey(self, user: str, question: str, answer: int):
        """Add user survey record to existing database.

        Args:
            user: str - user id
            question: str - question id
            answer: int - answer

        Returns: None
        """

        session = self.session
        survey_record = Survey(user=user, question=question, answer=answer)
        session.add(survey_record)
        session.commit()
        logger.info(f'User {user}: answer to {question} added to database.')

    def add_user_metadata(self, user: str, age: int, gender: int, accuracy: int,
                          country: str, source: int, elapsed: int):
        """Add user metadata record to existing database.

        Args:
            user: str - user ID
            age: int - user age
            gender: int - user gender, one-hot encoded
            accuracy: int - user self-identified survey result accuracy
            country: str - user country
            source: int - survey platform source
            elapsed: int - time elapsed

        Returns: None
        """

        session = self.session
        metadata_record = Metadata(user=user, age=age, gender=gender,
                                   accuracy=accuracy, country=country,
                                   source=source, elapsed=elapsed)
        session.add(metadata_record)
        session.commit()
        logger.info(f'User {user}: metadata added to database.')

    def add_initial_static_data(self):
        """Add initial raw data into database."""
        # read from s3

        # split dataframe into two dataframes in the format of the tables

        # ingest
        session = self.session

    def clear_table(self, table):
        """Clear table in case things go wrong in the data ingestion process."""
        pass
