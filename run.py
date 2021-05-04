import argparse

import src.ingest as ingest
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

if __name__ == '__main__':

    # Add parsers for downloading data and ingesting data
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers()

    sb_upload = subparsers.add_parser("ingest.upload_data_to_s3", description="Upload data to s3")
    sb_upload.add_argument("--")

    '''
    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting new data
    sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    sb_ingest.add_argument("--artist", default="Emancipator", help="Artist of song to be added")
    sb_ingest.add_argument("--title", default="Minor Cause", help="Title of song to be added")
    sb_ingest.add_argument("--album", default="Dusk to Dawn", help="Album of song being added")
    sb_ingest.add_argument("--engine_string", default='sqlite:///data/tracks.db',
                           help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest':
        tm = TrackManager(engine_string=args.engine_string)
        tm.add_track(args.title, args.artist, args.album)
        tm.close()
    else:
        parser.print_help()
    '''


