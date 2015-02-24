# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0019_auto_20150129_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='myaddress',
            name='province_en',
            field=models.CharField(default='', max_length=32, verbose_name='in English'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='myschool',
            name='formatted_address_en',
            field=models.CharField(max_length=256, null=True, verbose_name='Google geocode address', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='google_geo_code',
            field=annoying.fields.JSONField(null=True, verbose_name='Google geocode result', blank=True),
            preserve_default=True,
        ),
    ]
