# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0024_auto_20150227_0219'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='baidu_geocode',
            field=annoying.fields.JSONField(null=True, verbose_name='Baidu geocode result', blank=True),
            preserve_default=True,
        ),
    ]
