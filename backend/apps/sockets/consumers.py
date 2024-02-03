import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

import json

from apps.api.models import Game
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from .game.gamestatemanager import GameStateManager, GameState
from .game.serializers import GameStateSerializer

User = get_user_model()


class GameConsumer(WebsocketConsumer):
    game_code: str
    game_group_name: str
    game_state: GameState
    user: User = None

    @staticmethod
    def login_required(func):
        def wrapper(self, *args, **kwargs):
            if self.user is None:
                self.send("You aren't authorize")
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

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event_type = text_data_json["event"]
        if event_type == "authorization":
            self.receive_authorization(text_data_json)
        if event_type == "get_game_state":
            self.send()
        if event_type == "location_update":
            self.game_state.set_player_coordinates(self.user.id, text_data_json["coordinates"])
            self.send(text_data=GameStateSerializer(self.game_state, many=False))
        else:
            self.group_resend(text_data)

    @login_required
    def group_resend(self, data):
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name, {
                "type": "resend",
                "sender_id": self.user.id,
                "data": self.game_group_name
            }
        )

    def resend(self, data):
        print(data["data"])
        self.send(text_data=data["data"])

    def receive_authorization(self, data_json):
        self.user = User.objects.filter(id=int(data_json["token"])).first()
        if self.user is not None:
            self.send(text_data=json.dumps({"status": f"authorization succeed as {self.user}"}))
        else:
            self.send(text_data=json.dumps({"status": f"authorization failed"}))
            self.close()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name,
            self.channel_name
        )
