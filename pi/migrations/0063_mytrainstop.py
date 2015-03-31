# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0062_auto_20150330_0003'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyTrainStop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('train_id', models.CharField(max_length=8, verbose_name='\u8f66\u6b21')),
                ('stop_index', models.IntegerField(verbose_name='\u505c\u9760\u7ad9\u5e8f')),
                ('stop_name', models.CharField(max_length=64, verbose_name='\u7ad9\u540d')),
                ('arrival', models.DateTimeField(null=True, verbose_name='\u5230\u7ad9\u65f6\u95f4', blank=True)),
                ('departure', models.DateTimeField(null=True, verbose_name='\u53d1\u8f66\u65f6\u95f4', blank=True)),
                ('seconds_since_initial', models.IntegerField(default=0, verbose_name='\u8fd0\u884c\u65f6\u95f4')),
                ('province', models.ForeignKey(verbose_name='\u7701\u4efd', blank=True, to='pi.MyAddress', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
