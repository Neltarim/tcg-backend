from django.conf.urls import url

from game.MatchMaker import MatchMaker
from game.GameController import GameController

websocket_urlpatterns = [
    url(r'^play/(?P<room_code>\w+)/$', GameController.as_asgi()),
    url(r'^match-maker/$', MatchMaker.as_asgi()),
]