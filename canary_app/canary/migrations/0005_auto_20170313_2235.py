# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-13 22:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canary', '0004_auto_20170313_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userkeyword',
            name='keyword_name',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
