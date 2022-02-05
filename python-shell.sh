echo from django.contrib.auth.models import AnonymousUser, User
echo from planapp.models import Goal, Plan, Task, TodoList, UserData, Prize
echo from django.core.management.utils import get_random_secret_key
echo from django.core import serializers
echo import datetime
echo import json
echo '---------------------------'
docker exec -it goalsandplans_server_1 python3 manage.py shell
