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
    Player,
    PlayerTaskCompletion,
    QuestPoint,
    QuestTask,
    Route,
    GameSettingsQuestPoint,
    GameSettingsQuestTask
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "avatar"]


class PlayerTaskCompletionSerializer(serializers.ModelSerializer):
    task_id = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    def get_task_id(self, obj):
        return obj.game_task.id

    def get_photo(self, obj):
        return obj.photo.image.url

    class Meta:
        model = PlayerTaskCompletion
        fields = ["completed_at", "photo", "task_id"]


class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    completed = PlayerTaskCompletionSerializer(many=True, read_only=True)

    class Meta:
        model = Player
        fields = ["user", "role", "completed", "secret"]


class QuestTaskSerializer(serializers.ModelSerializer):
    quest_point = serializers.PrimaryKeyRelatedField(queryset=QuestPoint.objects.all(), write_only=True)

    class Meta:
        model = QuestTask
        fields = ("id", "title", "description", "quest_point")
        extra_kwargs = {
            'quest_point': {'write_only': True},
        }

    def create(self, validated_data):
        quest_point = validated_data.pop("quest_point")
        quest_task = QuestTask.objects.create(quest_point=quest_point, **validated_data)
        return quest_task


class GameSettingsQuestTaskSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='quest_task.title', read_only=True)
    description = serializers.CharField(source='quest_task.description', read_only=True)
    quest_point = serializers.PrimaryKeyRelatedField(source='quest_task.quest_point', read_only=True)
    id = serializers.IntegerField(source="quest_task.id", read_only=True)

    class Meta:
        model = GameSettingsQuestTask
        fields = ("id", "title", "description", "quest_point")


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


class GameSettingsQuestPointSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='quest_point.title', read_only=True)
    description = serializers.CharField(source='quest_point.description', read_only=True)
    location = CoordinatesSerializer(source='quest_point.location', read_only=True)
    city = serializers.CharField(source='quest_point.city', read_only=True)
    tasks = GameSettingsQuestTaskSerializer(many=True, read_only=True)
    image = serializers.ImageField(source="quest_point.image", read_only=True)
    id = serializers.IntegerField(source="quest_point.id", read_only=True)

    class Meta:
        model = GameSettingsQuestPoint
        fields = ("id", "title", "description", "location", "image", "city", "tasks")


class GameSettingsSerializer(serializers.ModelSerializer):
    quest_points = GameSettingsQuestPointSerializer(source="game_quest_points", many=True)

    class Meta:
        model = GameSettings
        fields = ["mode", "duration", "quest_points"]


class GameSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)
    settings = GameSettingsSerializer()
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


class RouteSerializer(serializers.ModelSerializer):
    quest_points = QuestPointSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Route
        fields = ["id", "title", "complexity", "popularity", "quest_points"]
