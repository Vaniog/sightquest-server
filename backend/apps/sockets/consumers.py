import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

import json

from apps.api.models import Player, GameQuestTask, GamePhoto
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from .game.gamemanager import GameManagerHolder, GameManager
from datetime import timedelta, datetime

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
        text_data_json = json.loads(text_data)
        try:
            event_type = text_data_json["event"]
        except ValueError:
            self.send_error_message("Wrong protocol (use event)")
            return
        except TypeError:
            self.send_error_message("Wrong protocol (use event)")
            return

        if event_type == "authorization":
            self.on_receive_authorization(text_data_json)
            self.group_broadcast({
                "event": "gamestate_update",
                "state": self.game_manager.process_to_json()
            })
            return

        if self.user is None:
            self.send_error_message("You didnt complete authorization")
            self.close()

        try:
            if event_type == "get_game_state":
                self.on_receive_send_game_state()
            elif event_type == "location_update":
                self.on_receive_location_update(text_data_json)
            elif event_type == "task_completed":
                self.on_receive_task_completed(text_data_json)
            elif event_type == "player_caught":
                self.on_receive_player_caught(text_data_json)
            elif event_type == "settings_update":
                self.on_receive_settings_update(text_data_json)
            elif event_type == "start_game":
                self.on_receive_start_game(text_data_json)
            else:
                self.group_broadcast(text_data_json)
        except ValueError as err:
            self.send_error_message(str(err))
        except GameManager.IllegalStateAction:
            self.send_error_message(
                f"You can't perform {event_type} event in {self.game_manager.game.state} state"
            )

    def on_receive_authorization(self, data_json):
        self.user = User.objects.filter(id=int(data_json["token"])).first()
        if self.user is not None:
            self.game_manager.add_player(self.user)
            self.player = Player.objects.filter(game=self.game_manager.game, user=self.user).first()
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

    def on_receive_location_update(self, data_json):
        self.game_manager.set_player_coordinates(self.user.id, data_json["coordinates"])
        self.group_broadcast(data_json)

    def on_receive_send_game_state(self):
        self.send_game_state()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name,
            self.channel_name
        )

    def on_receive_task_completed(self, data_json):
        task_id = int(data_json["task_id"])
        photo_id = int(data_json["photo_id"])
        game_photo: GamePhoto = GamePhoto.objects.filter(id=photo_id).first()

        game_task = GameQuestTask.objects.filter(
            settings__game=self.game_manager.game,
            quest_task_id=task_id
        ).first()

        self.game_manager.complete_task(
            player=self.player,
            game_task=game_task,
            game_photo=game_photo
        )

        self.group_broadcast(data_json)

    def on_receive_player_caught(self, data_json):
        secret: str = data_json["secret"]
        self.game_manager.catch_player(
            self.player,
            self.game_manager.get_player_by_secret(secret)
        )
        self.player.refresh_from_db()
        self.group_broadcast(data_json)

    def on_receive_settings_update(self, data_json):
        settings = data_json["settings"]

        quest_points_data = settings["quest_points"]
        task_ids: list[int] = []
        for quest_point_data in quest_points_data:
            for quest_task_data in quest_point_data["tasks"]:
                task_ids.append(quest_task_data["id"])

        duration_str = settings["duration"]
        t = datetime.strptime(duration_str, "%H:%M:%S")
        duration = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

        self.game_manager.update_settings(
            duration, task_ids
        )

        self.group_broadcast(data_json)

    def on_receive_start_game(self, data_json):
        self.game_manager.start_game()
        self.group_broadcast(data_json)
