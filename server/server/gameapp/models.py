import datetime

from django.contrib.auth.models import User
from django.db import models
from scipy.stats import binom
from django.utils import timezone
import json
from django.utils.translation import gettext_lazy as _
from secrets import randbelow

def get_rand(min_value, max_value):
    max_value += 1
    random_list = list()
    i = 0
    while min_value + i <= max_value - i:
        for val in range(min_value + i, max_value - i):
            random_list.append(val)
        i += 1
    return random_list[randbelow(len(random_list))]

class Game(models.Model):
    title = models.CharField(max_length=50)
    game_map = TextField(max_length=None default="")
    game_dimentions = models.IntegerField(default=200)
    description = models.CharField(max_length=300)
    last_used = models.DateField(auto_now=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_map(x=0, y=0, distance=2):
        map_size = (distance * 2) + 1

    # have a grid of 'memorized' closest 3 planets

    def configure_game(self):


class Player(models.Model):
    username = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=300)
    last_login_date = models.DateField(auto_now=True)
    is_mod = models.BooleanField(default=True)
    health = models.IntegerField(default=200)
    stamina = models.IntegerField(default=40)
    pos_x = models.IntegerField(default=40)
    pos_y = models.IntegerField(default=40)

    def get_username(self):
        return self.user.username

    def get_id(self):
        return self.user.id


class Weapon(models.Model):
    title = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    durability = models.IntegerField(default=1)
    attack = models.BooleanField(default=False)
    attack_val = models.IntegerField(default=1)
    health = models.IntegerField(default=1)
    owner = models.ForeignKey(Player, models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.title


class WeaponBlueprint(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    min_durability = models.IntegerField(default=1)
    max_durability = models.IntegerField(default=9)
    attack = models.BooleanField(default=False)
    min_attack = models.IntegerField(default=1)
    max_attack = models.IntegerField(default=20)
    min_health = models.IntegerField(default=1)
    max_health = models.IntegerField(default=20)
    frequency = models.IntegerField(min_value=1, max_value=99)

    def __str__(self):
        return self.title + "(weapon blueprint)"

    def generate(self):
        w = Weapon.objects.create(
            game = self.game,
            title = self.title,
            attack = self.attack
            attack_val = get_rand(
                self.min_attack, self.max_attack
            ),
            health = get_rand(
                self.min_attack, self.max_attack
            ),
            durability = get_rand(
                self.min_durability, self.max_durability
            )
        )
        w.save()


class Planet(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    planet_map = TextField(max_length=None default="")
    pos_x = models.IntegerField(default=40)
    pos_y = models.IntegerField(default=40)


class PlanetBlueprint(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title + "(planet blueprint)"
