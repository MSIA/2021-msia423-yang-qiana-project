import pandas as pd
from factor_analyzer.factor_analyzer import FactorAnalyzer
from sklearn.cluster import KMeans

from src.ingest import download_data_from_s3
from src.create_db import SurveyManager
from config.flaskconfig import logging


class OfflineModeling:

    def __init__(self, s3_bucket_name, data_path, codebook_path):
        """
        Args:
            s3_bucket_name: str - s3 bucket name
            data_path: str - path to data csv in s3 bucket
            codebook_path: str - path to codebook text file in s3 bucket
        """
        self.data = download_data_from_s3(s3_bucket_name, data_path, codebook_path)[0]
        self.fa = FactorAnalyzer(n_factors=12, rotation='promax')
        self.ca = KMeans(n_clusters=10, random_state=42)
        self.sql_session = SurveyManager()

    def initialize_models(self):
        """fit factor and cluster analysis models on seed dataset

        Returns:
            :obj: pandas dataframe: transformed features after factor analysis
            :obj: numpy array: assigned cluster(s) after cluster analysis
        """
        features = self.factor_analysis(transform_raw_data=True)
        clusters = self.cluster_analysis(features, assign_seed_data_clusters=True)
        return features, clusters

    def factor_analysis(self, transform_raw_data=False):
        """conduct factor analysis on 163 columns of survey questions
        
        Args:
            transform_raw_data: bool - whether to transform raw data or not

        Returns:
            None or :obj: pandas dataframe: transformed features
        """
        survey = self.data.iloc[:, 1:164]
        self.fa.fit(survey)
        logging.info('factor analysis model successfully fitted on raw seed data.')
        
        if transform_raw_data:
            arrays = self.fa.transform(survey)
            logging.info('seed survey data transformed into 12 latent variables.')
            features = pd.DataFrame(arrays, columns=[f'factor{i}' for i in range(1, 13)])
            return features

    def cluster_analysis(self, features, assign_seed_data_clusters=False):
        """conduct cluster analysis on transformed features

        Args:
            features: pandas dataframe or numpy array - features to perform cluster analysis on
            assign_seed_data_clusters: bool - whether to return cluster assignments for seed data

        Returns:
            None or :obj: numpy array: array of cluster assignments
        """
        self.ca.fit(features)
        logging.info('kmeans model successfully fitted on transformed data.')
        
        if assign_seed_data_clusters:
            return self.ca.labels_

    def upload_seed_data_to_rds(self):
        """upload reduced features and cluster assignment to rds

        Returns: None
        """
        pca_features, ca_labels = self.initialize_models()

        # features - csv, factor1, factor2, ...factor12, etc.
        # clusters - array, 0-9
        # metadata - self.data.iloc[:, 164:]

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
        self.sql_session.add_user_record(something)


if __name__ == '__main__':

    obj = OfflineModeling()
    obj.initialize_models()
    obj.upload_realtime_data_to_rds(something)