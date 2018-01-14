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
            name='Charge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('raw_amount', models.CharField(max_length=1023)),
                ('date', models.DateField()),
                ('from_user', models.ForeignKey(related_name='revenues', to=settings.AUTH_USER_MODEL)),
                ('to_users', models.ManyToManyField(related_name='expenses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
