# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0057_auto_20150327_0143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mybaidustream',
            name='url_original',
            field=models.URLField(default=b'', max_length=512, verbose_name='Data source original link'),
            preserve_default=True,
        ),
    ]
