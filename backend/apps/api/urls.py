from django.contrib import admin
from django.urls import include, path, re_path

from .views import (
    LobbyPhotoCreateView,
    PlayerLobbyDetailView,
    PlayerLobbyListView,
    QuestCompletedCreateView,
)

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("player-lobbies/", PlayerLobbyListView.as_view(), name="player-lobby-list"),
    path(
        "player-lobbies/<int:pk>/",
        PlayerLobbyDetailView.as_view(),
        name="player-lobby-detail",
    ),
    path("lobby-photos/", LobbyPhotoCreateView.as_view(), name="lobby-photo-create"),
    path(
        "quest-completed/",
        QuestCompletedCreateView.as_view(),
        name="quest-completed-create",
    ),
]
