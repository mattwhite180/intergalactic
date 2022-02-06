from django.core.management.utils import get_random_secret_key
from django.core import serializers
import datetime
import json
from django.contrib.auth.models import AnonymousUser, User
from gameapp.models import (
    MIN_DISTANCE_BETWEEN_PLANETS,
    Game,
    Planet,
    PlanetBlueprint,
    Player,
    Weapon,
    WeaponBlueprint,
    get_rand,
    rand_item_from_list,
)
import os

main_choice_list = {
    'Q': 'Quit Game',
    'M': 'Move',
    'P': 'Get position',
    'R': 'See what planets are nearby',
    'S': 'Set direction'
}

def get_input(choice_list):
    valid_choices = list()
    for i in choice_list:
        valid_choices.append(i)
        print(i[0], ": ", choice_list[i])
    val = input("[X::]:").upper()
    if val not in valid_choices:
        return get_input(choice_list)
    else:
        return val

def pre_setup():
    if User.objects.filter(username = 'shell_user').count() == 0:
        u = User.objects.create(username = 'shell_user')
        u.save()
    else:
        u = User.objects.get(username = 'shell_user')

    if Game.objects.filter(title='shell_game').count() == 0:
        g = Game.objects.create(title='shell_game', owner=u, game_dimentions = MIN_DISTANCE_BETWEEN_PLANETS * 100)
        g.save()
    else:
        g = Game.objects.get(title="shell_game")
    if Player.objects.filter(username='shell_player').count() == 0:
        p = Player.objects.create(username='shell_player', user=u, game=g)
        p.save()
    else:
        p = Player.objects.get(username='shell_player')
    return p

def run_game():

    p = pre_setup()

    val = get_input(main_choice_list)
    while val != 'Q':
        if val == 'M':
            result = p.move()
            print("distance moved: ", result)
        if val == 'P':
            result = p.get_position()
            print("current position: ", result)
        if val == 'R':
            result = p.get_closest_planets(3)
            planet_list = Planet.objects.filter(id__in=result)
            print("closest planets:")
            for i in planet_list:
                print(i.title, i.position, i.get_distance(p))
        print()
        print()
        val = get_input(main_choice_list)


    