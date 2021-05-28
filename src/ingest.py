import requests
import zipfile36 as zipfile
from io import BytesIO
import pandas as pd
import pickle
import os

import boto3
import botocore.exceptions

from config.flaskconfig import logging, data_source

logger = logging.getLogger('ingest')

# if have time, organize this into a class
def download():
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


def upload_data_to_s3(s3_bucket, s3_path_codebook, s3_path_data):
    """upload data and codebook to s3 bucket without saving the files locally

        Args:
            s3_bucket: str - S3 bucket name
            s3_path_codebook: str - filepath to codebook in S3
            s3_path_data: str - filepath to data.csv in S3

        Returns: None
    """
    # download data
    data, codebook = download()

    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
    except botocore.exceptions.PartialCredentialsError:
        # Checking for valid AWS credentials
        logger.error("Please provide valid AWS credentials")

    # write codebook to target path
    s3.put_object(Body=codebook, Bucket=s3_bucket, Key=s3_path_codebook)

    # write csv to target path - keep the index as 'user'
    data.index.name = 'user'
    data.to_csv(f's3://{s3_bucket}/{s3_path_data}', index=True)
    logger.info(f"Codebook and data uploaded to {s3_bucket}.")


def download_data_from_s3(s3_bucket, s3_path_codebook, s3_path_data):
    """read data and codebook from s3 bucket locally

        Args:
            s3_bucket: str - S3 bucket name
            s3_path_codebook: str - filepath to codebook in S3
            s3_path_data: str - filepath to data.csv in S3

        Returns:
            :obj: pandas dataframe (data.csv) and str (codebook.txt)
    """
    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
    except botocore.exceptions.PartialCredentialsError:
        # Checking for valid AWS credentials
        logger.error("Please provide valid AWS credentials")

    # read codebook
    result = s3.get_object(Bucket=s3_bucket, Key=s3_path_codebook)
    text = result['Body'].read().decode()

    # read csv file
    data = pd.read_csv(f's3://{s3_bucket}/{s3_path_data}')

    logger.info(f"Codebook and data downloaded from {s3_bucket}.")

    return data, text


def upload_model_to_s3(s3_bucket, fitted_model, filepath):
    """upload fitted models to s3 bucket

        Args:
            s3_bucket: str - S3 bucket name
            fitted_model: :obj: sklearn-compatible model - fitted model
            filepath: str - path to save serialized factor analysis model in s3

        Returns: None
    """

    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
    except botocore.exceptions.PartialCredentialsError:
        # Checking for valid AWS credentials
        logger.error("Please provide valid AWS credentials")

    pickle_obj = pickle.dumps(fitted_model)
    # write codebook to target path
    s3.put_object(Body=pickle_obj, Bucket=s3_bucket, Key=filepath)

    logger.info(f"Model uploaded to {s3_bucket}/{filepath}.")


def download_model_from_s3(s3_bucket, fa_path, ca_path):
    """download fitted models from s3 bucket

        Args:
            s3_bucket: str - S3 bucket name
            fa_path: str - path to factor analysis model in s3
            ca_path: str - path to cluster analysis model in s3

        Returns: None
    """

    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
    except botocore.exceptions.PartialCredentialsError:
        # Checking for valid AWS credentials
        logger.error("Please provide valid AWS credentials")

    fa_pickle_obj = s3.get_object(Bucket=s3_bucket, key=fa_path)
    ca_pickle_obj = s3.get_object(Bucket=s3_bucket, key=ca_path)

    logger.info(f"Fitted models downloaded from {s3_bucket}.")

    fa = pickle.loads(fa_pickle_obj)
    ca = pickle.loads(ca_pickle_obj)

    return fa, ca


