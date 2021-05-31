import argparse
import yaml
import pandas as pd

from factor_analyzer.factor_analyzer import FactorAnalyzer
from sklearn.cluster import KMeans

from src.ingest import download_data_from_s3
from config.flaskconfig import s3_bucket, CODEBOOK_PATH, DATA_PATH, logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    with open('config/modeling.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Add parsers for data ingestion pipeline
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='command')

    # Sub-parser for downloading data
    sb_download = subparsers.add_parser("download_data", description="Download data from s3")
    sb_download.add_argument("-b", "--bucket", default=s3_bucket, help="s3_bucket_name")
    sb_download.add_argument("-c", "--codebook", default=CODEBOOK_PATH, help="codebook")
    sb_download.add_argument("-d", "--data", default=DATA_PATH, help="data_filepath")
    sb_download.add_argument("-o", '--output', default=None, help="local_output_filepath")

    # Sub-parser for generating features
    sb_fa = subparsers.add_parser("generate_features", description="generate features with factor analysis")
    sb_fa.add_argument("-i", '--input', default=None, help="local_input_filepath")
    sb_fa.add_argument("-o", '--output', default=None, help="local_output_filepath")

    # Sub-parser for training model
    sb_ca = subparsers.add_parser("train_model", description="train model with cluster analysis")
    sb_ca.add_argument("-i", '--input', default=None, help="local_input_filepath")
    sb_ca.add_argument("-o", '--output', default=None, help="local_output_filepath")

    args = parser.parse_args()
    sp_used = args.command

    if sp_used == 'download_data':
        data, codebook = download_data_from_s3(s3_bucket=args.bucket,
                                               s3_path_data=args.data,
                                               s3_path_codebook=args.codebook)
        output = data

    elif sp_used == 'generate_features':
        data = pd.read_csv(args.input)
        survey = data.iloc[:, 1:164]

        # fit and transform raw survey data with factor analysis
        fa = FactorAnalyzer(**config['generate_features'])
        fa.fit(survey)
        arrays = fa.transform(survey)
        output = pd.DataFrame(arrays)

    elif sp_used == 'train_model':
        data = pd.read_csv(args.input).values
        ca = KMeans(n_clusters=10, random_state=42)
        ca.fit(data)
        clusters = ca.labels_
        logger.info(f'Generated clusters: {clusters[:5]}')
        output = None

    if args.output:
        output.to_csv(args.output, index=False)