from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe


def quest_directiory_path(instance, filename):
    return "quest_points/{0}".format(filename)


def lobby_image_file_path(instance, filename):
    return "lobby_photos/{0}/{1}".format(instance.lobby.id, filename)


class Coordinate(models.Model):
    latitude = models.DecimalField(max_digits=12, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"


# Модель задачи квеста
class QuestTask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()


# Модели для расширения
class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return self.name


# Модель точки квеста
class QuestPoint(models.Model):
    title = models.CharField(
        max_length=255, blank=False, null=False, default="No title"
    )
    description = models.TextField(blank=False, null=False, default="No description")
    location = models.ForeignKey(
        Coordinate, on_delete=models.SET_NULL, related_name="quest_points", null=True
    )
    image = models.ImageField(upload_to="quest_point_images/", null=True)
    tasks = models.ForeignKey(
        QuestTask, on_delete=models.SET_NULL, related_name="quest_points", null=True
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, related_name="quest_points", null=True
    )

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title


# Модель лобби игрока
class PlayerLobby(models.Model):
    players = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="PlayerLobbyMembership",
        related_name="lobbies",
    )
    questpoints = models.ManyToManyField(QuestPoint, related_name="lobbies")
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(default=timedelta(hours=1))


# Промежуточная модель для PlayerLobby и User
class PlayerLobbyMembership(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lobby = models.ForeignKey(PlayerLobby, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)


# Модель фото лобби
class LobbyPhoto(models.Model):
    lobby = models.ForeignKey(
        PlayerLobby, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField(upload_to=lobby_image_file_path)
    upload_time = models.DateTimeField(auto_now_add=True)


# Модель завершенного квеста
class QuestCompleted(models.Model):
    lobby = models.ForeignKey(
        PlayerLobby, on_delete=models.CASCADE, related_name="completed_quests"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="completed_quests",
    )
    task = models.ForeignKey(
        QuestTask, on_delete=models.CASCADE, related_name="completed_by"
    )
