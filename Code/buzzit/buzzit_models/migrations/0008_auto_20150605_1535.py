# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('buzzit_models', '0007_auto_20150605_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
