# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_ptr', models.OneToOneField(serialize=False, primary_key=True, auto_created=True, parent_link=True, to=settings.AUTH_USER_MODEL)),
                ('profile_picture', models.URLField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('gender', models.CharField(max_length=1, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'user',
                'abstract': False,
                'verbose_name_plural': 'users',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
