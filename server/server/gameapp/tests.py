import datetime
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from django.contrib.auth.models import AnonymousUser, User
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase

from .models import get_rand, rand_item_from_list, Game, Player, Weapon, WeaponBlueprint, Planet, PlanetBlueprint, MIN_DISTANCE_BETWEEN_PLANETS
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
                + " and " + str(max_val)
            )
            self.assertEqual(val, expected, errmsg)

class GetRandItemFromListTestCase(TestCase):
    def setUp(self):
        pass

    def test_task_limit(self):
        for i in range(10):
            l = ['a', 123, [1, 2, 3], 'asdf', 2.3]
            rand_val = rand_item_from_list(l)
            val = rand_val in l
            expected = True
            errmsg = (
                "value "
                + str(rand_val)
                + " not in list: "
                + str(l)
            )
            self.assertEqual(val, expected, errmsg)

class GameTestCase(TestCase):
    def setUp(self):
        g = Game.objects.create(
            title='testgame',
            game_dimentions=4,
            description='test!'
        )
        g.save()

    def test_sanity(self):
        g = Game.objects.get(title='testgame')
        expected = 4
        val = g.game_dimentions
        errmsg = (
            "expected " + str(expected) +
            " but got " + str(val)
        )
        self.assertEqual(val, expected, errmsg)
    
    def test_configure(self):
        g = Game.objects.get(title='testgame')
        g.configure_game()
        expected = MIN_DISTANCE_BETWEEN_PLANETS * 10
        val = g.game_dimentions
        errmsg = (
            "expected " + str(expected) +
            " but got " + str(val)
        )
        self.assertEqual(val, expected, errmsg)


class PlanetBlueprintTestCase(TestCase):
    def setUp(self):
        g = Game.objects.create(
            title='testgame',
            game_dimentions=1000,
            description='test!'
        )
        g.save()
        p = PlanetBlueprint.objects.create(
            game = g,
            title='testplanetbp'
        )
        p.save()

    def test_sanity(self):
        p = PlanetBlueprint.objects.get(title='testplanetbp')
        expected = "testplanetbp"
        val = p.title
        errmsg = (
            "expected " + str(expected) +
            " but got " + str(val)
        )
        self.assertEqual(val, expected, errmsg)

    def test_generate(self):
        p = PlanetBlueprint.objects.get(title='testplanetbp')
        new_planet = p.generate()
        new_planet.save()
        expected = 'testplanetbp'
        val = new_planet.title
        errmsg = (
            "expected " + str(expected) +
            " but got " + str(val)
        )
        self.assertEqual(val, expected, errmsg)

    def test_valid_locations(self):
        p = PlanetBlueprint.objects.get(title='testplanetbp')
        new_planet = p.generate()
        new_planet.pos_x = 300
        new_planet.pos_y = 900
        new_planet.save()
        available_list = p.get_valid_locations()
        x_list = available_list[0]
        y_list = available_list[1]
        x_list.sort()
        y_list.sort()
        expected_x = [100,
                    200,
                    400,
                    500,
                    600,
                    700,
                    800,
                    900,
                ]
        errmsg_x = (
            "expected " + str(expected_x) +
            " but got " + str(x_list)
        )
        self.assertEqual(x_list, expected_x, errmsg_x)        
        expected_y = [100,
                    200,
                    300,
                    400,
                    500,
                    600,
                    700,
                    800,
                ]
        errmsg_y = (
            "expected " + str(expected_y) +
            " but got " + str(y_list)
        )
        self.assertEqual(y_list, expected_y, errmsg_y)        




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
