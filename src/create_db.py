import numpy as np

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InternalError
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from config.flaskconfig import logging, SQLALCHEMY_DATABASE_URI
from src.modeling import OfflineModeling
from src.ingest import download_model_from_s3

Base = declarative_base()
logger = logging.getLogger('create_db')


class UserData(UserMixin, Base):
    """Create a data model for the database to be set up for user survey"""

    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=False, nullable=True)
    password = Column(String(32), unique=False, nullable=False)
    factor1 = Column(Float, unique=False, nullable=False)
    factor2 = Column(Float, unique=False, nullable=False)
    factor3 = Column(Float, unique=False, nullable=False)
    factor4 = Column(Float, unique=False, nullable=False)
    factor5 = Column(Float, unique=False, nullable=False)
    factor6 = Column(Float, unique=False, nullable=False)
    factor7 = Column(Float, unique=False, nullable=False)
    factor8 = Column(Float, unique=False, nullable=False)
    factor9 = Column(Float, unique=False, nullable=False)
    factor10 = Column(Float, unique=False, nullable=False)
    factor11 = Column(Float, unique=False, nullable=False)
    factor12 = Column(Float, unique=False, nullable=False)
    cluster = Column(Integer, unique=False, nullable=False)
    age = Column(Float, unique=False, nullable=True)
    gender = Column(Float, unique=False, nullable=True)
    country = Column(String(10), unique=False, nullable=True)

    def __repr__(self):
        return f'<Survey user {self.name} assigned to cluster {self.cluster}>'


def create_new_db(eng_str=SQLALCHEMY_DATABASE_URI):
    """create database from provided engine string

        Args:
            eng_str: str - Engine string

        Returns: None
    """
    try:
        engine = sqlalchemy.create_engine(eng_str)
        Base.metadata.create_all(engine)
        logger.warning('If a table with the same name already exists, it will not be updated with the new schema.')
        logger.info(f"database created at {eng_str}.")
    except sqlalchemy.exc.OperationalError:
        # Checking for correct credentials
        logger.error(f"create_db: Access to {eng_str} denied! Please enter correct credentials or check your VPN")


class SurveyManager:

    def __init__(self, app=None, engine_string=SQLALCHEMY_DATABASE_URI):
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

    def add_user_record(self, fa_path, ca_path, username, password, age, gender, country, survey):
        """Add user survey record to existing database.

        Args:
            TBA

        Returns: None
        """
        session = self.session
        fa, ca = download_model_from_s3(fa_path=fa_path, ca_path=ca_path)
        features = fa.transform(survey)
        cluster = ca.predict(features)[0][0]
        user_record = UserData(username, password,
                               TBA)
        session.add(user_record)
        session.commit()
        logger.info(f"New user {username} added to database.")

    def clear_table(self, table_name):
        """Clear table in case things go wrong in the data ingestion process."""
        session = self.session

        try:
            session.query(table_name).delete()
            session.commit()
        except Exception:
            session.rollback()

    def upload_seed_data_to_rds(self, s3_bucket, data_path, codebook_path,
                                fa_path, ca_path):
        """upload reduced features and cluster assignment to rds

        Args:
            s3_bucket: str - s3 bucket name
            data_path: str - data csv filepath in s3
            codebook_path: str - codebook text filepath in s3
            fa_path: str - path to save serialized factor analysis model in s3
            ca_path: str - path to save serialized cluster analysis model in s3

        Returns: None
        """
        session = self.session

        # prepare data for bulk upload
        offline_model = OfflineModeling(s3_bucket, data_path, codebook_path)
        pca_features, ca_labels = offline_model.initialize_models()
        offline_model.save_models(fa_path=fa_path, ca_path=ca_path)

        metadata = offline_model.data.iloc[:, 164:].values

        # reformat data - just the first 100 records for upload
        records = [UserData(name=f'fake person {i}',
                            password='00000',
                            factor1=float(pca_features[i][0]),
                            factor2=float(pca_features[i][1]),
                            factor3=float(pca_features[i][2]),
                            factor4=float(pca_features[i][3]),
                            factor5=float(pca_features[i][4]),
                            factor6=float(pca_features[i][5]),
                            factor7=float(pca_features[i][6]),
                            factor8=float(pca_features[i][7]),
                            factor9=float(pca_features[i][8]),
                            factor10=float(pca_features[i][9]),
                            factor11=float(pca_features[i][10]),
                            factor12=float(pca_features[i][11]),
                            cluster=int(ca_labels[i]),
                            age=float(metadata[i][0]),
                            gender=float(metadata[i][1]),
                            country=metadata[i][3] if metadata[i][3] is not np.nan else None)
                   for i in range(100)]

        logging.debug(f'The first record in the database is: {records[0]}.')

        try:
            session.add_all(records)
            session.commit()
            logging.info('records committed to database.')
        except AttributeError:
            logging.error('Something went wrong. Datatype(s) of input feature(s) may be incompatible with datatypes '
                          'in schema.')
            session.rollback()
        except IntegrityError:
            logging.error('New records trespass schema restrictions. Maybe you are trying to upload a primary key '
                          'that already exists or insert NA values in a non-nullable column.')
        except InternalError:
            logging.error('New record contains elements that mysql does not recognize. Maybe you have np.nan in a '
                          'column with type str.')

if __name__ == '__main__':

    sm = SurveyManager()
    sm.clear_table(UserData)


