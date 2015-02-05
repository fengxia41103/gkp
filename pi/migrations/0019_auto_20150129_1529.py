# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0018_auto_20150129_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mymajor',
            name='how_long',
            field=models.CharField(max_length=16, null=True, verbose_name='\u4fee\u5b66\u5e74\u9650', blank=True),
        ),
    ]
