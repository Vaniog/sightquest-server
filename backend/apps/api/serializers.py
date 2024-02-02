from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Game, GamePhoto, GameSettings, QuestTask

User = get_user_model()


class GamePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamePhoto
        fields = ["game", "image", "upload_time"]


class GameSerializer(serializers.ModelSerializer):
    players = serializers.SlugRelatedField(
        slug_field='username',
        many=True,
        queryset=User.objects.all()
    )
    tasks = serializers.PrimaryKeyRelatedField(
        many=True, queryset=QuestTask.objects.all()
    )
    settings = serializers.PrimaryKeyRelatedField(
        queryset=GameSettings.objects.all()
    )
    host_username = serializers.SerializerMethodField()


    class Meta:
        model = Game
        fields = [
            "code",
            "host_username",
            "players",
            "tasks",
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