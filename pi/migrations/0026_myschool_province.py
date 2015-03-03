# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0025_myschool_baidu_geocode'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='province',
            field=models.ForeignKey(verbose_name='\u6240\u5904\u7701', blank=True, to='pi.MyAddress', null=True),
            preserve_default=True,
        ),
    ]
