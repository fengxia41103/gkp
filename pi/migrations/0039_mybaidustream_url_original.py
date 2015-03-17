# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0038_auto_20150317_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='mybaidustream',
            name='url_original',
            field=models.URLField(default=b'', verbose_name='Data source original link'),
            preserve_default=True,
        ),
    ]
