from apps.users.views import CustomTokenObtainPairView
from django.contrib import admin
from django.urls import include, path, re_path

from .views import RouteListCreateView, RouteDetailView, GamePhotoCreateView, GameCreateView, QuestPointDetailView, \
    QuestTaskListCreateView, QuestTaskDetailView, QuestPointListCreateView

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("game-photos/", GamePhotoCreateView.as_view(), name="game-photo-create"),
    # path('games/', GameListCreateView.as_view(), name='game-list-create'),
    # path('games/<str:code>/', GameDetailView.as_view(), name='game-detail'),
    path("token/", CustomTokenObtainPairView.as_view(), name="custom-token-obtain-pair"),
    path("games/create/", GameCreateView.as_view(), name="create-game"),
    path('quest-tasks/', QuestTaskListCreateView.as_view(), name='quest-tasks-list-create'),
    path('quest-tasks/<int:pk>/', QuestTaskDetailView.as_view(), name='quest-tasks-create'),
    path('routes/', RouteListCreateView.as_view(), name='route-list-create'),
    path('routes/<int:pk>/', RouteDetailView.as_view(), name='route-detail'),
    path('quest-points/', QuestPointListCreateView.as_view(), name='quest-point-list-create'),
    path('quest-points/<int:pk>/', QuestPointDetailView.as_view(), name='quest-point-detail'),
]
