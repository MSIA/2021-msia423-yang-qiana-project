image:
	docker build -t qiana_project .

mysql_init:
	docker pull mysql:5.7.33

mysql:
	docker run -it --rm mysql:5.7.33 mysql -h$$MYSQL_HOST -u$$MYSQL_USER -p$$MYSQL_PASSWORD

ingest:
	docker run -it -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e S3_BUCKET qiana_project run.py ingest

create_db_rds:
	docker run -it -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME qiana_project run.py create_db

create_db_local:
	docker run -it qiana_project run.py create_db

create_db_custom:
	docker run -it -e SQLALCHEMY_DATABASE_URI qiana_project run.py create_db

upload_seed:
	docker run -it -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e S3_BUCKET qiana_project run.py upload_seed

clear_table:
	docker run -it -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME qiana_project run.py clear_table

drop_table:
	docker run -it -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME qiana_project run.py drop_table

test/data.csv:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e S3_BUCKET --mount type=bind,source="$(shell pwd)",target=/app/ qiana_project run_modeling_pipeline.py download_data --output=test/data.csv

modeling_data: test/data.csv

test/features.csv: test/data.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ qiana_project run_modeling_pipeline.py generate_features --input=test/data.csv --output=test/features.csv

modeling_features: test/features.csv

modeling_train:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ qiana_project run_modeling_pipeline.py train_model --input=test/features.csv

modeling_test:
	docker run --entrypoint "pytest" qiana_project test

modeling_clear:
	rm test/data.csv test/features.csv

modeling: modeling_data modeling_features modeling_train modeling_test modeling_clear

.PHONY: mysql ingest create_db_rds create_db_local create_db_custom upload_seed clear_table drop_table modeling_data modeling_features modeling_train modeling_test modeling

