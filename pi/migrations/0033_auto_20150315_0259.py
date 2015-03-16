# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0032_auto_20150313_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='take_1st_batch',
            field=models.NullBooleanField(default=False, verbose_name='\u62db\u6536\u672c\u79d1\u4e00\u6279'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='take_2nd_batch',
            field=models.NullBooleanField(default=False, verbose_name='\u62db\u6536\u672c\u79d1\u4e8c\u6279'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='take_3rd_batch',
            field=models.NullBooleanField(default=False, verbose_name='\u62db\u6536\u672c\u79d1\u4e09\u6279'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='take_associate',
            field=models.NullBooleanField(default=False, verbose_name='\u62db\u6536\u4e13\u79d1\u751f'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='take_bachelor',
            field=models.NullBooleanField(default=False, verbose_name='\u62db\u6536\u672c\u79d1\u751f'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='take_pre',
            field=models.NullBooleanField(default=False, verbose_name='\u63d0\u524d\u62db\u751f'),
            preserve_default=True,
        ),
    ]
