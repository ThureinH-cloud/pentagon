"""
ASGI config for pentagon project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from reader.consumers import CommentConsumer
from channels.sessions import SessionMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pentagon.settings')

application=ProtocolTypeRouter({
    'http':get_asgi_application(),
        "websocket":SessionMiddlewareStack(
            AuthMiddlewareStack(
            URLRouter([
                re_path(r"ws/comments/(?P<author_id>\d+)/$", CommentConsumer.as_asgi()),
            ])
        ),
    )
})