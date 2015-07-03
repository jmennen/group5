# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('buzzit_models', '0009_auto_20150605_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('owner', models.OneToOneField(to=settings.AUTH_USER_MODEL, serialize=False, primary_key=True)),
                ('show_own_messages_on_home_screen', models.BooleanField(default=True)),
            ],
        ),
    ]
