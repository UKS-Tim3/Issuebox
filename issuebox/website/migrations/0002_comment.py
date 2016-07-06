# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-02 23:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=300)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Issue')),
            ],
        ),
    ]
