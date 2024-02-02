import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

import json

from apps.api.models import Game
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model

User = get_user_model()

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
        if event_type == "authorization":
            self.receive_authorization(text_data_json)
        # Майку на подумать
        # elif event_type == "location_update":
        #     self.receive_location_update(text_data_json)
        else:
            self.group_resend(text_data)

    @login_required
    def group_resend(self, data):
        print(self.game_group_name)
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name, {
                "type": "resend",
                "sender_id": self.user.id,
                "data": data
            }
        )

    def resend(self, data):
        # Майку на подумать
        # if data["sender_id"] != self.user.id:
        self.send(text_data=data["data"])

    def receive_authorization(self, data_json):
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
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name, {
                "type": "location_update",
                "sender_id": self.user.id,
                "coordinates": data_json["coordinates"]
            }
        )
        self.users_coords[self.user.id] = data_json["coordinates"]
        self.send(text_data=json.dumps(self.users_coords))

    def location_update(self, data_json):
        self.users_coords[data_json["sender_id"]] = data_json["coordinates"]

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name,
            self.channel_name
        )
