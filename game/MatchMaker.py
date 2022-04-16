import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import authenticate
from channels.db import database_sync_to_async as db_call

from .database import lobbyQueries as Lobby_q


class MatchMaker(AsyncJsonWebsocketConsumer):

  async def connect(self):
    self.room_name = 'lobby'
    self.room_group_name = 'group_lobby'

    # Join room group
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
    
    else:
      print("Couldn't authenticate'")
      await self.disconnect('Login failed')
      await self.close()

  async def testFunc(self, event):
    print(event['message'])