# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('buzzit_models', '0016_auto_20150629_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreport',
            name='reported_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
