# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0022_auto_20150226_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myschool',
            name='admission_office_phone',
            field=models.CharField(default=b'', max_length=64, null=True, verbose_name='\u62db\u751f\u7535\u8bdd', blank=True),
            preserve_default=True,
        ),
    ]
