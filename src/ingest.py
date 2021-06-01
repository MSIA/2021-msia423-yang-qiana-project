import requests
import zipfile36 as zipfile
from io import BytesIO
import pandas as pd
import pickle
import os

import boto3
import botocore.exceptions

from config.flaskconfig import logging, data_source, s3_bucket, DATA_PATH, CODEBOOK_PATH, FA_PATH, CA_PATH

logger = logging.getLogger('ingest')


class Ingest:

    def __init__(self):
        try:
            self.s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                   aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
        except botocore.exceptions.PartialCredentialsError:
            # Checking for valid AWS credentials
            logger.error("Please provide valid AWS credentials")

    def download(self):
        """download static, publicly available data and codebook"""
        try:
            response = requests.get(data_source)
        except requests.exceptions.RequestException:
            logger.error("Cannot make web requests to download the data source.")
            return 0

        file = zipfile.ZipFile(BytesIO(response.content))
        files = file.namelist()
        with file.open(files[1]) as csv:
            data = pd.read_csv(csv, delimiter='\t')
        with file.open(files[0]) as html:
            codebook = html.read()
        return data, codebook

    def upload_data_to_s3(self):
        """upload data and codebook to s3 bucket"""
        # download data
        data, codebook = self.download()

        # write codebook to target path
        self.s3.put_object(Body=codebook, Bucket=s3_bucket, Key=CODEBOOK_PATH)

        # write csv to target path - keep the index as 'user'
        data.index.name = 'user'
        data.to_csv(f's3://{s3_bucket}/{DATA_PATH}', index=True)
        logger.info(f"Codebook and data uploaded to {s3_bucket}.")

    def download_data_from_s3(self):
        """read data and codebook from s3 bucket"""

        # read codebook
        result = self.s3.get_object(Bucket=s3_bucket, Key=CODEBOOK_PATH)
        text = result['Body'].read().decode()

        # read csv file
        data = pd.read_csv(f's3://{s3_bucket}/{DATA_PATH}')
        logger.info(f"Codebook and data downloaded from {s3_bucket}.")

        return data, text

    def upload_model_to_s3(self, fitted_model, filepath):
        """upload fitted models to s3 bucket

            Args:
                fitted_model: :obj: sklearn-compatible model - fitted model
                filepath: str - path to save serialized factor analysis model in s3

            Returns: None
        """
        pickle_obj = pickle.dumps(fitted_model)
        # write codebook to target path
        self.s3.put_object(Body=pickle_obj, Bucket=s3_bucket, Key=filepath)
        logger.info(f"Model uploaded to {s3_bucket}/{filepath}.")

    def download_model_from_s3(self):
        """download fitted models from s3 bucket"""

        fa_pickle_obj = self.s3.get_object(Bucket=s3_bucket, Key=FA_PATH)['Body'].read()
        ca_pickle_obj = self.s3.get_object(Bucket=s3_bucket, Key=CA_PATH)['Body'].read()
        logger.info(f"Fitted models downloaded from {s3_bucket}.")

        fa = pickle.loads(fa_pickle_obj)
        ca = pickle.loads(ca_pickle_obj)
        logger.info("Fitted models loaded.")

        return fa, ca
