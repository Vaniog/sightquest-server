import json

from rest_framework import serializers

from .models import Game, GamePhoto, GameSettings, QuestTask, QuestPoint, Coordinate, GameUser, Route
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from django.shortcuts import get_object_or_404

User = get_user_model()


class GamePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamePhoto
        fields = ["game", "image", "upload_time"]


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinate
        fields = ('latitude', 'longitude')


class SettingsSerializer(serializers.ModelSerializer):
    # tasks = QuestTaskSerializer(many=True)
    quest_points = serializers.SerializerMethodField()

    def get_quest_points(self, obj):
        quest_points = set([task.quest_point for task in obj.tasks.all()])
        return QuestPointSerializer(quest_points, many=True).data

    class Meta:
        model = GameSettings
        fields = ["mode", "duration", "quest_points"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "avatar"]


class GameUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    completed = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = GameUser
        fields = ["user", "role", "completed"]


class GameSerializer(serializers.ModelSerializer):
    players = GameUserSerializer(many=True)
    settings = SettingsSerializer()
    host_username = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            "code",
            "host_username",
            "players",
            "settings",
            "created_at",
            "started_at",
            "ended_at",
            "state",
        ]

    def get_host_username(self, obj):
        if obj.host:
            return obj.host.username
        return None

    def update(self, instance, validated_data):
        if 'players' in validated_data:
            player_usernames = validated_data.pop('players')
            players = User.objects.filter(username__in=player_usernames)
            instance.players.set(players)
        if 'tasks' in validated_data:
            instance.tasks.set(validated_data.get('tasks', instance.tasks.all()))
        if 'settings' in validated_data:
            instance.settings = validated_data.get('settings', instance.settings)

        instance.save()
        return instance


class QuestTaskSerializer(serializers.ModelSerializer):
    quest_point = serializers.PrimaryKeyRelatedField(queryset=QuestPoint.objects.all())

    class Meta:
        model = QuestTask
        fields = ('id', 'title', 'description', 'quest_point')

    def create(self, validated_data):
        quest_point = validated_data.pop('quest_point')
        quest_task = QuestTask.objects.create(quest_point=quest_point, **validated_data)
        return quest_task


class QuestPointSerializer(serializers.ModelSerializer):
    location = CoordinatesSerializer()
    tasks = QuestTaskSerializer(many=True, read_only=True)

    class Meta:
        model = QuestPoint
        fields = ('id', 'title', 'description', 'location', 'image', 'city', 'tasks')

    def to_representation(self, instance):
        representation = super(QuestPointSerializer, self).to_representation(instance)
        representation['image'] = instance.image.url if instance.image else None
        return representation

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        location_serializer = CoordinatesSerializer(data=location_data)
        location_serializer.is_valid(raise_exception=True)
        location = location_serializer.save()

        quest_point = QuestPoint.objects.create(location=location, **validated_data)

        return quest_point


class RouteSerializer(serializers.ModelSerializer):
    quest_points = QuestPointSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'title', 'complexity', 'popularity', 'quest_points']
