# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buzzit_models', '0011_auto_20150615_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle_message',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
