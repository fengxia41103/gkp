# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0008_auto_20150126_0118'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='raw_page',
            field=models.TextField(null=True, verbose_name='\u539f\u59cbhtml data. Research used ONLY!', blank=True),
            preserve_default=True,
        ),
    ]
