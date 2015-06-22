# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('buzzit_models', '0014_profile_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountActivation',
            fields=[
                ('username', models.OneToOneField(primary_key=True, to=settings.AUTH_USER_MODEL, serialize=False, to_field='username')),
                ('token', models.CharField(max_length=40)),
            ],
        ),
    ]
