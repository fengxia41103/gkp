# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0023_auto_20150226_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='lat',
            field=models.DecimalField(decimal_places=15, default=0, max_digits=20, blank=True, null=True, verbose_name='Address lat'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='lng',
            field=models.DecimalField(decimal_places=15, default=0, max_digits=20, blank=True, null=True, verbose_name='Address lng'),
            preserve_default=True,
        ),
    ]
