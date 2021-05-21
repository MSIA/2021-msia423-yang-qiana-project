import requests
import zipfile36 as zipfile
from io import BytesIO
import pandas as pd
import os

import boto3
import botocore.exceptions

from config.flaskconfig import logging, data_source

logger = logging.getLogger('ingest')


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


def upload_data_to_s3(s3_bucket, s3_path_codebook='raw/codebook.txt', s3_path_data='raw/data.csv'):
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


def download_data_from_s3(s3_bucket, s3_path_codebook='raw/codebook.txt', s3_path_data='raw/data.csv'):
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


if __name__ == '__main__':

    data, text = download_data_from_s3('2021-msia423-qiana-yang')
    print(data.head(5))
    print(text)
