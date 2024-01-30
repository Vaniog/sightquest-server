from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import GamePhoto, PlayerLobby, QuestCompleted, QuestPoint, QuestTask

User = get_user_model()


class PlayerLobbySerializer(serializers.ModelSerializer):
    players = serializers.SlugRelatedField(
        many=True, slug_field="id", queryset=User.objects.all()
    )
    questpoints = serializers.PrimaryKeyRelatedField(
        many=True, queryset=QuestPoint.objects.all()
    )
    host_id = serializers.SerializerMethodField()

    class Meta:
        model = PlayerLobby
        fields = [
            "id",
            "host_id",
            "players",
            "questpoints",
            "created_at",
            "started_at",
            "duration",
        ]

    def get_host_id(self, obj):
        if obj.host:
            return obj.host.id
        return None

    def update(self, instance, validated_data):
        instance.players.set(validated_data.get("players", instance.players.all()))
        instance.questpoints.set(
            validated_data.get("questpoints", instance.questpoints.all())
        )
        instance.save()
        return instance


class GamePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamePhoto
        fields = ["lobby", "image", "upload_time"]


class QuestCompletedSerializer(serializers.ModelSerializer):
    lobby = serializers.PrimaryKeyRelatedField(queryset=PlayerLobby.objects.all())
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )
    task = serializers.PrimaryKeyRelatedField(queryset=QuestTask.objects.all())

    class Meta:
        model = QuestCompleted
        fields = ["lobby", "user", "task"]
