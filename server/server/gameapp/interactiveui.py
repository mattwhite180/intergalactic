import datetime
import json
import os

from django.contrib.auth.models import AnonymousUser, User
from django.core import serializers
from django.core.management.utils import get_random_secret_key

from gameapp.models import (Game, Planet, Player, Weapon, WeaponBlueprint,
                            get_rand, rand_item_from_list)

main_choice_list = {
    "Q": "Quit Game",
    "M": "Move",
    "P": "Get position",
    "R": "See what planets are nearby",
    "S": "Set direction",
    "D": "Delete/redo models associated with the shell ui",
    "A": "Save player data",
    "L": "List where planets are",
    "F": "Set position of player",
    "Z": "delete and redo setup",
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


def get_input_int(phrase):
    val = input(phrase + ":")
    try:
        return int(val)
    except:
        return get_input_int(phrase)


def pre_setup(min_dist_betw_planets=100):
    if User.objects.filter(username="shell_user").count() == 0:
        u = User.objects.create(username="shell_user")
        u.save()
    else:
        u = User.objects.get(username="shell_user")

    if Game.objects.filter(title="shell_game").count() == 0:
        g = Game.objects.create(
            title="shell_game", owner=u, game_dimentions=min_dist_betw_planets * 10, min_distance_between_planets = min_dist_betw_planets
        )
        g.configure_game()
        g.save()
        planets = g.generate_planet(10)
        for planet in planets:
            planet.save()
    else:
        g = Game.objects.get(title="shell_game")
    if Player.objects.filter(username="shell_player").count() == 0:
        p = g.create_player(u)
        p.save()
    else:
        p = Player.objects.get(username="shell_player")
    return p


def delete_game():
    u = User.objects.get(username="shell_user")
    u.delete()


def run_game():

    p = pre_setup()

    val = get_input(main_choice_list)
    while val != "Q":
        print()
        if val == "M":
            result = p.move()
            print("distance moved: ", result)
        if val == "P":
            result = p.get_position()
            print("current position: ", result)
        if val == "R":
            result = p.get_closest_planets(3)
            planet_list = Planet.objects.filter(id__in=result)
            print("closest planets:")
            for i in planet_list:
                print("\t", i.title, [i.pos_x, i.pos_y], i.get_distance(p))
        if val == "D":
            print("implement... TODO")
        if val == "A":
            p.save()
            print("player saved")
        if val == "S":
            d = get_input_int("set the direction of the player")
            p.set_direction(d)
        if val == "L":
            for i in Planet.objects.filter(game=p.game):
                print(i.title, (i.id), [i.pos_x, i.pos_y], i.get_distance(p))
        if val == "F":
            x = get_input_int("enter the x coord of player")
            y = get_input_int("enter the y coord of player")
            p.set_position(x, y)
        if val == "Z":
            delete_game()
            p = pre_setup()
            print("redo!")
        print()
        val = get_input(main_choice_list)
