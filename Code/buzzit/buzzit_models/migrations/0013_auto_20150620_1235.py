# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buzzit_models', '0012_circle_message_public'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='profile_picture',
        ),
        migrations.AddField(
            model_name='profile',
            name='profile_picture_full',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='profile',
            name='profile_picture_small',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
