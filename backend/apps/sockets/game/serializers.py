from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.api.models import QuestTask, QuestPoint, GameSettings

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    avatar = serializers.CharField


class CoordinatesSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField
    longitude = serializers.FloatField


class UserStateSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    # coordinates = CoordinatesSerializer()
    role = serializers.CharField()
    completed: serializers.ListField(
        child=serializers.IntegerField()
    )


class QuestPointSerializer(serializers.ModelSerializer):
    location = CoordinatesSerializer()

    class Meta:
        model = QuestPoint
        fields = ('description', 'title', 'photo', 'location')


class QuestTaskSerializer(serializers.ModelSerializer):
    quest_point = QuestPointSerializer()

    class Meta:
        model = QuestTask
        fields = ('id', 'title', 'description', 'quest_point')


class SettingsSerializer:
    tasks = serializers.ListField(
        child=QuestTaskSerializer()
    )

    class Meta:
        model = GameSettings
        fields = ('mode', 'duration', 'tasks')


class GameStateSerializer(serializers.ModelSerializer):
    players = serializers.ListField(
        child=UserStateSerializer()
    )
    settings = SettingsSerializer()
    state = serializers.CharField()
