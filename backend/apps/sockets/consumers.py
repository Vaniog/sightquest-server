import os
import django

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
# Инициализируем Django
django.setup()

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from apps.api.models import Game

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = "test"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

        self.send(text_data=json.dumps({"type": "chat", "message": "connected!"}))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    def chat_message(self, event):
        message = event["message"]

        self.send(text_data=json.dumps({"type": "chat", "message": message}))


class LobbyConsumer(WebsocketConsumer):
    def connect(self):
        self.lobby_id = self.scope["url_route"]["kwargs"]["lobby_id"]
        self.lobby_group_name = "lobby_%s" % self.lobby_id

        async_to_sync(self.channel_layer.group_add)(
            self.lobby_group_name, self.channel_name
        )

        self.accept()

        async_to_sync(self.channel_layer.group_send)(
            self.lobby_group_name,
            {
                "type": "lobby_message",
                "message": f"Player {self.scope['user']} joined lobby {self.lobby_id}",
            },
        )

        self.send_lobby_info()

    def send_lobby_info(self):
        # try:
        # lobby = PlayerLobby.objects.get(pk=self.lobby_id)
        # lobby_data = PlayerLobbySerializer(lobby).data
        self.send(text_data=json.dumps({"lobby_info": f"{self.lobby_id}"}))
        # except PlayerLobby.DoesNotExist:
        #     self.close()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        self.channel_layer.group_send(
            self.lobby_group_name, {"type": "lobby_message", "message": message}
        )

    def lobby_message(self, event):
        message = event["message"]

        self.send(text_data=json.dumps({"message": message}))


class GameConsumer(WebsocketConsumer):
    game_id: int
    game_group_name: str
    game: Game
    user: User = None

    users_coords: dict = {}

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
        self.game_id = int(self.scope["url_route"]["kwargs"]["game_id"])
        self.game = Game.objects.filter(id=self.game_id).first()

        self.game_group_name = "game_%s" % self.game_id

        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )
        self.accept()

        self.send(text_data=json.dumps({"status": "connected"}))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event_type = text_data_json["event"]
        print(f"event: {event_type}")
        if event_type == "authorization":
            self.receive_authorization(text_data_json)
        elif event_type == "location_update":
            self.receive_location_update(text_data_json)
        else:
            self.send(text_data=json.dumps({"message": f"Event {event_type} doesn't supported"}))

    def receive_authorization(self, data_json):
        print(int(data_json["token"]))
        self.user = User.objects.filter(id=int(data_json["token"])).first()
        if self.user not in self.game.players.all():
            self.send(text_data=json.dumps({"status": f"you arent in game"}))
            self.user = None
        if self.user is not None:
            self.send(text_data=json.dumps({"status": f"authorization succeed as {self.user}"}))
        else:
            self.send(text_data=json.dumps({"status": f"authorization failed"}))
            self.close()

    @login_required
    def receive_location_update(self, data_json):
        self.channel_layer.group_send(
            self.game_group_name, {
                "type": "location_update",
                "user_id": data_json["user_id"],
                "coordinates": data_json["coordinates"]
            }
        )
        self.users_coords[data_json["user_id"]] = data_json["coordinates"]
        self.send(text_data=json.dumps(self.users_coords))

    def location_update(self, data_json):
        self.users_coords[data_json["user_id"]] = data_json["coordinates"]

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name,
            self.channel_name
        )
