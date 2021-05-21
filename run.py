import argparse

import src.ingest as ingest
import src.create_db as create_db

if __name__ == '__main__':

    # Add parsers for data ingestion pipeline
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='command')

    # Sub-parser for downloading data and uploading to S3
    sb_upload = subparsers.add_parser("ingest", description="Upload data to s3")
    sb_upload.add_argument("-b", "--bucket", required=True, type=str, help="s3_bucket_name")
    sb_upload.add_argument("-c", "--codebook", default='raw/codebook.txt', type=str, help="codebook_filepath")
    sb_upload.add_argument("-d", "--data", default='raw/data.csv', type=str, help="data_filepath")

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("-g", "--eng_str", required=False, type=str, help="engine_string")

    args = parser.parse_args()
    sp_used = args.command

    if sp_used == 'create_db':
        # if rds engine string not provided, system first searches sqlalchemy env variable for engine string
        # then, system searches mysql credentials for engine string
        # finally, system uses a default local sqlite credential for engine string
        if args.eng_str is None:
            create_db.create_new_db()
        else:
            create_db.create_new_db(args.eng_str)
    elif sp_used == 'ingest':
        ingest.upload_data_to_s3(args.bucket, args.codebook, args.data)
    else:
        parser.print_help()


