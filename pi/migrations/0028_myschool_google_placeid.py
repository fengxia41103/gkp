# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0027_myschool_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='google_placeid',
            field=models.CharField(default=b'', max_length=64, null=True, verbose_name='Google geocoding place id', blank=True),
            preserve_default=True,
        ),
    ]
