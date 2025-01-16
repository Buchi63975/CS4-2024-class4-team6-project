from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import User
from .models import ChatMessage  # メッセージのデータベースモデルをインポート


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URLの一部で受信者のユーザー名を取得（`receiver` はURLルートの引数で指定される）
        self.receiver_username = self.scope["url_route"]["kwargs"]["username"]
        self.sender = self.scope["user"]  # 現在のユーザー（送信者）

        # チャットルーム名は送信者と受信者のユーザー名で一意に設定
        self.room_name = f"{self.sender.username}_{self.receiver_username}"
        self.room_group_name = f"chat_{self.room_name}"

        # グループに参加
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # 履歴の取得と送信
        past_messages = ChatMessage.objects.filter(
            sender=self.sender, receiver=self.receiver_username
        ).order_by("created_at")  # メッセージ履歴を取得（送信者と受信者の間）

        for message in past_messages:
            await self.send(
                text_data=json.dumps(
                    {
                        "sender": message.sender.username,
                        "content": message.content,
                        "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
            )

    async def disconnect(self, close_code):
        # グループから離脱
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data["message"]

        # メッセージをデータベースに保存
        message = ChatMessage.objects.create(
            sender=self.sender,
            receiver=User.objects.get(username=self.receiver_username),
            content=message_content,
        )

        # メッセージをグループに送信
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender": self.sender.username,
                "content": message_content,
                "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

    async def chat_message(self, event):
        sender = event["sender"]
        content = event["content"]
        created_at = event["created_at"]

        # クライアントにメッセージを送信
        await self.send(
            text_data=json.dumps(
                {
                    "sender": sender,
                    "content": content,
                    "created_at": created_at,
                }
            )
        )
