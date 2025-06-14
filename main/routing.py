from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/online-status/", consumers.OnlineStatusConsumer.as_asgi()),
]
