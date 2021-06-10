from factor_analyzer.factor_analyzer import FactorAnalyzer
from sklearn.cluster import KMeans
import yaml
from config.flaskconfig import logging

logger = logging.getLogger(__name__)


class OfflineModeling:
    """Class for offline modeling for deployment in production setting"""
    def __init__(self):

        with open('config/modeling.yaml', 'r') as f:
            config = yaml.safe_load(f)

        self.fa = FactorAnalyzer(**config['generate_features'])
        self.ca = KMeans(**config['train_model'])

    def initialize_models(self, data):
        """fit factor and cluster analysis models on raw seed dataset

        Returns:
            (arrays, cluster): tuple - tuple of numpy arrays
        """
        survey = data.iloc[:, 1:164]

        # fit and transform raw survey data with factor analysis
        self.fa.fit(survey)
        arrays = self.fa.transform(survey)
        logger.info('survey questions are now transformed into 12 latent variables.')

        # fit cluster analysis model on raw survey data with reduced dimensions
        self.ca.fit(arrays)
        clusters = self.ca.labels_
        logger.info('users in the raw seed dataset are now assigned to 10 clusters.')

        return arrays, clusters
