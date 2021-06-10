import argparse
from src.ingest import Ingest
import src.create_db as create_db

if __name__ == '__main__':

    # Add parsers for data ingestion pipeline
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='command')

    # Sub-parser for downloading data and uploading to S3
    sb_upload = subparsers.add_parser("ingest", description="Upload data to s3")

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")

    # Sub-parser for uploading optional seed data (100 anonymized records) to database
    sb_seed = subparsers.add_parser("upload_seed", description="Upload seed data to database")

    # Sub-parser for clearing table
    sb_clear = subparsers.add_parser("clear_table", description="Clear all records from table")

    # Sub-parser for dropping table
    sb_drop = subparsers.add_parser("drop_table", description="Drop user_data table")

    args = parser.parse_args()
    sp_used = args.command

    if sp_used == 'create_db':
        create_db.create_new_db()

    elif sp_used == 'ingest':
        Ingest().upload_data_to_s3()

    elif sp_used == 'upload_seed':
        sm = create_db.SurveyManager()
        sm.upload_seed_data_to_rds()
        sm.close()

    elif sp_used == 'clear_table':
        sm = create_db.SurveyManager()
        sm.clear_table()
        sm.close()

    elif sp_used == 'drop_table':
        sm = create_db.SurveyManager()
        sm.drop_table()
        sm.close()

    else:
        parser.print_help()

