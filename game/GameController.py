import json
from random import choice
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import authenticate
from channels.db import database_sync_to_async as db_call

from .database import gameQueries as Game_q

class GameController(AsyncJsonWebsocketConsumer):
  async def connect(self):
    self.room_name = self.scope['url_route']['kwargs']['room_code']
    self.room_group_name = 'room_%s' % self.room_name
    # Join room group
    await self.channel_layer.group_add(
      self.room_group_name,
      self.channel_name
    )
    await self.accept()

  async def disconnect(self, close_code):
    print("Disconnected")
    # Leave room group
    await db_call(Game_q.leaveRoom)(self.user, self.room_name)
    await self.channel_layer.group_discard(
      self.room_group_name,
      self.channel_name
    )
    await self.channel_layer.group_send(
      self.room_group_name,
      { "type": "giveUp", "username": self.user.username }
    )

  async def login(self, username, password):
    self.user = await db_call(authenticate)(
      username=username, password=password
    )
    if self.user:
      roomData = await db_call(Game_q.enterRoom)(self.user, self.room_name)
      roomPopulation = roomData[0]
      if roomPopulation:
        self.room = roomData[1]
        self.opponent = roomData[3]
        print(username + ' Entered the game. TOKEN:' + self.room_group_name)
        if roomPopulation == 2:
          gm = choice([self.user.username, self.opponent.username])
          self.channel_layer.group_send(
            self.room_group_name,
            { 'type': "initGame", 'gameMaster': gm }
          )

        else:
          self.send_message({
            'event': 'WAITING_PLAYER',
            'message': 'Waiting for the other player.'
          })

      else:
        self.send_message({
          'event': 'WRONG_TOKEN',
          'message' : 'wrong room token provided.'
        })
        self.disconnect()
    
    else:
      print("Couldn't authenticate'")
      await self.disconnect('Login failed')
      await self.close()

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

  async def initGame(self, event):
    self.gameMaster = event['gm'] == self.user.username