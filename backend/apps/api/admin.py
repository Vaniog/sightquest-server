from django.contrib import admin
from django.utils.html import mark_safe

from .models import (
    City,
    Coordinate,
    LobbyPhoto,
    PlayerLobby,
    PlayerLobbyMembership,
    QuestCompleted,
    QuestPoint,
    QuestTask,
    Region,
)


# Inline класс для Membership модели
class PlayerLobbyMembershipInline(admin.TabularInline):
    model = PlayerLobbyMembership
    extra = 1


# Inline класс для фотографий лобби
class LobbyPhotoInline(admin.TabularInline):
    model = LobbyPhoto
    extra = 1


# Inline класс для завершенных квестов
class QuestCompletedInline(admin.TabularInline):
    model = QuestCompleted
    extra = 1


# Админ класс для координат
@admin.register(Coordinate)
class CoordinateAdmin(admin.ModelAdmin):
    list_display = ("latitude", "longitude")
    search_fields = ("latitude", "longitude")


# Админ класс для задач квеста
@admin.register(QuestTask)
class QuestTaskAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "description"]


# Админ класс для точек квеста
@admin.register(QuestPoint)
class QuestPointAdmin(admin.ModelAdmin):
    list_display = ("title", "description_short", "location", "product_image")
    search_fields = ("title", "description")
    list_filter = ("location",)

    def description_short(self, obj):
        return (
            obj.description[:50] + "..."
            if len(obj.description) > 50
            else obj.description
        )

    def product_image(self, obj):
        if obj.image:
            return mark_safe('<img src="%s" width="50" height="50" />' % obj.image.url)
        return "No Image"


# Админ класс для лобби игрока
@admin.register(PlayerLobby)
class PlayerLobbyAdmin(admin.ModelAdmin):
    list_display = ["id", "host_info", "created_at", "started_at", "duration"]
    inlines = [PlayerLobbyMembershipInline, LobbyPhotoInline, QuestCompletedInline]

    def host_info(self, obj):
        return f"{obj.host.username}"

    host_info.short_description = "Host"


# Админ класс для фотографий лобби
@admin.register(LobbyPhoto)
class LobbyPhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "lobby", "image", "upload_time"]


# Админ класс для завершенных квестов
@admin.register(QuestCompleted)
class QuestCompletedAdmin(admin.ModelAdmin):
    list_display = ["id", "lobby", "user", "task"]


# Админ класс для городов и регионов
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "region"]
