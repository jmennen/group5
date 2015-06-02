from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    profile_picture = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    gender = models.CharField(blank=True, null=True, max_length=1)


class Message(models.Model):
    creator = models.ForeignKey(User, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False)
    text = models.CharField(blank=False, null=False, max_length=140)


class Circle(models.Model):
    owner = models.ForeignKey(User, blank=False, null=False) # User erstellt Kreis
    messages = models.ManyToManyField(Message, blank=True, null=True) # Kreis enth�lt Nachrichten
    members = models.ManyToManyField(User, blank=True, null=True) # Kreis enth�lt User


class Circle_message(Message):
    answer_to = models.ForeignKey("self", blank=True, null=True, related_name="answer_to") # ist Antwort auf Kreisnachricht