import datetime
import json
import secrets

from django.utils import timezone

from apps.api.serializers import GameSerializer
from apps.api.models import Game, Player, GameSettingsQuestPoint, GameSettingsQuestTask, QuestTask, \
    PlayerTaskCompletion, GamePhoto
from django.contrib.auth import get_user_model

from apps.sockets.game.dto import *

User = get_user_model()


class GameManager:
    player_coordinates = {}

    def __init__(self, game: Game):
        self.game = game
        self.game_json = GameSerializer(game).data

    class IllegalStateAction(Exception):
        pass

    @staticmethod
    def lobby_required(func):
        def wrapper(self, *args, **kwargs):
            if self.game.state != "LOBBY":
                raise GameManager.IllegalStateAction()
            func(self, *args, **kwargs)

        return wrapper

    def refresh_from_db(self):
        self.game.refresh_from_db()
        self.game_json = GameSerializer(self.game).data

    def process_to_json(self):
        for player in self.game_json["players"]:
            player["coordinates"] = self.player_coordinates.get(player["user"]["id"], None) \
                                    or {"latitude": "0", "longitude": "0"}
        return self.game_json

    def set_player_coordinates(self, player_id: int, coordinates: CoordinateDTO):
        self.player_coordinates[player_id] = coordinates.model_dump()

    def add_player(self, user: User):
        if self.game.players.filter(user=user).count() == 0:
            player = Player(game=self.game, user=user)
            if self.game.players.filter(role="RUNNER").count() == 0:
                player.role = "RUNNER"
            player.save()
        self.refresh_from_db()

    def complete_task(self, event: TaskCompletedDTO):
        player = self.get_player_by_user_id(event.user.id)
        game_task = GameSettingsQuestTask.objects.filter(
            quest_task_id=event.task_id, settings=self.game.settings
        ).first()
        if game_task is None:
            raise ValueError(f"Task with id {event.task_id} does not exist")
        game_photo = GamePhoto.objects.filter(id=event.photo_id)
        if game_photo is None:
            raise ValueError(f"Photo with id {event.photo_id} does not exist")

        PlayerTaskCompletion(
            player=player,
            game_task=game_task,
            photo=game_photo
        ).save()

        self.refresh_from_db()

    def get_player_by_secret(self, secret: str) -> Player:
        player = self.game.players.filter(secret=secret).first()
        if player is None:
            raise ValueError(f"Person with code {secret} does not exist")
        return player

    def get_player_by_user_id(self, user_id: int) -> Player:
        player = Player.objects.filter(user_id=user_id, game=self.game).first()
        if player is None:
            raise ValueError(f"Person with id {user_id} is not in game, or doesn't exist")
        return player

    def catch_player(self, event: PlayerCaughtDTO):
        catcher = self.get_player_by_user_id(event.user.id)
        runner = self.get_player_by_secret(event.secret)

        if catcher.role != "CATCHER":
            raise ValueError("You aren't a catcher")
        if runner.role != "RUNNER":
            raise ValueError("The person who you tries to catch is not a runner")
        self.make_roles_rotation()
        self.refresh_from_db()

    def make_roles_rotation(self):
        players = [player for player in self.game.players.order_by("order_key")]
        runner_index = None
        runner = None
        for i, player in enumerate(players):
            if player.role == "RUNNER":
                runner_index = i
                runner = player

        next_runner_index = (runner_index + 1) % len(players)

        runner.role = "CATCHER"
        runner.regenerate_secret()
        runner.save()

        players[next_runner_index].role = "RUNNER"
        players[next_runner_index].save()

    def start_game(self):
        self.game.started_at = timezone.now()
        players = [player for player in self.game.players.all()]
        for player in players:
            player.role = "CATCHER"
            player.save()
        runner = secrets.choice(players)
        runner.role = "RUNNER"
        runner.save()

        self.game.state = "PLAYING"
        self.game.save()
        self.refresh_from_db()

    @lobby_required
    def update_settings(
            self,
            settings_dto: SettingsDTO
    ):
        self.game.settings.duration = settings_dto.duration

        GameSettingsQuestPoint.objects.filter(settings=self.game.settings).delete()

        for quest_point in settings_dto.quest_points:
            for task in quest_point.tasks:
                self.add_quest_task(task)

        self.game.settings.save()
        self.refresh_from_db()

    def add_quest_task(self, task_dto: QuestTaskDTO):
        quest_task: QuestTask = QuestTask.objects.filter(id=task_dto.id).first()
        if quest_task is None:
            raise ValueError(f"Task with id {task_dto.id} does not exists")

        quest_point = quest_task.quest_point

        game_quest_point = GameSettingsQuestPoint.objects.filter(
            settings=self.game.settings,
            quest_point=quest_point
        ).first()

        if game_quest_point is None:
            game_quest_point = GameSettingsQuestPoint(
                settings=self.game.settings,
                quest_point=quest_point
            )
            game_quest_point.save()

        game_quest_task = GameSettingsQuestTask(
            settings=self.game.settings,
            game_quest_point=game_quest_point,
            quest_task=quest_task
        )
        game_quest_task.save()


class GameManagerHolder:
    game_managers = {}

    @staticmethod
    def get_game_manager(code: str) -> GameManager:
        game_manager: GameManager = GameManagerHolder.game_managers.get(code, None)
        if game_manager is None:
            game = Game.objects.filter(code=code).first()
            game_manager = GameManager(game)
            GameManagerHolder.game_managers[code] = game_manager
        return game_manager

    @staticmethod
    def pop_game_manager(code: str):
        GameManagerHolder.game_managers.pop(code)
