# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buzzit_models', '0004_auto_20150602_2232'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='follows',
            field=models.ManyToManyField(related_name='follows_rel_+', to='buzzit_models.Profile'),
        ),
    ]
