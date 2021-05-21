import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

from config.flaskconfig import logging, sql_uri
from src.modeling import OfflineModeling

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

    def clear_table(self):
        """Clear table in case things go wrong in the data ingestion process."""
        session = self.session

        try:
            session.query('user_data').delete()
            session.commit()
        except Exception:
            session.rollback()

    def upload_seed_data_to_rds(self, s3_bucket, data_path, codebook_path):
        """upload reduced features and cluster assignment to rds

        Returns: None
        """
        session = self.session

        # prepare data for bulk upload
        offline_model = OfflineModeling(s3_bucket, data_path, codebook_path)
        pca_features, ca_labels = offline_model.initialize_models()
        users = offline_model.data.user.values
        metadata = offline_model.data.iloc[: 164:].values

        # reformat data
        records = [UserData(users[i], *pca_features[i], ca_labels[i], metadata[i][0], metadata[i][1], metadata[i][3])
                   for i in range(len(users))]

        logging.debug(f'The first record in the database is: {records[0]}')

        try:
            session.add_all(records)
            session.commit()
            logging.info('records committed to database.')
        except Exception:
            logging.error('something is wrong')
            session.rollback()

    def upload_realtime_data_to_rds(self, row):
        """transform and upload realtime user input data to rds

        Args:
            TBA

        Returns: None
        """
        raw_survey = None
        metadata = None

        try:
            transformed_survey = self.fa.transform(raw_survey)
        except Exception:
            logging.error('data cannot be transformed; check if factor analysis model is fitted on seed dataset.')

        try:
            cluster = self.ca.predict(transformed_survey)[0]
        except Exception:
            logging.error('data cannot be assigned a cluster; check if cluster analysis model is fitted on seed '
                          'dataset.')

        # transformed_survey
        # cluster
        # metadata
        # session.add_user_record(something)

if __name__ == '__main__':
    obj = SurveyManager()
    obj.upload_seed_data_to_rds('2021-msia423-yang-qiana', 'raw/codebook.txt', 'raw/data.csv')
    # obj.clear_table()
