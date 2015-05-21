# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0078_auto_20150507_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myadmissionplan',
            name='count',
            field=models.IntegerField(null=True, verbose_name='\u8ba1\u5212\u6570', blank=True),
            preserve_default=True,
        ),
    ]
