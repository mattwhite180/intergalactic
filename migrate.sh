docker exec -it intergalactic_server_1 python3 manage.py migrate auth
docker exec -it intergalactic_server_1 python3 manage.py makemigrations
docker exec -it intergalactic_server_1 python3 manage.py migrate
