from ..models import *

def connectUser(user):
  lobby = Lobby.objects.all()[0]
  lobby.users.add(user)
  return lobby

def disconnectUser(user):
  lobby = Lobby.objects.all()[0]
  lobby.users.remove(user)
  for room in WaitingRoom.objects.all():
    for usr in WaitingRoom.objects.all():
      if usr == user:
        room.delete()

def clear():
  lobby = Lobby.objects.all()[0]
  WaitingRoom.objects.all().delete()
  GameRoom.objects.all().delete()

  for user in [u for u in lobby.users.all()]:
    lobby.users.remove(user)

def getlobbyPlayers():
  return [i for i in Lobby.objects.all()[0].users.all()]

def enterWaitingRoom(user):
  rooms = WaitingRoom.objects.all()
  for r in rooms:
    roomLen = len(r.users.all())
    if roomLen < 2:
      r.users.add(user)
      return [roomLen + 1, r]

  room = WaitingRoom()
  room.save()
  room.users.add(user)
  return [1, room]

clear()