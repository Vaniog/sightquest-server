from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.html import mark_safe
from shortuuid.django_fields import ShortUUIDField
import secrets
import string

from backend.yandex_s3_storage import ClientDocsStorage


def quest_directiory_path(instance, filename):
    return "quest_points/{0}".format(filename)


def game_image_file_path(instance, filename):
    return "game_photos/{0}/{1}".format(instance.game.code, filename)


# Содель координат
class Coordinate(models.Model):
    latitude = models.DecimalField(max_digits=12, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"


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


class QuestPoint(models.Model):
    title = models.CharField(
        max_length=255, blank=False, null=False, default="No title"
    )
    description = models.TextField(blank=False, null=False, default="No description")
    location = models.ForeignKey(Coordinate, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(
        upload_to="quest_point_images/", null=True, storage=ClientDocsStorage()
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, related_name="quest_points", null=True
    )

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.image.url)

    def __str__(self):
        return self.title


# Модель задачи квеста
class QuestTask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    quest_point = models.ForeignKey(
        QuestPoint, on_delete=models.SET_NULL, related_name="tasks", null=True
    )

    def __str__(self):
        if self.quest_point:
            return f"{self.quest_point.title}: {self.title}"
        else:
            return f"No Quest Point: {self.title}"


# Модель для настроек игры
class GameSettings(models.Model):
    MODE_CHOICES = [
        ('BASE', 'Base'),
    ]
    mode = models.CharField(choices=MODE_CHOICES, max_length=50, default="BASE")
    duration = models.DurationField(default=timedelta(hours=1))
    tasks = models.ManyToManyField(QuestTask, through="GameQuestTask")

    def __str__(self):
        return f"{self.mode}, Duration: {self.duration}"


# Класс игры
class Game(models.Model):
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_games",
        on_delete=models.SET_NULL,
        null=True,
    )
    settings = models.ForeignKey(
        GameSettings, related_name="game", on_delete=models.PROTECT
    )
    code = ShortUUIDField(
        unique=True, length=8, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True)

    STATE_CHOICES = [
        ("LOBBY", "Lobby"),
        ("PLAYING", "Playing"),
        ("ENDED", "Ended"),
    ]
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default="LOBBY")

    def __str__(self):
        return f"Game #{self.code}"


@receiver(pre_save, sender=Game)
def create_game_settings(sender, instance, **kwargs):
    print("saved!")
    if not hasattr(instance, 'settings'):
        game_settings = GameSettings.objects.create()
        instance.settings = game_settings


pre_save.connect(create_game_settings, sender=Game)


def generate_secret(length=6):
    secret_length = length
    characters = string.ascii_letters + string.digits
    new_secret = ''.join(secrets.choice(characters).upper() for _ in range(secret_length))
    return new_secret


class GameUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="players")
    ROLE_CHOICES = [
        ('RUNNER', 'Runner'),
        ('CATCHER', 'Catcher')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CATCHER')

    def regenerate_secret(self):
        self.secret = generate_secret()
        self.save()

    secret = models.CharField(max_length=10, default=generate_secret)
    order_key = models.CharField(max_length=10, default=generate_secret)

    def __str__(self):
        return f"User {str(self.user)} in Game #{str(self.game)}"


# Модель фото лобби
class GamePhoto(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(
        upload_to=game_image_file_path, storage=ClientDocsStorage()
    )
    upload_time = models.DateTimeField(auto_now_add=True)


# Модель для заданий внутри игры
class GameQuestTask(models.Model):
    settings = models.ForeignKey(GameSettings, on_delete=models.CASCADE)
    quest_task = models.ForeignKey(
        QuestTask, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{str(self.settings.game)} - {self.quest_task}"


# Модель для выполнения задачи игроком
class PlayerTaskCompletion(models.Model):
    player = models.ForeignKey(
        GameUser,
        on_delete=models.CASCADE,
        related_name="completed",
    )
    game_task = models.ForeignKey(
        GameQuestTask, on_delete=models.CASCADE, related_name="task_completions"
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    photo = models.ForeignKey(GamePhoto, on_delete=models.CASCADE, related_name="task_completion")

    def __str__(self):
        return f"{self.player} completed {self.game_task} at {self.completed_at}"


class Route(models.Model):
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=False, null=False, default="No description")
    complexity = models.IntegerField(default=0)
    popularity = models.IntegerField(default=0)
    quest_points = models.ManyToManyField(QuestPoint, related_name="routes")
