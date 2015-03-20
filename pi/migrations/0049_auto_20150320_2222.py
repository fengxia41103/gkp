# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0048_auto_20150317_2314'),
    ]

    operations = [
        migrations.AddField(
            model_name='mycrawlerrequest',
            name='is_processing',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myuserprofile',
            name='estimated_score',
            field=models.IntegerField(default=200, verbose_name='\u5206\u6570'),
            preserve_default=True,
        ),
    ]
