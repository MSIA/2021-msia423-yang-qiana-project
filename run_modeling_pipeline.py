import argparse
import pandas as pd

from src.ingest import Ingest
from src.modeling import OfflineModeling
from config.flaskconfig import logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    # Add parsers for data ingestion pipeline
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='command')

    # Sub-parser for downloading data
    sb_download = subparsers.add_parser("download_data", description="Download data from s3")
    sb_download.add_argument("-o", '--output', default=None, help="local_output_filepath")

    # Sub-parser for generating features
    sb_fa = subparsers.add_parser("generate_features",
                                  description="generate features with factor analysis")
    sb_fa.add_argument("-i", '--input', default=None, help="local_input_filepath")
    sb_fa.add_argument("-o", '--output', default=None, help="local_output_filepath")

    # Sub-parser for training model
    sb_ca = subparsers.add_parser("train_model", description="train model with cluster analysis")
    sb_ca.add_argument("-i", '--input', default=None, help="local_input_filepath")
    sb_ca.add_argument("-o", '--output', default=None, help="local_output_filepath")

    args = parser.parse_args()
    sp_used = args.command

    model = OfflineModeling()

    if sp_used == 'download_data':
        output = Ingest().download_data_from_s3()[0]

    elif sp_used == 'generate_features':
        data = pd.read_csv(args.input)
        survey = data.iloc[:, 1:164]

        # fit and transform raw survey data with factor analysis
        model.fa.fit(survey)
        arrays = model.fa.transform(survey)
        output = pd.DataFrame(arrays)

    elif sp_used == 'train_model':
        data = pd.read_csv(args.input).values
        model.ca.fit(data)
        clusters = model.ca.labels_
        logger.info('Clusters generated.')
        output = None

    if args.output:
        output.to_csv(args.output, index=False)
        logger.info('Output saved to %s.', args.output)
