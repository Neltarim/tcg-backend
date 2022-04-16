from channels.db import database_sync_to_async
from ..models import *

def connectUser(user):
  lobby = Lobby.objects.all()[0]
  lobby.users.add(user)
  return lobby

def disconnectUser(user):
  lobby = Lobby.objects.all()[0]
  lobby.users.remove(user)

def clear():
  lobby = Lobby.objects.all()[0]

  for user in [u for u in lobby.users.all()]:
    lobby.users.remove(user)

clear()