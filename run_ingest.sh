docker run -it \
    --env AWS_ACCESS_KEY_ID \
    --env AWS_SECRET_ACCESS_KEY \
    qiana_project src/ingest.py \
    -b <s3_bucket_name> \
    [-c] [<codebook_path>] \
    [-d] [<data_path>]