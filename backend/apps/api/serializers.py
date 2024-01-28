from rest_framework import serializers

from .models import PlayerLobby


class PlayerLobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerLobby
        fields = ["id", "host", "players", "created_at"]
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        players_data = validated_data.pop("players")
        lobby = PlayerLobby.objects.create(**validated_data)
        lobby.players.set(players_data)
        return lobby
