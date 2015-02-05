# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0003_auto_20150121_0633'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyAdmission',
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
                ('school', models.ForeignKey(verbose_name='\u9ad8\u6821\u540d\u79f0', to='pi.MySchool')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='myadminssion',
            name='province',
        ),
        migrations.RemoveField(
            model_name='myadminssion',
            name='school',
        ),
        migrations.DeleteModel(
            name='MyAdminssion',
        ),
    ]
