from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import LobbyPhoto, PlayerLobby, QuestCompleted
from .serializers import (
    LobbyPhotoSerializer,
    PlayerLobbySerializer,
    QuestCompletedSerializer,
)


class PlayerLobbyListView(generics.ListCreateAPIView):
    queryset = PlayerLobby.objects.all()
    serializer_class = PlayerLobbySerializer


class PlayerLobbyDetailView(generics.RetrieveUpdateAPIView):
    queryset = PlayerLobby.objects.all()
    serializer_class = PlayerLobbySerializer


class LobbyPhotoCreateView(generics.CreateAPIView):
    queryset = LobbyPhoto.objects.all()
    serializer_class = LobbyPhotoSerializer
    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request, *args, **kwargs):
        file_serializer = self.serializer_class(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestCompletedCreateView(generics.CreateAPIView):
    queryset = QuestCompleted.objects.all()
    serializer_class = QuestCompletedSerializer
