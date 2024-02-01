from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Game, GamePhoto, GameSettings, QuestTask

User = get_user_model()


class GamePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamePhoto
        fields = ["game", "image", "upload_time"]


class GameSerializer(serializers.ModelSerializer):
    players = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all()
    )
    tasks = serializers.PrimaryKeyRelatedField(
        many=True, queryset=QuestTask.objects.all()
    )
    settings = serializers.PrimaryKeyRelatedField(
        queryset=GameSettings.objects.all()
    )
    host_id = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            "id",
            "code",
            "host_id",
            "players",
            "tasks",
            "settings",
            "created_at",
            "started_at",
            "ended_at",
            "state",
        ]

    def get_host_id(self, obj):
        if obj.host:
            return obj.host.id
        return None

    def update(self, instance, validated_data):
        instance.players.set(validated_data.get("players", instance.players.all()))
        instance.tasks.set(validated_data.get("tasks", instance.tasks.all()))
        instance.settings = validated_data.get("settings", instance.settings)
        instance.save()
        return instance
