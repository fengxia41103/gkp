# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0047_auto_20150317_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='mybaidustream',
            name='hash',
            field=models.CharField(default=b'', max_length=256, null=True, verbose_name='MD5 hash', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mymajor',
            name='hash',
            field=models.CharField(default=b'', max_length=256, null=True, verbose_name='MD5 hash', blank=True),
            preserve_default=True,
        ),
    ]
