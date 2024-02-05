import json

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from .models import (
    Coordinate,
    Game,
    GamePhoto,
    GameSettings,
    GameUser,
    PlayerTaskCompletion,
    QuestPoint,
    QuestTask,
    Route,
)

User = get_user_model()


class GamePhotoSerializer(serializers.ModelSerializer):
    game_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = GamePhoto
        fields = ["id", "game_code", "image", "upload_time"]

    def get_game_code(self, obj):
        if obj.game:
            return obj.game.code
        return None

    def create(self, validated_data):
        game_code = validated_data.pop("game_code", None)

        if game_code:
            try:
                game = Game.objects.get(code=game_code)
            except Game.DoesNotExist:
                raise ValidationError(
                    {
                        "error": f"Game with code {game_code} does not exist",
                        "game_code": f"{game_code}",
                    }
                )
        else:
            raise ValidationError({"error": "Game code is required."})

        image = validated_data.pop("image", None)

        game_photo = GamePhoto(**validated_data)
        game_photo.game = game

        if image:
            game_photo.image = image

        game_photo.save()
        return game_photo


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinate
        fields = ("latitude", "longitude")


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


class PlayerTaskCompletionSerializer(serializers.ModelSerializer):
    task_id = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    def get_task_id(self, obj):
        return obj.game_task.quest_task.id

    def get_photo(self, obj):
        return obj.photo.image.url

    class Meta:
        model = PlayerTaskCompletion
        fields = ["completed_at", "photo", "task_id"]


class GameUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    completed = PlayerTaskCompletionSerializer(many=True, read_only=True)

    class Meta:
        model = GameUser
        fields = ["user", "role", "completed", "secret"]


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
        if "players" in validated_data:
            player_usernames = validated_data.pop("players")
            players = User.objects.filter(username__in=player_usernames)
            instance.players.set(players)
        if "tasks" in validated_data:
            instance.tasks.set(validated_data.get("tasks", instance.tasks.all()))
        if "settings" in validated_data:
            instance.settings = validated_data.get("settings", instance.settings)

        instance.save()
        return instance


class QuestTaskSerializer(serializers.ModelSerializer):
    quest_point = serializers.PrimaryKeyRelatedField(queryset=QuestPoint.objects.all())

    class Meta:
        model = QuestTask
        fields = ("id", "title", "description", "quest_point")

    def create(self, validated_data):
        quest_point = validated_data.pop("quest_point")
        quest_task = QuestTask.objects.create(quest_point=quest_point, **validated_data)
        return quest_task


class QuestPointSerializer(serializers.ModelSerializer):
    location = CoordinatesSerializer()
    tasks = QuestTaskSerializer(many=True, read_only=True)

    class Meta:
        model = QuestPoint
        fields = ("id", "title", "description", "location", "image", "city", "tasks")

    def to_representation(self, instance):
        representation = super(QuestPointSerializer, self).to_representation(instance)
        representation["image"] = instance.image.url if instance.image else None
        return representation

    def create(self, validated_data):
        location_data = validated_data.pop("location")
        location_serializer = CoordinatesSerializer(data=location_data)
        location_serializer.is_valid(raise_exception=True)
        location = location_serializer.save()

        quest_point = QuestPoint.objects.create(location=location, **validated_data)

        return quest_point


class RouteSerializer(serializers.ModelSerializer):
    quest_points = QuestPointSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Route
        fields = ["id", "title", "complexity", "popularity", "quest_points"]
