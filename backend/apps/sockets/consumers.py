import json

from apps.api.models import PlayerLobby
from apps.api.serializers import PlayerLobbySerializer
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer


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


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_id = self.scope["url_route"]["kwargs"]["lobby_id"]
        self.lobby_group_name = "lobby_%s" % self.lobby_id

        await self.channel_layer.group_add(self.lobby_group_name, self.channel_name)

        await self.accept()

        await self.send_lobby_info()

    async def send_lobby_info(self):
        try:
            lobby = PlayerLobby.objects.get(pk=self.lobby_id)
            lobby_data = PlayerLobbySerializer(lobby).data
            await self.send(text_data=json.dumps({"lobby_info": lobby_data}))
        except PlayerLobby.DoesNotExist:
            await self.close()

    # Получение сообщения от WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Отправка сообщения в группу лобби
        await self.channel_layer.group_send(
            self.lobby_group_name, {"type": "lobby_message", "message": message}
        )

    # Получение сообщения из группы лобби
    async def lobby_message(self, event):
        message = event["message"]

        # Отправка сообщения в WebSocket
        await self.send(text_data=json.dumps({"message": message}))
