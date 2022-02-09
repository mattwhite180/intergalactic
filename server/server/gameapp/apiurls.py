from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from . import apiviews

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"games", apiviews.GameViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [path("", include(router.urls))]
