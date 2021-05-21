import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

from config.flaskconfig import logging, sql_uri

Base = declarative_base()
logger = logging.getLogger('create_db')


class UserData(Base):
    """Create a data model for the database to be set up for user survey"""

    __tablename__ = 'user_data'

    user = Column(Integer, primary_key=True, nullable=False)
    factor1 = Column(Float, unique=False, nullable=True)
    factor2 = Column(Float, unique=False, nullable=True)
    factor3 = Column(Float, unique=False, nullable=True)
    factor4 = Column(Float, unique=False, nullable=True)
    factor5 = Column(Float, unique=False, nullable=True)
    factor6 = Column(Float, unique=False, nullable=True)
    factor7 = Column(Float, unique=False, nullable=True)
    factor8 = Column(Float, unique=False, nullable=True)
    factor9 = Column(Float, unique=False, nullable=True)
    factor10 = Column(Float, unique=False, nullable=True)
    factor11 = Column(Float, unique=False, nullable=True)
    factor12 = Column(Float, unique=False, nullable=True)
    cluster = Column(Integer, unique=False, nullable=False)
    age = Column(Integer, unique=False, nullable=True)
    gender = Column(Integer, unique=False, nullable=True)
    country = Column(String(10), unique=False, nullable=True)

    def __repr__(self):
        return f'<Survey user {self.user} assigned to cluster {self.cluster}.'


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

    def add_user_record(self, user: str, factors: dict, cluster: int, age: int, gender: int, country: str):
        """Add user survey record to existing database.

        Args:
            user: int - user id
            factors: dict - dict of floats corresponding to latent variables 1 to 12
            cluster: int - cluster assignment for user
            age: int - user age
            gender: int - user gender
            country: str - user country

        Returns: None
        """

        session = self.session
        user_record = UserData(user=user, **factors, cluster=cluster, age=age, gender=gender, country=country)
        session.add(user_record)
        session.commit()
        logger.info(f"User {user}'s record added to database.")

    def clear_table(self, table):
        """Clear table in case things go wrong in the data ingestion process."""
        pass
