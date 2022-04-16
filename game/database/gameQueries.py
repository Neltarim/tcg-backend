from ..models import *

def createRoom(token):
  rooms = GameRoom()
  rooms.token = token
  rooms.save()