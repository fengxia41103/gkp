# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0060_auto_20150329_0215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mybaidustream',
            name='author',
            field=models.CharField(max_length=64, null=True, verbose_name='\u4f5c\u8005', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mybaidustream',
            name='school',
            field=models.ForeignKey(verbose_name='\u6240\u5c5e\u5b66\u6821', blank=True, to='pi.MySchool', null=True),
            preserve_default=True,
        ),
    ]
