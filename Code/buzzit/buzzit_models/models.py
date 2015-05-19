from django.db import models
from django.contrib.auth.models import User

class Profile(User):
    profile_picture = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    gender = models.CharField(blank=True, null=True)
