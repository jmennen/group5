# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buzzit_models', '0006_auto_20150605_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='messages',
            field=models.ManyToManyField(null=True, to='buzzit_models.Circle_message'),
        ),
    ]
