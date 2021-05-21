import pandas as pd
from factor_analyzer.factor_analyzer import FactorAnalyzer

from src.ingest import download_data_from_s3
from config.flaskconfig import logging


class FeatureGeneration:

    def __init__(self, s3_bucket_name, data_path, codebook_path):
        self.data = download_data_from_s3(s3_bucket_name, data_path, codebook_path)[0]
        self.survey = self.data.iloc[:, 1:164]

    def factor_analysis(self):
        """conduct factor analysis on 163 columns of survey questions

            Returns:
                :obj: FactorAnalyzer - fitted feature generation model
        """
        fa = FactorAnalyzer(n_factors=12, rotation='promax')
        fa.fit(self.survey)
        return fa

    def get_seed_features(self):
        """get transformed seed data to perform cluster analysis on

            Returns:
                :obj: pandas dataframe - transformed features
        """
        model = self.factor_analysis()
        arrays = model.transform(self.survey)
        features = pd.DataFrame(arrays, columns=[f'factor_{i}' for i in range(1, 13)])

        return features

    def cluster_analysis(self):
        """conduct cluster analysis on transformed features

            Returns:
                :obj: transformed features and cluster assignment
        """
        features = self.get_seed_features()
        

    def upload_seed_data_to_rds(self):
        """upload features (transformed on raw data) to rds

            Returns: None
        """

    def upload_realtime_data_to_rds(self):



# save results to s3
