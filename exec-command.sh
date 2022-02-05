docker-compose down --remove-orphans && \
docker-compose build \
&& docker-compose run server python3 manage.py $1 $2 $3
