from django.urls import path

from .views import CustomTokenObtainPairView, CustomUserDetailView, CustomUserListView

urlpatterns = [
    path("", CustomUserListView.as_view(), name="customuser-list"),
    path("<int:id>/", CustomUserDetailView.as_view(), name="customuser-update"),
    path(
        "token/", CustomTokenObtainPairView.as_view(), name="custom_token_obtain_pair"
    ),
]
