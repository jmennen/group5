# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buzzit_models', '0002_auto_20150602_0721'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='name',
            field=models.CharField(default='kreis', max_length=40),
            preserve_default=False,
        ),
    ]
