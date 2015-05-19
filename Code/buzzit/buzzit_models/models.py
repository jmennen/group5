from django.db import models
from django.contrib.auth.models import User

class Profile(User):
    """

    """
    profile_picture = models.URLField(blank=True, null=True)