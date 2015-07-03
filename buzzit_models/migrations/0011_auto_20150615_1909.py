# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('buzzit_models', '0010_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='Directmessage',
            fields=[
                ('message_ptr', models.OneToOneField(auto_created=True, to='buzzit_models.Message', serialize=False, parent_link=True, primary_key=True)),
                ('read', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            bases=('buzzit_models.message',),
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('name', models.CharField(serialize=False, max_length=140, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='circle_message',
            name='mentions',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='circle_message',
            name='original_message',
            field=models.ForeignKey(to='buzzit_models.Circle_message', blank=True, related_name='repost_of', null=True),
        ),
        migrations.AddField(
            model_name='circle_message',
            name='themes',
            field=models.ManyToManyField(to='buzzit_models.Theme'),
        ),
    ]
