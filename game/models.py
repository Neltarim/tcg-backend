from django.db import models
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

class Lobby(models.Model):
    room_name = models.CharField(max_length=150, unique=True)
    users = models.ManyToManyField(User)