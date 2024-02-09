import datetime
import secrets

from django.utils import timezone

from apps.api.serializers import GameSerializer
from apps.api.models import Game, Coordinate, GameUser, GameQuestTask, QuestTask, PlayerTaskCompletion, GamePhoto
from django.contrib.auth import get_user_model

User = get_user_model()


class GameManager:
    player_coordinates = {}

    def __init__(self, game: Game):
        self.game = game
        self.game_json = GameSerializer(game).data

    def refresh_from_db(self):
        self.game.refresh_from_db()
        self.game_json = GameSerializer(self.game).data

    def set_player_coordinates(self, player_id: int, coordinates: Coordinate):
        self.player_coordinates[player_id] = coordinates

    def process_to_json(self):
        for player in self.game_json["players"]:
            player["coordinates"] = self.player_coordinates.get(player["user"]["id"], None) \
                                    or {"latitude": 0, "longitude": 0}
        return self.game_json

    def add_player(self, user: User):
        if self.game.players.filter(user=user).count() == 0:
            game_user = GameUser(game=self.game, user=user)
            if self.game.players.filter(role="RUNNER").count() == 0:
                game_user.role = "RUNNER"
            game_user.save()
        self.refresh_from_db()

    def task2game_task(self, quest_task: QuestTask) -> GameQuestTask:
        return GameQuestTask.objects.filter(
            settings__game=self.game,
            quest_task=quest_task
        ).first()

    def complete_task(self, game_user: GameUser, game_task: GameQuestTask, game_photo: GamePhoto):
        if game_user is None or game_task is None or game_photo is None:
            raise ValueError("Some data does not exists")
        PlayerTaskCompletion(
            player=game_user,
            game_task=game_task,
            photo=game_photo
        ).save()
        self.refresh_from_db()

    def get_player_by_secret(self, secret: str) -> GameUser:
        game_user = self.game.players.filter(secret=secret).first()
        if game_user is None:
            raise ValueError("Person with this code does not exists")
        return game_user

    def catch_player(self, catcher: GameUser, runner: GameUser):
        if catcher.role != "CATCHER":
            raise ValueError("Person who tries to catch is not a catcher")
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
        self.refresh_from_db()

    def update_settings(
            self,
            duration: datetime.timedelta,
            task_ids: list[int]
    ):
        self.game.settings.duration = duration
        self.game.settings.tasks.clear()
        for task_id in task_ids:
            try:
                game_quest_task = GameQuestTask(
                    settings=self.game.settings,
                    quest_task_id=task_id
                )
            except QuestTask.DoesNotExist:
                raise ValueError("Some task does not exists")
            game_quest_task.save()

        self.game.settings.save()
        self.refresh_from_db()


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
