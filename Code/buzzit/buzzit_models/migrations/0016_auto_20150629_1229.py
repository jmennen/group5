# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('buzzit_models', '0015_accountactivation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('message_ptr', models.OneToOneField(serialize=False, parent_link=True, to='buzzit_models.Message', auto_created=True, primary_key=True)),
                ('closed', models.BooleanField(default=False)),
                ('valid', models.BooleanField(default=False)),
            ],
            bases=('buzzit_models.message',),
        ),
        migrations.CreateModel(
            name='CircleMessageReport',
            fields=[
                ('report_ptr', models.OneToOneField(serialize=False, parent_link=True, to='buzzit_models.Report', auto_created=True, primary_key=True)),
                ('reported_message', models.OneToOneField(to='buzzit_models.Circle_message')),
            ],
            bases=('buzzit_models.report',),
        ),
        migrations.CreateModel(
            name='UserReport',
            fields=[
                ('report_ptr', models.OneToOneField(serialize=False, parent_link=True, to='buzzit_models.Report', auto_created=True, primary_key=True)),
                ('reported_user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            bases=('buzzit_models.report',),
        ),
        migrations.AddField(
            model_name='report',
            name='issuer',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
