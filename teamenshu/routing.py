# routing.py
from django.urls import path
from teamenshu import consumers

websocket_urlpatterns = [
    path("ws/chat/", consumers.ChatConsumer.as_asgi()),  # WebSocketエンドポイント
]
