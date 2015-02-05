# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0011_auto_20150127_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mymajorcategory',
            name='name',
            field=models.CharField(max_length=16, verbose_name='\u5b66\u79d1\u95e8\u7c7b'),
        ),
        migrations.AlterField(
            model_name='mymajorsubcategory',
            name='name',
            field=models.CharField(max_length=16, verbose_name='\u4e13\u4e1a\u7c7b'),
        ),
    ]
