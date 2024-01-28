from rest_framework import generics, status
from rest_framework.response import Response

from .models import PlayerLobby
from .serializers import PlayerLobbySerializer


class PlayerLobbyListCreateView(generics.ListCreateAPIView):
    queryset = PlayerLobby.objects.all()
    serializer_class = PlayerLobbySerializer


class PlayerLobbyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlayerLobby.objects.all()
    serializer_class = PlayerLobbySerializer
