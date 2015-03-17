# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0041_auto_20150317_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mybaidustream',
            name='posted',
            field=models.DateTimeField(null=True, verbose_name='Posted timestamp read from the source site', blank=True),
            preserve_default=True,
        ),
    ]
