import datetime
import json
from secrets import randbelow

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from scipy.stats import binom

MIN_DISTANCE_BETWEEN_PLANETS = 100


def get_rand(min_value, max_value):
    max_value += 1
    random_list = list()
    i = 0
    while min_value + i <= max_value - i:
        for val in range(min_value + i, max_value - i):
            random_list.append(val)
        i += 1
    return random_list[randbelow(len(random_list))]


def rand_item_from_list(l):
    return l[get_rand(0, len(l) - 1)]


class Game(models.Model):
    title = models.CharField(max_length=50)
    game_dimentions = models.IntegerField(default=20000)
    description = models.CharField(max_length=300)
    last_used = models.DateField(auto_now=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def configure_game(self):
        if self.game_dimentions % 10 != 0:
            self.game_dimentions - (self.game_dimentions % 10)
        if self.game_dimentions <= MIN_DISTANCE_BETWEEN_PLANETS * 10:
            self.game_dimentions = MIN_DISTANCE_BETWEEN_PLANETS * 10


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
    pos_x = models.IntegerField(default=40)
    pos_y = models.IntegerField(default=40)

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
    frequency = models.IntegerField()  ## 1 - 99

    def __str__(self):
        return self.title + "(weapon blueprint)"

    def generate(self):
        w = Weapon.objects.create(
            game=self.game,
            title=self.title,
            attack=self.attack,
            attack_val=get_rand(self.min_attack, self.max_attack),
            health=get_rand(self.min_attack, self.max_attack),
            durability=get_rand(self.min_durability, self.max_durability),
        )
        return w


class Planet(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    pos_x = models.IntegerField(default=40)
    pos_y = models.IntegerField(default=40)

    def get_distance(x, y):
        return -1


class PlanetBlueprint(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title + "(planet blueprint)"

    def get_valid_locations(self):
        gd = self.game.game_dimentions
        dim = gd - (gd % MIN_DISTANCE_BETWEEN_PLANETS)
        available_x = list()
        available_y = list()
        p = Planet.objects.filter(game=self.game)
        for i in range(MIN_DISTANCE_BETWEEN_PLANETS, dim, MIN_DISTANCE_BETWEEN_PLANETS):
            p_list = Planet.objects.filter(game=self.game)
            if p_list.filter(pos_x=i).count() == 0:
                available_x.append(i)
            if p_list.filter(pos_y=i).count() == 0:
                available_y.append(i)
        return [available_x, available_y]

    def get_valid_random_location(self):
        l = self.get_valid_locations()
        if len(l[0]) == 0 or len(l[1]) == 0:
            return False
        else:
            rand_x = rand_item_from_list(l[0])
            rand_y = rand_item_from_list(l[1])
            return [rand_x, rand_y]

    def generate(self):
        pos = self.get_valid_random_location()
        if pos == False:
            pos = [0, 0]
        p = Planet.objects.create(
            game=self.game, title=self.title, pos_x=pos[0], pos_y=pos[1]
        )
        return p
