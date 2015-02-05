# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0007_myadmissionbymajor_major'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myschool',
            name='key_field',
        ),
        migrations.AddField(
            model_name='myschool',
            name='en_name',
            field=models.CharField(max_length=256, null=True, verbose_name='\u82f1\u6587\u540d', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='no_fellow',
            field=models.IntegerField(null=True, verbose_name='\u9662\u58eb\u4eba\u6570', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='no_key_major',
            field=models.IntegerField(null=True, verbose_name='\u91cd\u70b9\u5b66\u79d1\u6570\u76ee', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='no_master_program',
            field=models.IntegerField(null=True, verbose_name='\u7855\u58eb\u70b9\u4e2a\u6570', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='no_phd_program',
            field=models.IntegerField(null=True, verbose_name='\u535a\u58eb\u70b9\u4e2a\u6570', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='no_student',
            field=models.IntegerField(null=True, verbose_name='\u5b66\u751f\u4eba\u6570', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='school_type',
            field=models.CharField(max_length=16, null=True, verbose_name='\u5b66\u6821\u7c7b\u578b', blank=True),
            preserve_default=True,
        ),
    ]
