# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0010_auto_20150126_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mymajor',
            name='degree_type',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='\u6559\u80b2\u7c7b\u522b', choices=[('\u672c\u79d1', '\u672c\u79d1'), ('\u4e13\u79d1', '\u4e13\u79d1'), ('\u804c\u4e1a\u6559\u80b2', '\u804c\u4e1a\u6559\u80b2')]),
        ),
    ]
