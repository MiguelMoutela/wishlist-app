# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-19 00:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_remove_userprofile_per_item_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='per_item_email',
            field=models.BooleanField(default=True),
        ),
    ]
