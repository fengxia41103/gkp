# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0059_auto_20150329_0207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mybaidustream',
            name='name',
            field=models.CharField(default=None, max_length=128, verbose_name='\u540d\u79f0'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mymajor',
            name='name',
            field=models.CharField(default=None, max_length=128, verbose_name='\u540d\u79f0'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myschool',
            name='name',
            field=models.CharField(default=None, max_length=128, verbose_name='\u540d\u79f0'),
            preserve_default=True,
        ),
    ]
