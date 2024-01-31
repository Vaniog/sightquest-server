from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import GamePhoto, QuestPoint, QuestTask

User = get_user_model()


class GamePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamePhoto
        fields = ["game", "image", "upload_time"]
