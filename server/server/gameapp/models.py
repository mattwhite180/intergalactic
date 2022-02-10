import datetime
import json
import math
from collections import namedtuple
from secrets import randbelow

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from scipy.stats import binom

Point = namedtuple("Point", "x y")

DEFAULT_SPEED = 10
ALPHABET = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]


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
    if len(l) == 0:
        return None
    return l[get_rand(0, len(l) - 1)]


class Game(models.Model):
    title = models.CharField(max_length=50)
    game_dimentions = models.IntegerField(default=10 * 10)
    description = models.CharField(max_length=300)
    last_used = models.DateField(auto_now=True)
    created_date = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    min_distance_between_planets = models.IntegerField(default=10)

    def __str__(self):
        return self.title

    def get_valid_locations(self):
        gd = self.game_dimentions
        dim = gd - (gd % self.min_distance_between_planets)
        available_list = list()
        p_list = Planet.objects.filter(game=self)
        for x in range(
            self.min_distance_between_planets, dim, self.min_distance_between_planets
        ):
            for y in range(
                self.min_distance_between_planets,
                dim,
                self.min_distance_between_planets,
            ):
                if p_list.filter(pos_x=x).filter(pos_y=y).count() == 0:
                    available_list.append(Point(x, y))
        return available_list

    def get_valid_random_location(self, n):
        l = self.get_valid_locations()
        random_list = list()
        for i in range(n):
            rand_point = rand_item_from_list(l)
            random_list.append(rand_point)
            if rand_point != None:
                l.remove(rand_point)
        return random_list

    def generate_planet(self, n=1):
        planet_list = list()
        location_list = self.get_valid_random_location(n)
        for pos in location_list:
            if pos == None:
                pos = Point(-1, -1)
            p = Planet.objects.create(
                game=self,
                title="planet "
                + rand_item_from_list(ALPHABET)
                + "-"
                + str(get_rand(1, 100)),
                pos_x=pos.x,
                pos_y=pos.y,
            )
            planet_list.append(p)
        return planet_list

    def configure_game(self):
        if self.game_dimentions % 10 != 0:
            self.game_dimentions - (self.game_dimentions % 10)
        if self.game_dimentions < self.min_distance_between_planets * 10:
            self.game_dimentions = self.min_distance_between_planets * 10

    def get_random_planet(self):
        if Planet.objects.filter(game=self).count() == 0:
            return False
        else:
            return rand_item_from_list(Planet.objects.filter(game=self))

    def create_player(self, user):
        home_planet = self.get_random_planet()
        if home_planet == False:
            return False
        p = Player.objects.create(
            user=user,
            username=user.username,
            game=self,
            bio=user.username + "'s bio",
            pos_x=home_planet.pos_x,
            pos_y=home_planet.pos_y,
        )
        return p


class Player(models.Model):
    username = models.CharField(max_length=50, default="player")
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    bio = models.CharField(max_length=300, default="enter bio here")
    last_login_date = models.DateField(auto_now=True)
    is_mod = models.BooleanField(default=False)
    health = models.IntegerField(default=200)
    pos_x = models.IntegerField(default=0)
    pos_y = models.IntegerField(default=0)
    direction = models.IntegerField(default=0)

    def get_user_username(self):
        return self.user.username

    def get_user_id(self):
        return self.user.id

    def get_distance(self, obj):
        if hasattr(obj, "pos_x") and hasattr(obj, "pos_y"):
            return math.sqrt(
                (obj.pos_x - self.pos_x) ** 2 + (obj.pos_y - self.pos_y) ** 2
            )
        else:
            return -1

    def get_direction(self):
        return self.direction

    def set_direction(self, d):
        while d < 0:
            d += 360
        if d >= 360:
            d = d % 360
        self.direction = d

    def set_position(self, x, y):
        self.pos_x = x
        self.pos_y = y

    def get_position(self):
        return [self.pos_x, self.pos_y]

    def get_closest_planets(self, n):
        range_distance = self.game.min_distance_between_planets * 2
        my_list = list()
        for p in Planet.objects.filter(game=self.game):
            if self.get_distance(p) <= range_distance:
                my_list.append(p.id)
        return my_list

    def move(self):
        speed = DEFAULT_SPEED
        if Vehicle.objects.filter(owner=self).count() == 1:
            v = Vehicle.objects.get(owner=self)
            speed = v.speed
        d = self.direction + 90  # 0' is up, 90 is left...
        direction_radients = math.pi * d / 180
        change_x = int(speed * math.cos(direction_radients))
        change_y = int(speed * math.sin(direction_radients))
        self.pos_x += change_x
        self.pos_y += change_y
        if self.pos_x > self.game.game_dimentions:
            self.pos_x = self.pos_x % self.game.game_dimentions
        if self.pos_y > self.game.game_dimentions:
            self.pos_y = self.pos_y % self.game.game_dimentions
        return [change_x, change_y]


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

    def generate_weapon(self):
        w = Weapon.objects.create(
            game=self.game,
            title=self.title,
            attack=self.attack,
            attack_val=get_rand(self.min_attack, self.max_attack),
            health=get_rand(self.min_attack, self.max_attack),
            durability=get_rand(self.min_durability, self.max_durability),
        )
        return w


class Vehicle(models.Model):
    title = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    durability = models.IntegerField(default=1)
    attack = models.BooleanField(default=False)
    attack_val = models.IntegerField(default=1)
    health = models.IntegerField(default=1)
    owner = models.ForeignKey(Player, models.SET_NULL, blank=True, null=True)
    pos_x = models.IntegerField(default=40)
    pos_y = models.IntegerField(default=40)
    speed = models.IntegerField(default=40)
    autopilot_y = models.IntegerField(default=-1)
    autopilot_x = models.IntegerField(default=-1)

    def __str__(self):
        return self.title

    def get_distance(self, obj):
        if hasattr(obj, "pos_x") and hasattr(obj, "pos_y"):
            return math.sqrt(
                (obj.pos_x - self.pos_x) ** 2 + (obj.pos_y - self.pos_y) ** 2
            )
        else:
            return -1


class VehicleBlueprint(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    min_durability = models.IntegerField(default=1)
    max_durability = models.IntegerField(default=9)
    attack = models.BooleanField(default=False)
    min_attack = models.IntegerField(default=1)
    max_attack = models.IntegerField(default=20)
    min_health = models.IntegerField(default=1)
    max_health = models.IntegerField(default=20)

    def __str__(self):
        return self.title + "(vehicle blueprint)"

    def generate_vehicle(self, owner):
        v = Vehicle.objects.create(
            owner=owner,
            game=self.game,
            title=self.title,
            attack=self.attack,
            attack_val=get_rand(self.min_attack, self.max_attack),
            health=get_rand(self.min_attack, self.max_attack),
            durability=get_rand(self.min_durability, self.max_durability),
        )
        return v


class Planet(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    pos_x = models.IntegerField(default=40)
    pos_y = models.IntegerField(default=40)

    def __str__(self):
        return self.title

    def set_position(self, x, y):
        self.pos_x = x
        self.pos_y = y

    def get_distance(self, obj):
        if hasattr(obj, "pos_x") and hasattr(obj, "pos_y"):
            return math.sqrt(
                (obj.pos_x - self.pos_x) ** 2 + (obj.pos_y - self.pos_y) ** 2
            )
        else:
            return -1
