import argparse
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
    """upload data and codebook to s3 bucket without saving the files locally"""
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


if __name__ == '__main__':

    # allow user to specify custom function arguments
    ap = argparse.ArgumentParser(description="Pass S3 bucket name and data paths to function.")
    ap.add_argument("-b", "--bucket", required=True, type=str, help="s3_bucket_name")
    ap.add_argument("-c", "--codebook", required=False, type=str, help="codebook_filepath")
    ap.add_argument("-d", "--data", required=False, type=str, help="data_filepath")
    arg = ap.parse_args()

    # pass custom arguments to upload_data_to_s3
    bucket = arg.bucket
    cpath = arg.codebook if arg.codebook is not None else 'raw/codebook.txt'
    dpath = arg.data if arg.data is not None else 'raw/data.csv'

    upload_data_to_s3(bucket, cpath, dpath)