image:
	docker build -t qiana_project .

mysql_init:
	docker pull mysql:5.7.33

mysql:
	docker run -it --rm mysql:5.7.33 mysql -h$$MYSQL_HOST -u$$MYSQL_USER -p$$MYSQL_PASSWORD

ingest:
	docker run -it -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY qiana_project run.py ingest

create_db_rds:
	docker run -it -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME qiana_project run.py create_db

create_db_local:
	docker run -it qiana_project run.py create_db

create_db_custom:
	docker run -it -e SQLALCHEMY_DATABASE_URI qiana_project run.py create_db

