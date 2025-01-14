from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"user_{self.user.id}", self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        to_user = data["to"]

        # メッセージをDBに保存（非同期処理）
        await self.save_message(to_user, message)

        # 受信者のグループにメッセージを送信
        await self.channel_layer.group_send(
            f"user_{to_user}",
            {
                "type": "chat.message",
                "message": message,
                "from": self.user.id,
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "from": event["from"],
                }
            )
        )

    @database_sync_to_async
    def save_message(self, to_user, message):
        # ここでDBに保存する処理を実装
        pass
