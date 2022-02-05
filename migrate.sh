docker exec -it goalsandplans_server_1 python3 manage.py migrate auth
docker exec -it goalsandplans_server_1 python3 manage.py makemigrations
docker exec -it goalsandplans_server_1 python3 manage.py migrate
