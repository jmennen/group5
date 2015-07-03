# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, primary_key=True, serialize=False)),
                ('profile_picture', models.URLField(null=True, blank=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('gender', models.CharField(null=True, blank=True, max_length=1)),
            ],
        ),
    ]
