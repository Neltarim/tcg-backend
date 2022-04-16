import json, random, string
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import authenticate
from channels.db import database_sync_to_async as db_call

from .database import lobbyQueries as Lobby_q
from .database import gameQueries as Game_q


class MatchMaker(AsyncJsonWebsocketConsumer):

  async def connect(self):
    self.room_name = 'lobby'
    self.room_group_name = 'group_lobby'

    # Join lobby
    await self.channel_layer.group_add(
      self.room_group_name,
      self.channel_name
    )
    await self.accept()

  async def disconnect(self, close_code):
    # Leave room group
    await db_call(Lobby_q.disconnectUser)(self.user)
    await self.channel_layer.group_discard(
      self.room_group_name,
      self.channel_name
    )
    await self.close()
    print("Disconnected")

  async def send_message(self, res):
    """ Send message to WebSocket """
    await self.send(text_data=json.dumps({
      "payload": res,
    }))

  async def receive(self, text_data):
    """
    Receive message from WebSocket.
    Get the event and send the appropriate event
    """
    response = json.loads(text_data)
    event = response.get("event", None)
    message = response.get("message", None)
    print(
      'Event :%s \nmessage :%s' % (event, message)
    )
    if event == 'LOGIN':
      await self.login(
        username=response.get("username", None),
        password=response.get("password", None)
      )

    if not self.scope['user']:
      print("Couldn't authenticate'")
      await self.disconnect('Login failed')
      await self.close()

    ## START EVENT HANDLING ##
    if event == 'DISCONNECT':
      await self.disconnect('Disconnect')

    if event == 'TEST':
      await self.channel_layer.group_send(
        self.room_group_name,
        {
            "type": "testFunc",
            "username": self.user.username,
            "message": 'test throwed by : ' + self.user.username,
        }
      )


  async def login(self, username, password):
    self.user = await db_call(authenticate)(
      username=username, password=password
    )
    if self.user:
      self.lobby = await db_call(Lobby_q.connectUser)(self.user)
      print('NEW USER CONNECTED :' + username)
      await self.findMatch()
    
    else:
      print("Couldn't authenticate'")
      await self.disconnect('Login failed')
      await self.close()

  async def testFunc(self, event):
    print(event['message'])

  async def findMatch(self):
    data = await db_call(Lobby_q.enterWaitingRoom)(self.user)
    self.waitingRoom = data[1]
    roomPopulation = data[0]

    await self.channel_layer.group_add(
      str(self.waitingRoom.id),
      self.channel_name
    )
    letters = string.ascii_lowercase
    if roomPopulation == 2:
      token = ''.join(random.choice(letters) for i in range(10))
      await db_call(Game_q.createRoom)(token)

      print('Game found')
      await self.channel_layer.group_send(
        str(self.waitingRoom.id),
        { "type" : "startMatch", 'token': token }
      )

    else:
      await self.send_message({
        'event': 'WAITING_ROOM', 
        'message' : 'Currently in waiting room.'
      })

  async def startMatch(self, event):
    await db_call(Lobby_q.disconnectUser)(self.user)
    await self.send_message({
      'event': 'JOIN_GAME', 
      'message': 'Game found.',
      'token': event['token']
    })
    await self.disconnect('GAME_FOUND')