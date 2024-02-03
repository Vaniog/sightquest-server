from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Game, GamePhoto
from .serializers import GamePhotoSerializer, GameSerializer

User = get_user_model()


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


class GameListCreateView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    lookup_field = "code"

