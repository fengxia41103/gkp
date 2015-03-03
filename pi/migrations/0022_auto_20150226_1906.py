# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0021_auto_20150220_0305'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='address',
            field=models.CharField(default=b'', max_length=256, null=True, verbose_name='\u5b66\u6821\u5730\u5740', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='admission_office_email',
            field=models.EmailField(default=b'', max_length=75, null=True, verbose_name='\u62db\u751f\u7535\u5b50\u90ae\u7bb1', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='admission_office_phone',
            field=models.CharField(default=b'', max_length=24, null=True, verbose_name='\u62db\u751f\u7535\u8bdd', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='city',
            field=models.CharField(default=b'', max_length=64, null=True, verbose_name='\u6240\u5904\u57ce\u5e02', blank=True),
            preserve_default=True,
        ),
    ]
