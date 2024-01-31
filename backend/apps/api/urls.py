from django.contrib import admin
from django.urls import include, path, re_path

from .views import (
    GamePhotoCreateView,
    GameListCreateView,
    GameDetailView,
)

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("game-photos/", GamePhotoCreateView.as_view(), name="game-photo-create"),
    path('games/', GameListCreateView.as_view(), name='game-list-create'),
    path('games/<int:pk>/', GameDetailView.as_view(), name='game-detail'),
]
