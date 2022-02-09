import json
import os

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from gameapp.models import Game
from gameapp.serializers import GameSerializer
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
def api_root(request, format=None):
    return Response({"games": reverse("game-list", request=request, format=format)})


class GameViewSet(viewsets.ModelViewSet):
    """
    This is the RESTful API for Chessdynamics
    """

    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @action(detail=True)
    def play_leela(self, request, *args, **kwargs):
        game = self.get_object()
        if game.available:
            gh = GameHandler(game)
            l = Leela(game.time_controls)
            move = l.getMove(gh.get_board())
            # move = gh.play_turn()
            gh.play_move(move)
            return Response(
                {
                    "message": "game " + str(game.id) + " moved",
                    "move": move,
                    "gameover": str(gh.is_game_over()),
                }
            )
        else:
            return Response({"message": "game is already in use"})

    @action(detail=True, url_path="play_stockfish/(?P<level_str>[^/.]+)")
    def play_stockfish(self, request, level_str, pk=None):
        game = self.get_object()
        if game.available:
            gh = GameHandler(game)
            s = Stockfish(int(level_str), game.time_controls)
            move = s.getMove(gh.get_board())
            # move = gh.play_turn()
            gh.play_move(move)
            return Response(
                {
                    "message": "game " + str(game.id) + " moved",
                    "move": move,
                    "gameover": str(gh.is_game_over()),
                }
            )
        else:
            return Response({"message": "game is already in use"})

    @action(detail=True)
    def play_random(self, request, *args, **kwargs):
        game = self.get_object()
        if game.available:
            gh = GameHandler(game)
            r = RandomEngine()
            move = r.getMove(gh.get_board())
            # move = gh.play_turn()
            gh.play_move(move)
            return Response(
                {
                    "message": "game " + str(game.id) + " moved",
                    "move": move,
                    "gameover": str(gh.is_game_over()),
                }
            )
        else:
            return Response({"message": "game is already in use"})
