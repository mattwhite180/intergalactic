from django.http import HttpResponse
from django.shortcuts import render


def testview(request):
    return HttpResponse("hello world! you are at the Intergalactic testview!")
