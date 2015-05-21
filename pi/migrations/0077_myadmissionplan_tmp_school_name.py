# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0076_auto_20150507_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='myadmissionplan',
            name='tmp_school_name',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
