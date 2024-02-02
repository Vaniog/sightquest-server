from django.contrib.auth import authenticate, get_user_model
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
        password = attrs.get("password")

        if not username:
            raise ValidationError("Username is required")
        if not password:
            raise ValidationError("Password is required")

        user = authenticate(username=username, password=password)
        if user is None:
            raise AuthenticationFailed('No active user found with the given credentials')

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "password", "avatar"] 
        read_only_fields = ("id",)
        extra_kwargs = {
            "password": {"write_only": True, "required": True},  
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = CustomUser(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance
    
class UserDetailSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ["id", "username", "avatar", "current_password"]
        read_only_fields = ("id",)
        extra_kwargs = {
            "current_password": {"write_only": True, "required": False},
        }

    def update(self, instance, validated_data):
        current_password = validated_data.pop('current_password', None)

        if 'username' in validated_data:
            if not current_password:
                raise serializers.ValidationError({'current_password': ['Current password is required to change the username.']})
            if not instance.check_password(current_password):
                raise serializers.ValidationError({'current_password': ['Current password is incorrect.']})
            instance.username = validated_data.get('username')

        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
