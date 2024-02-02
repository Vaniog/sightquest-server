from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserDetailSerializer,
    UserListSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserDetailView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = "username"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class CustomUserListView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer 

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserListSerializer
        return super().get_serializer_class() 