# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buzzit_models', '0003_circle_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='messages',
            field=models.ManyToManyField(to='buzzit_models.Circle_message'),
        ),
    ]
