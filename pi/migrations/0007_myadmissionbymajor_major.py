# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0006_auto_20150122_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='myadmissionbymajor',
            name='major',
            field=models.ForeignKey(default=2, verbose_name='\u4e13\u4e1a\u540d\u79f0', to='pi.MyMajor'),
            preserve_default=False,
        ),
    ]
