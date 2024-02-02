from apps.users.views import CustomTokenObtainPairView
from django.contrib import admin
from django.urls import include, path, re_path

from .views import GameDetailView, GameListCreateView, GamePhotoCreateView

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("game-photos/", GamePhotoCreateView.as_view(), name="game-photo-create"),
    path('games/', GameListCreateView.as_view(), name='game-list-create'),
    path('games/<str:code>/', GameDetailView.as_view(), name='game-detail'),
    path("token/", CustomTokenObtainPairView.as_view(), name="custom-token-obtain-pair"),
]
