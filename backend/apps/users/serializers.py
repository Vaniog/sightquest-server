from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        return token

    def validate(self, attrs):
        username = attrs.get("username")

        if not username:
            raise ValidationError("Username is required")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("No active user found with the given username")

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "avatar"]
        read_only_fields = ("id",)

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance
