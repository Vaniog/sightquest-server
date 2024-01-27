from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [path("users/", include("apps.users.urls"))]
