from django.urls import path

from .views import CustomUserDetailView, CustomUserListView

urlpatterns = [
    path("", CustomUserListView.as_view(), name="customuser-list"),
    path("<str:username>/", CustomUserDetailView.as_view(), name="customuser-detail"),
]
