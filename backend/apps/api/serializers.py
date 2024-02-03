from rest_framework import serializers

from .models import Game, GamePhoto, GameSettings, QuestTask, QuestPoint, Coordinate, GameUser
from django.contrib.auth import get_user_model

User = get_user_model()


class GamePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamePhoto
        fields = ["game", "image", "upload_time"]


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinate
        fields = ('latitude', 'longitude')


class QuestPointSerializer(serializers.ModelSerializer):
    location = CoordinatesSerializer()

    class Meta:
        model = QuestPoint
        fields = ('description', 'title', 'image', 'location')


class QuestTaskSerializer(serializers.ModelSerializer):
    quest_point = QuestPointSerializer()

    class Meta:
        model = QuestTask
        fields = ('id', 'title', 'description', 'quest_point')


class SettingsSerializer(serializers.ModelSerializer):
    tasks = QuestTaskSerializer(many=True)

    class Meta:
        model = GameSettings
        fields = ["mode", "duration", "tasks"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "avatar"]


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
