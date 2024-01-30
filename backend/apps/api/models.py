from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe


def quest_directiory_path(instance, filename):
    return "quest_points/{0}".format(filename)


def lobby_image_file_path(instance, filename):
    return "lobby_photos/{0}/{1}".format(instance.lobby.id, filename)


# Содель координат
class Coordinate(models.Model):
    latitude = models.DecimalField(max_digits=12, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"


# Модель задачи квеста
class QuestTask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


# Модели для расширения (регион и город)
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
class Lobby(models.Model):
    players = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="LobbyMembership",
        related_name="lobbies",
    )
    created_at = models.DateTimeField(auto_now_add=True)


# Промежуточная модель для Lobby и User
class LobbyMembership(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)


# Модель для настроек игры
class GameSettings(models.Model):
    mode = models.CharField(max_length=50)
    duration = models.DurationField(default=timedelta(hours=1))

    def __str__(self):
        return f"{self.mode}, Duration: {self.duration}"


# Класс игры
class Game(models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    settings = models.ForeignKey(GameSettings, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(default=timezone.now)


# Модель фото лобби
class GamePhoto(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to=lobby_image_file_path)
    upload_time = models.DateTimeField(auto_now_add=True)


# Модель для заданий внутри игры
class GameQuestTask(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="game_tasks")
    quest_task = models.ForeignKey(
        QuestTask, on_delete=models.CASCADE, related_name="game_tasks"
    )

    def __str__(self):
        return f"{self.game} - {self.quest_task}"


# Модель для выполнения задачи игроком
class PlayerTaskCompletion(models.Model):
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_completions",
    )
    game_task = models.ForeignKey(
        GameQuestTask, on_delete=models.CASCADE, related_name="task_completions"
    )
    completed_at = models.DateTimeField()

    def __str__(self):
        return f"{self.player} completed {self.game_task} at {self.completed_at}"
