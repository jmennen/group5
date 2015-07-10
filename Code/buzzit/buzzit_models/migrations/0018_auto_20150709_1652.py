# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buzzit_models', '0017_auto_20150708_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circlemessagereport',
            name='reported_message',
            field=models.ForeignKey(to='buzzit_models.Circle_message'),
        ),
    ]
