# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0069_auto_20150405_2045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myjob',
            name='total_count',
        ),
    ]
