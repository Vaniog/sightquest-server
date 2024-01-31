from django.contrib import admin
from django.urls import include, path, re_path

from .views import (
    GamePhotoCreateView
)

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("game-photos/", GamePhotoCreateView.as_view(), name="game-photo-create"),
]
