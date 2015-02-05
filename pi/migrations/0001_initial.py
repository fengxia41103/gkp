# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('name', models.CharField(default=b'default name', max_length=64, verbose_name='\u9644\u4ef6\u540d\u79f0')),
                ('description', models.CharField(default=b'default description', max_length=64, verbose_name='\u9644\u4ef6\u63cf\u8ff0')),
                ('file', models.FileField(help_text='\u9644\u4ef6', upload_to=b'files/%Y/%m/%d', verbose_name='\u9644\u4ef6')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(default=None, verbose_name='\u521b\u5efa\u7528\u6237', to=settings.AUTH_USER_MODEL, help_text=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('province', models.IntegerField(verbose_name='\u7701\u4efd', choices=[(1, '\u5317\u4eac'), (2, '\u5929\u6d25'), (3, '\u6cb3\u5317'), (4, '\u5c71\u897f'), (5, '\u5185\u8499\u53e4'), (6, '\u8fbd\u5b81'), (7, '\u5409\u6797'), (8, '\u9ed1\u9f99\u6c5f'), (9, '\u4e0a\u6d77'), (10, '\u6c5f\u82cf'), (11, '\u6d59\u6c5f'), (12, '\u5b89\u5fbd'), (13, '\u798f\u5efa'), (14, '\u6c5f\u897f'), (15, '\u5c71\u4e1c'), (16, '\u6cb3\u5357'), (17, '\u6e56\u5317'), (18, '\u6e56\u5357'), (19, '\u5e7f\u4e1c'), (20, '\u5e7f\u897f'), (21, '\u6d77\u5357'), (22, '\u91cd\u5e86'), (23, '\u56db\u5ddd'), (24, '\u8d35\u5dde'), (25, '\u4e91\u5357'), (26, '\u897f\u85cf'), (27, '\u9655\u897f'), (28, '\u7518\u8083'), (29, '\u9752\u6d77'), (30, '\u5b81\u590f'), (31, '\u65b0\u7586')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyAdminssion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=8, choices=[('\u6587\u79d1', '\u6587\u79d1'), ('\u7406\u79d1', '\u7406\u79d1'), ('\u7efc\u5408', '\u7efc\u5408'), ('\u5176\u4ed6', '\u5176\u4ed6')])),
                ('year', models.IntegerField()),
                ('batch', models.CharField(max_length=16, verbose_name='\u5f55\u53d6\u6279\u6b21')),
                ('min_score', models.IntegerField(null=True, verbose_name='\u6700\u4f4e\u5206', blank=True)),
                ('max_score', models.IntegerField(null=True, verbose_name='\u6700\u9ad8\u5206', blank=True)),
                ('avg_score', models.IntegerField(null=True, verbose_name='\u5e73\u5747\u5206', blank=True)),
                ('province_score', models.IntegerField(null=True, verbose_name='\u7701\u63a7\u5206', blank=True)),
                ('province', models.ForeignKey(verbose_name='\u62db\u751f\u5730\u533a', to='pi.MyAddress')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='\u4e13\u4e1a\u540d\u79f0')),
                ('category', models.CharField(max_length=64, verbose_name='\u4e13\u4e1a\u7c7b\u522b', choices=[('\u5de5\u5b66', '\u5de5\u5b66'), ('\u7406\u5b66', '\u7406\u5b66'), ('\u6cd5\u5b66', '\u54f2\u5b66'), ('\u6587\u5b66', '\u6587\u5b66'), ('\u827a\u672f\u5b66', '\u827a\u672f\u5b66'), ('\u7ecf\u6d4e\u5b66', '\u7ecf\u6d4e\u5b66'), ('\u5386\u53f2\u5b66', '\u5386\u53f2\u5b66'), ('\u7ba1\u7406\u5b66', '\u7ba1\u7406\u5b66')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MySchool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=None, max_length=64, verbose_name='\u540d\u79f0')),
                ('description', models.TextField(null=True, verbose_name='\u63cf\u8ff0', blank=True)),
                ('help_text', models.CharField(max_length=64, null=True, verbose_name='\u5e2e\u52a9\u63d0\u793a', blank=True)),
                ('tags', tagging.fields.TagField(default=b'default', max_length=255, verbose_name='\u6807\u7b7e', blank=True)),
                ('founded', models.IntegerField(null=True, verbose_name='\u521b\u5efa\u65f6\u95f4', blank=True)),
                ('key_field', models.IntegerField(null=True, verbose_name='\u91cd\u70b9\u5b66\u79d1', blank=True)),
                ('created_by', models.ForeignKey(default=None, verbose_name='\u521b\u5efa\u7528\u6237', to=settings.AUTH_USER_MODEL, help_text=b'')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='myadminssion',
            name='school',
            field=models.ForeignKey(verbose_name='\u9ad8\u6821\u540d\u79f0', to='pi.MySchool'),
            preserve_default=True,
        ),
    ]
