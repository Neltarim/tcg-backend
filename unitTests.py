from game.models import *

def run():
  Lobby.objects.all()[0].users.all()[0]