#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from teamenshu.consumers import ChatConsumer  # 後で作成します

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Channelsの設定
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/chat/", ChatConsumer.as_asgi()),
                ]
            )
        ),
    }
)


def main():
    """Run administrative tasks."""
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
