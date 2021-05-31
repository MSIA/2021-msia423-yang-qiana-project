from factor_analyzer.factor_analyzer import FactorAnalyzer
from sklearn.cluster import KMeans

from src.ingest import download_data_from_s3, upload_model_to_s3
from config.flaskconfig import logging


class OfflineModeling:

    def __init__(self, s3_bucket_name, codebook_path, data_path):
        """
        Args:
            s3_bucket_name: str - s3 bucket name
            data_path: str - path to data csv in s3 bucket
            codebook_path: str - path to codebook text file in s3 bucket
        Returns: None
        """
        self.s3 = s3_bucket_name
        self.data = download_data_from_s3(self.s3, s3_path_codebook=codebook_path, s3_path_data=data_path)[0]
        self.fa = FactorAnalyzer(n_factors=12, rotation='promax')
        self.ca = KMeans(n_clusters=10, random_state=42)

    def initialize_models(self):
        """fit factor and cluster analysis models on raw seed dataset

        Returns:
            (arrays, cluster): tuple - tuple of numpy arrays
        """
        survey = self.data.iloc[:, 1:164]

        # fit and transform raw survey data with factor analysis
        self.fa.fit(survey)
        arrays = self.fa.transform(survey)
        logging.info('survey questions are now transformed into 12 latent variables.')

        # fit cluster analysis model on raw survey data with reduced dimensions
        self.ca.fit(arrays)
        clusters = self.ca.labels_
        logging.info('users in the raw seed dataset are now assigned to 10 clusters.')

        return arrays, clusters

    def save_models(self, fa_path, ca_path):
        """save factor and cluster analysis models to s3

        Args:
            fa_path: str - path to factor analysis model in s3
            ca_path: str - path to cluster analysis model in s3
        Returns: None
        """
        upload_model_to_s3(self.s3, self.fa, fa_path)
        upload_model_to_s3(self.s3, self.ca, ca_path)
        logging.info(f'models uploaded to {self.s3}.')
