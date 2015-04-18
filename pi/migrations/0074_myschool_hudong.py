# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0073_auto_20150408_0201'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='hudong',
            field=models.TextField(null=True, verbose_name='Hudong wiki', blank=True),
            preserve_default=True,
        ),
    ]
