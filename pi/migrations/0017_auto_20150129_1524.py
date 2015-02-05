# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0016_auto_20150129_0157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mymajor',
            name='degree_type',
            field=models.CharField(default='\u672c\u79d1', max_length=8, verbose_name='\u6559\u80b2\u7c7b\u522b', choices=[(b'', b''), ('\u672c\u79d1', '\u672c\u79d1'), ('\u4e13\u79d1', '\u4e13\u79d1'), ('\u804c\u4e1a\u6559\u80b2', '\u804c\u4e1a\u6559\u80b2')]),
        ),
        migrations.AlterField(
            model_name='mymajor',
            name='how_long',
            field=models.CharField(default='\u56db\u5e74', max_length=16, verbose_name='\u4fee\u5b66\u5e74\u9650'),
        ),
    ]
