# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0058_auto_20150328_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mybaidustream',
            name='reply_num',
            field=models.IntegerField(null=True, verbose_name='\u56de\u590d\u6570', blank=True),
            preserve_default=True,
        ),
    ]
