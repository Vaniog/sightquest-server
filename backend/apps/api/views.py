from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import GamePhoto, PlayerLobby, QuestCompleted
from .serializers import (
    GamePhotoSerializer,
    PlayerLobbySerializer,
    QuestCompletedSerializer,
)

User = get_user_model()


class PlayerLobbyListView(generics.ListCreateAPIView):
    queryset = PlayerLobby.objects.all()
    serializer_class = PlayerLobbySerializer

    def post(self, request, *args, **kwargs):
        # user = request.user
        user = User.objects.get(id=1)
        if user.hosted_lobby:
            return Response(
                {
                    "message": "User is already hosting a lobby",
                    "lobby_id": user.hosted_lobby.id,
                },
                status=status.HTTP_200_OK,
            )
        else:
            lobby = PlayerLobby.objects.create()
            user.hosted_lobby = lobby
            user.save()
            lobby.players.add(user)  # Добавляем пользователя в список игроков
            lobby.save()
            return Response(
                {"message": "New lobby created", "lobby_id": lobby.id},
                status=status.HTTP_201_CREATED,
            )


class PlayerLobbyDetailView(generics.RetrieveUpdateAPIView):
    queryset = PlayerLobby.objects.all()
    serializer_class = PlayerLobbySerializer


class GamePhotoCreateView(generics.CreateAPIView):
    queryset = GamePhoto.objects.all()
    serializer_class = GamePhotoSerializer
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
