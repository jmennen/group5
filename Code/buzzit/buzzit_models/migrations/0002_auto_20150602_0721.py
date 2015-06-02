# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('buzzit_models', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Circle',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created', models.DateTimeField()),
                ('text', models.CharField(max_length=140)),
            ],
        ),
        migrations.CreateModel(
            name='Circle_message',
            fields=[
                ('message_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, parent_link=True, to='buzzit_models.Message')),
                ('answer_to', models.ForeignKey(null=True, blank=True, to='buzzit_models.Circle_message')),
            ],
            bases=('buzzit_models.message',),
        ),
        migrations.AddField(
            model_name='message',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='circle',
            name='messages',
            field=models.ManyToManyField(to='buzzit_models.Message'),
        ),
        migrations.AddField(
            model_name='circle',
            name='owner',
            field=models.ForeignKey(related_name='owner_of_circle', to=settings.AUTH_USER_MODEL),
        ),
    ]
