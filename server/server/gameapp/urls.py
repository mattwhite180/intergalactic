from django.urls import path

from . import views

urlpatterns = [
    path("testview", views.testview, name="testview"),
    path("index", views.index, name="index"),
    path("sidebar", views.sidebar, name="sidebar"),
]
