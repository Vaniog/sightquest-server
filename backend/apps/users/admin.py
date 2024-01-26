from django.contrib import admin

from .models import CustomUser


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "date_joined", "last_login", "is_staff", "is_active")
    search_fields = ("username",)
    list_filter = ("is_staff", "is_active", "date_joined")
    ordering = ("date_joined",)
