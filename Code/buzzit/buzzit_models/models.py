from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    profile_picture = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    gender = models.CharField(blank=True, null=True, max_length=1)
    follows = models.ManyToManyField("self", symmetrical=False)


class Message(models.Model):
    creator = models.ForeignKey(User, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False)
    text = models.CharField(blank=False, null=False, max_length=140)


class Circle_message(Message):
    answer_to = models.ForeignKey("self", blank=True, null=True)  # ist Antwort auf Kreisnachricht


class Circle(models.Model):
    owner = models.ForeignKey(User, blank=False, null=False, related_name="owner_of_circle")  # User erstellt Kreis
    messages = models.ManyToManyField(Circle_message, symmetrical=False)  # Kreis enthält Nachrichten
    members = models.ManyToManyField(User, symmetrical=False)  # Kreis enthält User
    name = models.CharField(max_length=40, null=False, blank=False)
