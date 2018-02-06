# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('date', models.DateField()),
                ('from_user', models.ForeignKey(related_name='outgoing_transfers', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('to_user', models.ForeignKey(related_name='incoming_transfers', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
    ]
