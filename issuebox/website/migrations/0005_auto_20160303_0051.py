# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-03 00:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_comment_comments'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='comments',
            new_name='commenter',
        ),
    ]
