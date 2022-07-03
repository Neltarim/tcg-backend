from ..models import *

def createRoom(token):
  room = GameRoom()
  room.token = token
  room.save()

def enterRoom(user, token):
  room = GameRoom.objects.get(token=token)

  if room:
    room.user.add(user)
    return [len(room.users.objects.all()), room]
      
  else:
    return [0]

def leaveRoom(token):
  room = GameRoom.objects.get(token=token)
  room.delete()