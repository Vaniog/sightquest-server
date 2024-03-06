import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

import json

from apps.api.models import Player
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from .game.gamemanager import GameManagerHolder, GameManager
from .game.dto import *

User = get_user_model()


class GameConsumer(WebsocketConsumer):
    game_code: str
    game_group_name: str
    game_manager: GameManager
    user: User = None
    player: Player = None

    def connect(self):
        self.game_code = str(self.scope["url_route"]["kwargs"]["game_id"])
        self.game_manager = GameManagerHolder.get_game_manager(self.game_code)
        if self.game_manager.game is None:
            self.close()

        self.game_group_name = "game_%s" % self.game_code

        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )
        self.accept()

        self.send_status_message("connection succeeded")

    def receive(self, text_data):
        data_json = json.loads(text_data)
        try:
            event: EventDTO = EventDTO.model_validate(data_json)
        except ValueError:
            self.send_error_message("Use event protocol")
            return

        if event.event == "authorization":
            self.on_receive_authorization(data_json)
            self.group_broadcast({
                "event": "gamestate_update",
                "state": self.game_manager.process_to_json()
            })
            return

        if self.user is None:
            self.send_error_message("You didnt complete authorization")
            self.close()

        try:
            if event.event == "get_game_state":
                self.on_receive_send_game_state()
            elif event.event == "location_update":
                self.on_receive_location_update(data_json)
            elif event.event == "task_completed":
                self.on_receive_task_completed(data_json)
            elif event.event == "player_caught":
                self.on_receive_player_caught(data_json)
            elif event.event == "settings_update":
                self.on_receive_settings_update(data_json)
            elif event.event == "start_game":
                self.on_receive_start_game(data_json)
            else:
                self.group_broadcast(data_json)
        except ValueError as err:
            self.send_error_message(str(err))
        except GameManager.IllegalStateAction:
            self.send_error_message(
                f"You can't perform {event.event} event in {self.game_manager.game.state} state"
            )

    def on_receive_authorization(self, data_json):
        authorization = AuthorizationDTO.model_validate(data_json)
        self.user = User.objects.filter(id=int(authorization.token)).first()

        if self.user is not None:
            self.game_manager.add_player(self.user)
            self.player = Player.objects.filter(
                game=self.game_manager.game,
                user=self.user
            ).first()
            self.send_status_message(f"authorization succeeded as {self.user}")
        else:
            self.send_error_message("authorization failed")
            self.close()

    def send_game_state(self):
        self.send(text_data=json.dumps(
            {
                "event": "gamestate_update",
                "state": self.game_manager.process_to_json()
            }
        ))

    def group_broadcast(self, data):
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name, {
                "type": "broadcast",
                "sender_id": self.user.id,
                "data": data
            }
        )

    def broadcast(self, data):
        self.send(text_data=json.dumps(data["data"]))

    def send_status_message(self, message):
        self.send(json.dumps({
            "event": "status",
            "message": message
        }))

    def send_error_message(self, message):
        self.send(json.dumps({
            "event": "error",
            "message": message
        }))

    def on_receive_send_game_state(self):
        self.send_game_state()

    def on_receive_location_update(self, data_json):
        event: LocationUpdateDTO = LocationUpdateDTO.model_validate(data_json)
        self.game_manager.set_player_coordinates(event.user.id, event.coordinates)
        self.group_broadcast(data_json)

    def on_receive_task_completed(self, data_json):
        event: TaskCompletedDTO = TaskCompletedDTO.model_validate(data_json)
        self.game_manager.complete_task(event)
        self.group_broadcast(data_json)

    def on_receive_player_caught(self, data_json):
        event: PlayerCaughtDTO = PlayerCaughtDTO.model_validate(data_json)
        self.game_manager.catch_player(event)
        self.refresh_all_players()
        self.group_broadcast(data_json)

    def on_receive_settings_update(self, data_json):
        event: SettingsUpdateDTO = SettingsUpdateDTO.model_validate(data_json)
        self.game_manager.update_settings(event.settings)
        self.group_broadcast(data_json)

    def on_receive_start_game(self, data_json):
        self.game_manager.start_game()
        self.group_broadcast(data_json)
        self.refresh_all_players()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name,
            self.channel_name
        )

    def refresh_all_players(self):
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name, {
                "type": "refresh_player",
            }
        )

    def refresh_player(self, data):
        self.user = User.objects.filter(id=self.user.id).first()
        self.player = Player.objects.filter(game=self.game_manager.game, user=self.user).first()
