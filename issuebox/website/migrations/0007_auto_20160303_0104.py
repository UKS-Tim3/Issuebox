# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-03 01:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_auto_20160303_0059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.CharField(choices=[(0, 'New'), (1, 'In Progress'), (2, 'Closed')], max_length=1),
        ),
    ]
