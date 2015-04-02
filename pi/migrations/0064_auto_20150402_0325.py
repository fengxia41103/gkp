# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0063_mytrainstop'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='city2',
            field=models.CharField(max_length=64, null=True, verbose_name='\u6240\u5904\u57ce\u5e02', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myschool',
            name='city',
            field=models.CharField(max_length=64, null=True, verbose_name='\u6240\u5904\u57ce\u5e02', blank=True),
            preserve_default=True,
        ),
    ]
