from django.urls import re_path, path
from .consumers import PersonalChatConsumer,ChatConsumer


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$',ChatConsumer.as_asgi()),
    path('ws/<int:id>/', PersonalChatConsumer.as_asgi()),
    path('wss/<int:id>/', PersonalChatConsumer.as_asgi())

]