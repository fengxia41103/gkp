# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0046_auto_20150317_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='source_url',
            field=models.URLField(max_length=512, verbose_name='File origin url'),
            preserve_default=True,
        ),
    ]
