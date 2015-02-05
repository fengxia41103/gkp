# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0004_auto_20150121_0634'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyMajor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=None, max_length=64, verbose_name='\u540d\u79f0')),
                ('description', models.TextField(null=True, verbose_name='\u63cf\u8ff0', blank=True)),
                ('help_text', models.CharField(max_length=64, null=True, verbose_name='\u5e2e\u52a9\u63d0\u793a', blank=True)),
                ('tags', tagging.fields.TagField(default=b'default', max_length=255, verbose_name='\u6807\u7b7e', blank=True)),
                ('code', models.CharField(max_length=16, verbose_name='\u4e13\u4e1a\u4ee3\u7801')),
                ('category', models.CharField(max_length=64, verbose_name='\u4e13\u4e1a\u5927\u7c7b', choices=[('\u5de5\u5b66', '\u5de5\u5b66'), ('\u7406\u5b66', '\u7406\u5b66'), ('\u6cd5\u5b66', '\u54f2\u5b66'), ('\u6587\u5b66', '\u6587\u5b66'), ('\u827a\u672f\u5b66', '\u827a\u672f\u5b66'), ('\u7ecf\u6d4e\u5b66', '\u7ecf\u6d4e\u5b66'), ('\u5386\u53f2\u5b66', '\u5386\u53f2\u5b66'), ('\u54f2\u5b66', '\u54f2\u5b66'), ('\u7ba1\u7406\u5b66', '\u7ba1\u7406\u5b66'), ('\u533b\u5b66', '\u533b\u5b66'), ('\u7ba1\u7406\u5b66', '\u7ba1\u7406\u5b66'), ('\u519c\u5b66', '\u519c\u5b66')])),
                ('subcategory', models.CharField(max_length=32, null=True, verbose_name='\u4e13\u4e1a\u7c7b\u522b', blank=True)),
                ('degree_type', models.CharField(max_length=8, verbose_name='\u6559\u80b2\u7c7b\u522b', choices=[('\u672c\u79d1', '\u672c\u79d1'), ('\u4e13\u79d1', '\u4e13\u79d1'), ('\u804c\u4e1a\u6559\u80b2', '\u804c\u4e1a\u6559\u80b2')])),
                ('degree', models.CharField(max_length=32, null=True, verbose_name='\u6388\u4e88\u5b66\u4f4d', blank=True)),
                ('how_long', models.CharField(max_length=8, null=True, verbose_name='\u4fee\u5b66\u5e74\u9650', blank=True)),
                ('course_description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='MyField',
        ),
    ]
