from django.contrib import admin
from django.utils.html import mark_safe

from .models import Coordinate, PlayerLobby, QuestPoint


# Register your models here.
@admin.register(Coordinate)
class CoordinateAdmin(admin.ModelAdmin):
    list_display = ("latitude", "longitude")
    search_fields = ("latitude", "longitude")


@admin.register(QuestPoint)
class QuestPointAdmin(admin.ModelAdmin):
    list_display = ("title", "description_short", "location", "product_image")
    search_fields = ("title", "description")
    list_filter = ("location",)
    raw_id_fields = ("location",)

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


@admin.register(PlayerLobby)
class PlayerLobbyAdmin(admin.ModelAdmin):
    list_display = ["id", "host", "created_at"]
    list_filter = ["host"]
    search_fields = ["host__username"]
