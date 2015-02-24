# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0020_auto_20150220_0300'),
    ]

    operations = [
        migrations.RenameField(
            model_name='myschool',
            old_name='google_geo_code',
            new_name='google_geocode',
        ),
    ]
