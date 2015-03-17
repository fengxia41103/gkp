# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0044_auto_20150317_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='source_url',
            field=models.URLField(default=1),
            preserve_default=False,
        ),
    ]
