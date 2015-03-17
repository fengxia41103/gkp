# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0036_mycrawlerrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='mycrawlerrequest',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 17, 13, 50, 49, 478978), verbose_name='Using crawler machine timestamp', auto_now_add=True),
            preserve_default=True,
        ),
    ]
