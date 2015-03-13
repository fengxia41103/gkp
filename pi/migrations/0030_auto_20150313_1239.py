# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pi', '0029_auto_20150312_1748'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUserProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('estimated_score', models.IntegerField(default=-1, verbose_name='\u5206\u6570')),
                ('student_type', models.CharField(blank=True, max_length=8, null=True, verbose_name='\u8003\u751f\u7c7b\u522b', choices=[(b'', b''), ('\u6587\u79d1', '\u6587\u79d1'), ('\u7406\u79d1', '\u7406\u79d1')])),
                ('degree_type', models.CharField(blank=True, max_length=8, null=True, verbose_name='\u5b66\u4f4d\u7c7b\u522b', choices=[(b'', b''), ('\u672c\u79d1', '\u672c\u79d1'), ('\u4e13\u79d1', '\u4e13\u79d1')])),
                ('owner', models.ForeignKey(default=None, verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL, help_text=b'')),
                ('province', models.ForeignKey(verbose_name='\u5165\u8003\u7701\u4efd', blank=True, to='pi.MyAddress', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='mymajor',
            name='student_type',
            field=models.CharField(max_length=8, null=True, verbose_name='\u6587\u7406\u79d1', blank=True),
            preserve_default=True,
        ),
    ]
