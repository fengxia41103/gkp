# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0012_auto_20150127_2356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mymajor',
            name='code',
            field=models.CharField(default=b'', max_length=16, verbose_name='\u4e13\u4e1a\u4ee3\u7801'),
        ),
    ]
