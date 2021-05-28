winpty docker run \
	-it \
	--rm \
	mysql:5.7.33 mysql \
	-h${MYSQL_HOST} \
	-u${MYSQL_USER} \
	-p${MYSQL_PASSWORD}

