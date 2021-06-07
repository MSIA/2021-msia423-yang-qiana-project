import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InternalError
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from config.flaskconfig import logging, SQLALCHEMY_DATABASE_URI, FA_PATH, CA_PATH
from src.modeling import OfflineModeling
from src.ingest import Ingest

Base = declarative_base()
logger = logging.getLogger(__name__)


class UserData(UserMixin, Base):
    """Create a data model for the database to be set up for user survey"""

    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=False, nullable=False)
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
    image = Column(String(28500), unique=False, nullable=True)

    def __repr__(self):
        return f'<Survey user {self.name} assigned to cluster {self.cluster}>'


def create_new_db():
    """create database from provided engine string"""
    try:
        engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(engine)
        logger.warning(f'If a user_data table already exists, new schema will not be created.'
                       f'Check mysql database to ensure user_data does not exist.')
        logger.info(f"database created at {SQLALCHEMY_DATABASE_URI}.")
    except sqlalchemy.exc.OperationalError:
        # Checking for correct credentials
        logger.error(f"create_db: Access to {SQLALCHEMY_DATABASE_URI} denied! Please enter correct credentials or "
                     f"check your VPN.")


class SurveyManager(Ingest):

    def __init__(self, app=None, engine_string=SQLALCHEMY_DATABASE_URI):
        """
        Args:
            app: Flask - Flask app
            engine_string: str - Engine string
        """
        super().__init__()
        if app:
            self.db = SQLAlchemy(app)
            self.session = self.db.session
        elif engine_string:
            self.engine = sqlalchemy.create_engine(engine_string)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            raise ValueError("Need either an engine string or a Flask app to initialize")
        logger.debug('Session successfully created.')

    def close(self):
        """Closes session"""
        self.session.close()

    def add_user_record(self, username, password, age, gender, survey, image):
        """Add user survey record to existing database.

        Args:
            username: str - username
            password: str - password
            age: float - age
            gender: float - gender, one-hot encoded
            survey: :obj: pandas dataframe - user survey results as a dataframe with header
            image: str - encoded image

        Returns: None
        """
        session = self.session
        fa, ca = self.download_model_from_s3()
        pca_features = fa.transform(survey)
        cluster = ca.predict(pca_features)[0]
        user_record = UserData(name=username, password=password,
                               age=float(age) if age else None,
                               gender=float(gender) if gender else None,
                               factor1=float(pca_features[0][0]),
                               factor2=float(pca_features[0][1]),
                               factor3=float(pca_features[0][2]),
                               factor4=float(pca_features[0][3]),
                               factor5=float(pca_features[0][4]),
                               factor6=float(pca_features[0][5]),
                               factor7=float(pca_features[0][6]),
                               factor8=float(pca_features[0][7]),
                               factor9=float(pca_features[0][8]),
                               factor10=float(pca_features[0][9]),
                               factor11=float(pca_features[0][10]),
                               factor12=float(pca_features[0][11]),
                               cluster=int(cluster),
                               image=image)
        session.add(user_record)
        session.commit()

    def clear_table(self):
        """Clear table in case things go wrong in the data ingestion process."""
        session = self.session
        session.query(UserData).delete()
        session.commit()
        logger.info('User data table cleared.')

    def drop_table(self):
        """drop user_data table from database."""
        try:
            UserData.__table__.drop(self.engine)
            logger.info('User data table dropped.')
        except InternalError:
            logger.error('Table was not created or was already dropped.')

    def upload_seed_data_to_rds(self):
        """upload reduced features and cluster assignment to rds and save models to s3"""
        session = self.session

        # prepare data for bulk upload
        offline_model = OfflineModeling()
        data = self.download_data_from_s3()[0]
        pca_features, ca_labels = offline_model.initialize_models(data)

        # save models to s3
        self.upload_model_to_s3(offline_model.fa, filepath=FA_PATH)
        self.upload_model_to_s3(offline_model.ca, filepath=CA_PATH)
        logging.info(f'models uploaded to {self.s3}.')

        metadata = data.iloc[:, 164:].values

        # reformat data - just the first 100 records for upload
        records = [UserData(name=f'anonymous user {i}',
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
                            gender=float(metadata[i][1]))
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
            session.rollback()
        except InternalError:
            logging.error('New record contains elements that mysql does not recognize. Maybe you have np.nan in a '
                          'column with type str.')
            session.rollback()
