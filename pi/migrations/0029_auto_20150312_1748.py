# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0028_myschool_google_placeid'),
    ]

    operations = [
        migrations.AddField(
            model_name='mymajor',
            name='student_type',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='\u6587\u7406\u79d1', choices=[(b'', b''), ('\u6587\u79d1', '\u6587\u79d1'), ('\u7406\u79d1', '\u7406\u79d1')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myadmissionbymajor',
            name='category',
            field=models.CharField(max_length=8, choices=[(b'', b''), ('\u6587\u79d1', '\u6587\u79d1'), ('\u7406\u79d1', '\u7406\u79d1'), ('\u7efc\u5408', '\u7efc\u5408'), ('\u5176\u4ed6', '\u5176\u4ed6')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myadmissionbyschool',
            name='category',
            field=models.CharField(max_length=8, choices=[(b'', b''), ('\u6587\u79d1', '\u6587\u79d1'), ('\u7406\u79d1', '\u7406\u79d1'), ('\u7efc\u5408', '\u7efc\u5408'), ('\u5176\u4ed6', '\u5176\u4ed6')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mymajor',
            name='course',
            field=models.TextField(max_length=8, null=True, verbose_name='\u4e13\u4e1a\u8bfe\u7a0b', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mymajor',
            name='degree_type',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='\u6559\u80b2\u7c7b\u522b', choices=[(b'', b''), ('\u672c\u79d1', '\u672c\u79d1'), ('\u4e13\u79d1', '\u4e13\u79d1')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mymajor',
            name='is_gov_controlled',
            field=models.BooleanField(default=False, verbose_name='\u56fd\u5bb6\u63a7\u5236\u5e03\u70b9\u4e13\u4e1a'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mymajor',
            name='is_specialized',
            field=models.BooleanField(default=False, verbose_name='\u7279\u8bbe\u4e13\u4e1a'),
            preserve_default=True,
        ),
    ]
