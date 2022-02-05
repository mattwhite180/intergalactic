from django.urls import path

from . import views

urlpatterns = [
    path('testview', views.testview, name='testview')
]