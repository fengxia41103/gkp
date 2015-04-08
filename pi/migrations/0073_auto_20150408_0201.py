# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0072_myweixinaccount_sg_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myweixinaccount',
            name='barcode',
            field=models.FileField(upload_to=b'weixin/barcode', null=True, verbose_name='barcode', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myweixinaccount',
            name='icon',
            field=models.FileField(upload_to=b'weixin/icon', null=True, verbose_name='icon', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myweixinaccount',
            name='sg_url',
            field=models.URLField(max_length=512, null=True, verbose_name='Sogou URL', blank=True),
            preserve_default=True,
        ),
    ]
