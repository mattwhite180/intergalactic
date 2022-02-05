from django.shortcuts import render
from django.http import HttpResponse

def testview(request):
    return HttpResponse("hello world! you are at the Intergalactic testview!")