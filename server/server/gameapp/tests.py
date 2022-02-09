import datetime
import unittest

from django.contrib.auth.models import AnonymousUser, User
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .models import (Game, Planet, Player, Point, Vehicle, VehicleBlueprint,
                     Weapon, WeaponBlueprint, get_rand, rand_item_from_list)

# from .views import data_to_json, run_jobs

MIN_DISTANCE_BETWEEN_PLANETS = 10


class GetRandTestCase(TestCase):
    def setUp(self):
        pass

    def test_task_limit(self):
        for i in range(1000):
            min_val = 1
            max_val = 12
            rand_val = get_rand(min_val, max_val)
            val = (min_val <= rand_val) and (max_val >= rand_val)
            expected = True
            errmsg = (
                "value "
                + str(rand_val)
                + " out of range from "
                + str(min_val)
                + " and "
                + str(max_val)
            )
            self.assertEqual(val, expected, errmsg)


class GetRandItemFromListTestCase(TestCase):
    def setUp(self):
        pass

    def test_task_limit(self):
        for i in range(10):
            l = ["a", 123, [1, 2, 3], "asdf", 2.3]
            rand_val = rand_item_from_list(l)
            val = rand_val in l
            expected = True
            errmsg = "value " + str(rand_val) + " not in list: " + str(l)
            self.assertEqual(val, expected, errmsg)


class GameTestCase(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(username="testuser", password="1234")
        g = Game.objects.create(
            title="testgame",
            game_dimentions=4,
            description="test!",
            owner=test_user,
            min_distance_between_planets=MIN_DISTANCE_BETWEEN_PLANETS,
        )
        g.save()
        planet_list = g.generate_planet(7)
        for p in range(len(planet_list)):
            planet_list[p].title = f"planet #{p}"
            planet_list[p].save()

    def test_sanity(self):
        g = Game.objects.get(title="testgame")
        expected = 4
        val = g.game_dimentions
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_configure(self):
        g = Game.objects.get(title="testgame")
        g.configure_game()
        expected = MIN_DISTANCE_BETWEEN_PLANETS * 10
        val = g.game_dimentions
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_game_dimention_configure(self):
        g = Game.objects.get(title="testgame")
        g.configure_game()
        expected = MIN_DISTANCE_BETWEEN_PLANETS * 10
        val = g.game_dimentions
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)


class PlanetTestCase(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(username="testuser", password="1234")
        g = Game.objects.create(
            title="testgame",
            game_dimentions=MIN_DISTANCE_BETWEEN_PLANETS * 10,
            description="test!",
            owner=test_user,
            min_distance_between_planets=MIN_DISTANCE_BETWEEN_PLANETS,
        )
        g.save()
        planet_list = g.generate_planet(2)
        p1 = planet_list[0]
        p1.title = "testplanet1"
        p1.pos_x = 10
        p1.pos_y = 10
        p1.save()
        p2 = planet_list[1]
        p2.title = "testplanet2"
        p2.pos_x = 50
        p2.pos_y = 40
        p2.save()

    def test_sanity(self):
        p = Planet.objects.get(title="testplanet1")
        expected = "testplanet1"
        val = p.title
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_valid_locations(self):
        p1 = Planet.objects.get(title="testplanet1")
        p2 = Planet.objects.get(title="testplanet2")
        val = p1.get_distance(p2)
        expected = 50
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        val = p2.get_distance(p1)
        expected = 50
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)


class PlayerTestCase(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(username="testuser", password="1234")
        g = Game.objects.create(
            title="testgame",
            game_dimentions=MIN_DISTANCE_BETWEEN_PLANETS * 20,
            description="test!",
            owner=test_user,
            min_distance_between_planets=MIN_DISTANCE_BETWEEN_PLANETS,
        )
        g.configure_game()
        g.save()
        planet_list = g.generate_planet(3)
        for p in range(len(planet_list)):
            planet_list[p].title = f"planet #{p}"
            planet_list[p].save()

    def test_sanity_check(self):
        p = Planet.objects.get(title="planet #1")
        expected = "planet #1"
        val = p.title
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_create_player(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        p = g.create_player(u)
        p.save()
        expected = "testuser's bio"
        val = p.bio
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_player_location(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        for p in Planet.objects.filter(game=g)[1:]:
            p.delete()
        planet = Planet.objects.filter(game=g)[0]
        player = g.create_player(u)
        self.assertNotEquals(player, False, "there is an issue with creating a player")
        player.save()
        expected = planet.pos_x
        val = player.pos_x
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        expected = planet.pos_y
        val = player.pos_y
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_create_player_no_planets(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        for i in Planet.objects.filter(game=g):
            i.delete()
        player = g.create_player(u)
        expected = False
        val = player
        errmsg = "expected 'player' to be false since no planets exist on this game"
        self.assertEqual(val, expected, errmsg)

    def test_set_direction(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        player = g.create_player(u)
        player.set_direction(4)
        expected = 4
        val = player.get_direction()
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        player.set_direction(365)
        expected = 5
        val = player.get_direction()
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        player.set_direction(-10)
        expected = 350
        val = player.get_direction()
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        player.set_direction(-360 - 360 - 90)
        expected = 270
        val = player.get_direction()
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_move_up(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        p = g.create_player(u)
        p.set_position(
            MIN_DISTANCE_BETWEEN_PLANETS / 2, MIN_DISTANCE_BETWEEN_PLANETS / 2
        )
        p.save()
        p.set_direction(0)
        p.move()
        pos = p.get_position()
        expected = (MIN_DISTANCE_BETWEEN_PLANETS / 2) + 0
        val = pos[0]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        expected = (MIN_DISTANCE_BETWEEN_PLANETS / 2) + 10
        val = pos[1]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_move_left(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        p = g.create_player(u)
        p.set_position(
            MIN_DISTANCE_BETWEEN_PLANETS / 2, MIN_DISTANCE_BETWEEN_PLANETS / 2
        )
        p.save()
        p.set_direction(90)
        p.move()
        pos = p.get_position()
        expected = (MIN_DISTANCE_BETWEEN_PLANETS / 2) - 10
        val = pos[0]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        expected = (MIN_DISTANCE_BETWEEN_PLANETS / 2) + 0
        val = pos[1]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_move_down(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        p = g.create_player(u)
        p.set_position(
            (MIN_DISTANCE_BETWEEN_PLANETS / 2), (MIN_DISTANCE_BETWEEN_PLANETS / 2)
        )
        p.save()
        p.set_direction(180)
        p.move()
        pos = p.get_position()
        expected = (MIN_DISTANCE_BETWEEN_PLANETS / 2) + 0
        val = pos[0]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        expected = (MIN_DISTANCE_BETWEEN_PLANETS / 2) + -10
        val = pos[1]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_move_right(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        p = g.create_player(u)
        p.set_position(
            (MIN_DISTANCE_BETWEEN_PLANETS / 2), (MIN_DISTANCE_BETWEEN_PLANETS / 2)
        )
        p.save()
        p.set_direction(270)
        p.move()
        pos = p.get_position()
        expected = (MIN_DISTANCE_BETWEEN_PLANETS / 2) + 10
        val = pos[0]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        expected = (MIN_DISTANCE_BETWEEN_PLANETS / 2) + 0
        val = pos[1]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_move_semi_left(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        p = g.create_player(u)
        p.set_position(
            (MIN_DISTANCE_BETWEEN_PLANETS / 2), (MIN_DISTANCE_BETWEEN_PLANETS / 2)
        )
        p.save()
        p.set_direction(30)
        p.move()
        pos = p.get_position()
        expected_left = (MIN_DISTANCE_BETWEEN_PLANETS / 2) - 4
        val = pos[0]
        errmsg = "expected " + str(expected_left) + " but got " + str(val)
        self.assertEqual(val, expected_left, errmsg)
        expected = (MIN_DISTANCE_BETWEEN_PLANETS / 2) + 8
        val = pos[1]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_move_slightly_right(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        p = g.create_player(u)
        p.set_position(
            (MIN_DISTANCE_BETWEEN_PLANETS / 2), (MIN_DISTANCE_BETWEEN_PLANETS / 2)
        )
        p.save()
        p.set_direction(360 - 15)
        p.move()
        pos = p.get_position()
        expected_left = (MIN_DISTANCE_BETWEEN_PLANETS / 2) + 2
        val = pos[0]
        errmsg = "expected " + str(expected_left) + " but got " + str(val)
        self.assertEqual(val, expected_left, errmsg)
        expected = (MIN_DISTANCE_BETWEEN_PLANETS / 2) + 9
        val = pos[1]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_n_closest_planets(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username="testuser")
        player = g.create_player(u)
        mindist = MIN_DISTANCE_BETWEEN_PLANETS / 2
        player.set_position(mindist, mindist)
        player.save()
        # beforeList = list()
        # for p in Planet.objects.filter(game=g):
        #     beforeList.append(p.title)
        # for i in Planet.objects.filter(game=g):
        #     if i.title not in ["planet #0", "planet #1", "planet #2"]:
        #         i.delete()
        # afterList = list()
        # for p in Planet.objects.filter(game=g):
        #     afterList.append(p.title)
        # self.assertEqual(beforeList, afterList)
        iterator = 0
        distance_between = mindist
        for i in Planet.objects.filter(game=g):
            iterator += 1
            i.title = f"p{iterator}"
            i.pos_x = mindist
            i.pos_y = mindist
            i.save()
            distance_between += mindist

        name_list = list()
        planet_list = player.get_closest_planets(5)
        for p in planet_list:
            planet = Planet.objects.get(id=p)
            name_list.append(planet.title)
        name_list.sort()
        expected = ["p1", "p2", "p3"]
        val = name_list
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)


# class RemoteGoogleTestCase(unittest.TestCase):
#     #check if selenium is working
#     def setUp(self):
#         self.browser = webdriver.Remote(
#             command_executor='http://chrome:4444/wd/hub',
#             desired_capabilities=DesiredCapabilities.CHROME)
#         self.addCleanup(self.browser.quit)

#     def testPageTitle(self):
#         self.browser.get('http://www.google.com')
#         self.assertIn('Google', self.browser.title)
