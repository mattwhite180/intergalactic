echo from django.contrib.auth.models import AnonymousUser, User
echo 'from gameapp.models import (
    Game,
    Planet,
    PlanetBlueprint,
    Player,
    Weapon,
    WeaponBlueprint,
    get_rand,
    rand_item_from_list,
)'
echo from django.core.management.utils import get_random_secret_key
echo from django.core import serializers
echo import datetime
echo import json
echo from gameapp.interactiveui import run_game
echo '---------------------------'
docker exec -it intergalactic_server_1 python3 manage.py shell
