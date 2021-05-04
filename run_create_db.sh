docker run -it \
    --env MYSQL_HOST \
    --env MYSQL_PORT \
    --env MYSQL_USER \
    --env MYSQL_PASSWORD \
    --env DATABASE_NAME \
    qiana_project src/create_db.py \
    [-e] [<engine_string>]