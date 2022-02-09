import re

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from .models import (Game, Planet, Player, Vehicle, VehicleBlueprint, Weapon,
                     WeaponBlueprint, get_rand, rand_item_from_list)


"""
#####
Helpful functions used by views
"""


def testview(request):
    return HttpResponse("hello world! you are at the Intergalactic testview!")


def debug():
    return settings.DEBUG


def mobile(request):
    # Return True if the request comes from a mobile device.
    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)
    if MOBILE_AGENT_RE.match(request.META["HTTP_USER_AGENT"]):
        return True
    else:
        return False


def get_context(request):
    context = {}
    context["is_mobile"] = mobile(request)
    context["debug"] = debug()
    if request.user.is_authenticated:
        context["players"] = Player.objects.filter(user=request.user)
    # context["games"] = Game.objects.filter()
    return context


"""
#####
non-model views
"""


def index(request):
    context = get_context(request)
    return render(request, "gameapp/bootstrap.html", context)


def sidebar(request):
    context = get_context(request)
    return render(request, "gameapp/sidebar.html", context)
