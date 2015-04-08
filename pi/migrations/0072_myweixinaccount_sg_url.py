# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0071_mysogoustream_myweixinaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='myweixinaccount',
            name='sg_url',
            field=models.URLField(default='', max_length=512, verbose_name='Sogou URL'),
            preserve_default=False,
        ),
    ]
