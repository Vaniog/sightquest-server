from django.contrib import admin
from django.utils.html import mark_safe

from .models import (
    City,
    Coordinate,
    GamePhoto,
    QuestPoint,
    QuestTask,
    Region,
    GameSettings,
    Game,
    Player,
    GameQuestTask, PlayerTaskCompletion, Route
)


# Inline класс для фотографий лобби
class GamePhotoInline(admin.TabularInline):
    model = GamePhoto
    extra = 1


class PlayerInline(admin.TabularInline):
    model = Player
    extra = 1


class GameQuestTaskInline(admin.TabularInline):
    model = GameQuestTask
    extra = 1


# Админ класс для координат
@admin.register(Coordinate)
class CoordinateAdmin(admin.ModelAdmin):
    list_display = ("latitude", "longitude")
    search_fields = ("latitude", "longitude")


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


# Админ класс для фотографий лобби
@admin.register(GamePhoto)
class GamePhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "game", "image", "upload_time"]


# Админ класс для городов и регионов
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "region"]


@admin.register(QuestTask)
class QuestTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'quest_point')  # Поля, которые будут отображаться в списке объектов
    search_fields = ('title', 'description', 'quest_point__title')  # Поля, по которым можно производить поиск
    list_filter = ('quest_point',)  # Фильтры в боковой панели
    ordering = ('title',)  # Сортировка


@admin.register(GameSettings)
class GameSettingsAdmin(admin.ModelAdmin):
    list_display = ('mode', 'duration')  # Поля, которые будут отображаться в списке объектов
    search_fields = ('mode',)  # Поля, по которым можно производить поиск
    ordering = ('mode',)  # Сортировка
    inlines = [GameQuestTaskInline]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        'host', 'created_at', 'started_at', 'ended_at')  # Поля, которые будут отображаться в списке объектов
    search_fields = (
        'host__username', 'created_at', 'started_at', 'ended_at')  # Поля, по которым можно производить поиск
    list_filter = ('host', 'created_at', 'started_at')  # Фильтры в боковой панели
    ordering = ('-created_at',)  # Сортировка (по умолчанию в порядке убывания)
    inlines = [PlayerInline]


@admin.register(PlayerTaskCompletion)
class PlayerTaskCompletionAdmin(admin.ModelAdmin):
    list_display = ('player', 'game_task', 'completed_at')  # Поля, которые будут отображаться в списке объектов
    search_fields = (
        'player__username', 'game_task__game__host__username',
        'completed_at')  # Поля, по которым можно производить поиск
    list_filter = ('player',)  # Фильтры в боковой панели
    ordering = ('-completed_at',)  # Сортировка (по умолчанию в порядке убывания)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('title', 'complexity', 'popularity')
    search_fields = ['title', 'description']
    filter_horizontal = ('quest_points',)
