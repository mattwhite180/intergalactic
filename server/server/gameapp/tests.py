import datetime
import unittest

from django.contrib.auth.models import AnonymousUser, User
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from django.contrib.auth.models import AnonymousUser, User

from .models import (
    MIN_DISTANCE_BETWEEN_PLANETS,
    Game,
    Planet,
    PlanetBlueprint,
    Player,
    Weapon,
    WeaponBlueprint,
    get_rand,
    rand_item_from_list,
    VehicleBlueprint,
    Vehicle,
)

# from .views import data_to_json, run_jobs


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
            title="testgame", game_dimentions=4, description="test!",
            mod=test_user,
        )
        g.save()

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


class PlanetBlueprintTestCase(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(username="testuser", password="1234")
        g = Game.objects.create(
            title="testgame", game_dimentions=MIN_DISTANCE_BETWEEN_PLANETS * 10, description="test!",
            mod=test_user,
        )
        g.save()
        p = PlanetBlueprint.objects.create(game=g, title="testplanetbp")
        p.save()

    def test_sanity(self):
        p = PlanetBlueprint.objects.get(title="testplanetbp")
        expected = "testplanetbp"
        val = p.title
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_generate(self):
        p = PlanetBlueprint.objects.get(title="testplanetbp")
        new_planet = p.generate_planet()
        new_planet.save()
        expected = "testplanetbp"
        val = new_planet.title
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_valid_locations(self):
        p = PlanetBlueprint.objects.get(title="testplanetbp")
        new_planet = p.generate_planet()
        new_planet.pos_x = 3 * MIN_DISTANCE_BETWEEN_PLANETS
        new_planet.pos_y = 9 * MIN_DISTANCE_BETWEEN_PLANETS
        new_planet.save()
        available_list = p.get_valid_locations()
        x_list = available_list[0]
        y_list = available_list[1]
        x_list.sort()
        y_list.sort()
        my_list = [1, 2, 4, 5, 6, 7, 8, 9]
        expected_x = list()
        for i in my_list:
            expected_x.append(i * MIN_DISTANCE_BETWEEN_PLANETS)
        errmsg_x = "x_list should have " + str(expected_x) + " but got " + str(x_list)
        self.assertEqual(x_list, expected_x, errmsg_x)
        my_list = [1, 2, 3, 4, 5, 6, 7, 8]
        expected_y = list()
        for i in my_list:
            expected_y.append(i * MIN_DISTANCE_BETWEEN_PLANETS)
        errmsg_y = "y_list should have " + str(expected_y) + " but got " + str(y_list)
        self.assertEqual(y_list, expected_y, errmsg_y)


class PlanetTestCase(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(username="testuser", password="1234")
        g = Game.objects.create(
            title="testgame", game_dimentions=4, description="test!",
            mod=test_user,
        )
        g.save()
        pb = PlanetBlueprint.objects.create(game=g, title="testplanetbp")
        pb.save()
        p1 = pb.generate_planet()
        p1.title = "testplanet1"
        p1.pos_x = 100
        p1.pos_y = 100
        p1.save()
        p2 = pb.generate_planet()
        p2.title = "testplanet2"
        p2.pos_x = 500
        p2.pos_y = 400
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
        expected = 500
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        val = p2.get_distance(p1)
        expected = 500
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

class PlayerTestCase(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(username="testuser", password="1234")
        g = Game.objects.create(
            title="testgame", game_dimentions=4, description="test!",
            mod=test_user,
        )
        g.configure_game()
        g.save()
        pb = PlanetBlueprint.objects.create(game=g, title="testplanetbp")
        pb.save()
        for p in range(6):
            pl = pb.generate_planet()
            pl.title = 'planet #' + str(p)
            pl.save()

    def test_sanity_check(self):
        p = Planet.objects.get(title="planet #4")
        expected = "planet #4"
        val = p.title
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_create_player(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username='testuser')
        p = g.create_player(u)
        p.save()
        expected = "testuser's bio"
        val = p.bio
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_player_location(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username='testuser')
        for i in Planet.objects.filter(game=g):
            i.delete()
        pb = PlanetBlueprint.objects.create(game=g, title="testplanetbp")
        pb.save()
        planet = pb.generate_planet()
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
        u = User.objects.get(username='testuser')
        for i in Planet.objects.filter(game=g):
            i.delete()
        player = g.create_player(u)
        expected = False
        val = player
        errmsg = "expected 'player' to be false since no planets exist on this game"
        self.assertEqual(val, expected, errmsg)

    def test_set_direction(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username='testuser')
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
        player.set_direction(-360 - 360 -90)
        expected = 270
        val = player.get_direction()
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)

    def test_move_forward(self):
        g = Game.objects.get(title="testgame")
        u = User.objects.get(username='testuser')
        p = g.create_player(u)
        p.set_position(1000, 1000)
        p.save()
        p.set_direction(0)
        p.move()
        pos = p.get_position()
        expected = 1000 + 10
        val = pos[0]
        errmsg = "expected " + str(expected) + " but got " + str(val)
        self.assertEqual(val, expected, errmsg)
        expected = 1000 + 0
        val = pos[1]
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
