import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

import json

from apps.api.models import Game, GameUser, GameQuestTask
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from .game.gamestatemanager import GameStateManager, GameState
from apps.api.models import PlayerTaskCompletion

User = get_user_model()


class GameConsumer(WebsocketConsumer):
    game_code: str
    game_group_name: str
    game_state: GameState
    user: User = None
    game_user: GameUser = None

    @staticmethod
    def login_required(func):
        def wrapper(self, *args, **kwargs):
            if self.user is None:
                self.send(text_data=json.dumps({"status": "You didnt complete authorization"}))
                self.close()
                return
            func(self, *args, **kwargs)

        return wrapper

    def connect(self):
        self.game_code = str(self.scope["url_route"]["kwargs"]["game_id"])
        self.game_state = GameStateManager.get_game_state(self.game_code)

        self.game_group_name = "game_%s" % self.game_code

        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )
        self.accept()

        self.send(text_data=json.dumps({"status": "connection succeed"}))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event_type = text_data_json["event"]
        if event_type == "authorization":
            self.on_receive_authorization(text_data_json)
        elif event_type == "get_game_state":
            self.on_receive_send_game_state(text_data_json)
        elif event_type == "location_update":
            self.on_receive_location_update(text_data_json)
        elif event_type == "task_completed":
            self.on_receive_task_completed(text_data_json)
        elif event_type == "player_caught":
            self.on_receive_player_caught(text_data_json)
        else:
            self.group_resend(text_data)

    def send_game_state(self):
        self.send(text_data=json.dumps(
            {
                "event": "gamestate_update",
                "state": self.game_state.process_to_json()
            }
        ))

    @login_required
    def group_resend(self, data):
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name, {
                "type": "resend",
                "sender_id": self.user.id,
                "data": data
            }
        )

    def resend(self, data):
        self.send(text_data=data["data"])

    def on_receive_location_update(self, data_json):
        self.game_state.set_player_coordinates(self.user.id, data_json["coordinates"])
        self.send_game_state()

    def on_receive_authorization(self, data_json):
        self.user = User.objects.filter(id=int(data_json["token"])).first()
        if self.user is not None:
            self.game_state.add_player(self.user)
            self.game_user = GameUser.objects.filter(game=self.game_state.game, user=self.user).first()
            self.send(text_data=json.dumps({"status": f"authorization succeed as {self.user}"}))
        else:
            self.send(text_data=json.dumps({"status": f"authorization failed"}))
            self.close()

    def on_receive_send_game_state(self, data_json):
        self.send_game_state()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name,
            self.channel_name
        )

    def on_receive_task_completed(self, data_json):
        try:
            task_id = int(data_json["task_id"])
            game_task = GameQuestTask.objects.filter(settings__game=self.game_state.game, quest_task_id=task_id).first()
            photo = data_json["photo"]
            PlayerTaskCompletion(
                photo=photo,
                game_task=game_task,
                player=self.game_user
            ).save()
            self.game_state.update_from_db()
            self.send_game_state()
        except Exception:
            self.send(text_data=json.dumps({"status": "Your data bad somehow"}))

    def on_receive_player_caught(self, data_json):
        try:
            secret = data_json["secret"]


        except Exception:
            self.send(text_data=json.dumps({"status": "Your data bad somehow"}))
