from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Game, GamePhoto, QuestPoint, Route
from .serializers import (
    GamePhotoSerializer,
    GameSerializer,
    QuestPointSerializer,
    QuestTask,
    QuestTaskSerializer,
    RouteSerializer,
)

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


class GameCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        game = Game(host=request.user)
        game.save()

        return Response(GameSerializer(game).data)


class QuestTaskListCreateView(generics.ListCreateAPIView):
    queryset = QuestTask.objects.all()
    serializer_class = QuestTaskSerializer


class QuestTaskDetailView(generics.RetrieveDestroyAPIView):
    queryset = QuestTask.objects.all()
    serializer_class = QuestTaskSerializer


class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class RouteDetailView(generics.RetrieveDestroyAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class QuestPointListCreateView(generics.ListCreateAPIView):
    queryset = QuestPoint.objects.all()
    serializer_class = QuestPointSerializer


class QuestPointDetailView(generics.RetrieveDestroyAPIView):
    queryset = QuestPoint.objects.all()
    serializer_class = QuestPointSerializer
