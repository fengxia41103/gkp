# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0075_auto_20150420_1616'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyAdmissionPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tmp_major', models.CharField(max_length=b'128', verbose_name=b'Major temp')),
                ('plan_type', models.CharField(max_length=64, verbose_name='\u8ba1\u5212\u7c7b\u578b')),
                ('degree_type', models.CharField(max_length=8, verbose_name='\u5c42\u6b21', choices=[(b'', b''), ('\u672c\u79d1', '\u672c\u79d1'), ('\u4e13\u79d1', '\u4e13\u79d1')])),
                ('student_type', models.CharField(max_length=8, verbose_name='\u79d1\u7c7b', choices=[(b'', b''), ('\u6587\u79d1', '\u6587\u79d1'), ('\u7406\u79d1', '\u7406\u79d1')])),
                ('count', models.IntegerField(verbose_name='\u8ba1\u5212\u6570')),
                ('school', models.ForeignKey(verbose_name=b'School', to='pi.MySchool')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='myweixinaccount',
            name='school',
            field=models.ForeignKey(related_name='school_weixin', verbose_name='Related \u5b66\u6821', blank=True, to='pi.MySchool', null=True),
            preserve_default=True,
        ),
    ]
