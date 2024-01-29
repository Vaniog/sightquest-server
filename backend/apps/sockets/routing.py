from django.urls import re_path

from .consumers import ChatConsumer, LobbyConsumer

websocket_urlpatterns = [
    re_path(r"ws/socket-server/", ChatConsumer.as_asgi()),
    re_path(r"ws/lobby/(?P<lobby_id>\w+)/$", LobbyConsumer.as_asgi()),
]
