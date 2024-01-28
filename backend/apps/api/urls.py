from django.contrib import admin
from django.urls import include, path, re_path

from .views import PlayerLobbyDetailView, PlayerLobbyListCreateView

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path(
        "player-lobbies/", PlayerLobbyListCreateView.as_view(), name="player-lobby-list"
    ),
    path(
        "player-lobbies/<int:pk>/",
        PlayerLobbyDetailView.as_view(),
        name="player-lobby-detail",
    ),
]
