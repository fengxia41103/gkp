# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0052_auto_20150324_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyRank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(default=b'', max_length=256, null=True, verbose_name='MD5 hash', blank=True)),
                ('name', models.CharField(default=None, max_length=64, verbose_name='\u540d\u79f0')),
                ('description', models.TextField(null=True, verbose_name='\u63cf\u8ff0', blank=True)),
                ('help_text', models.CharField(max_length=64, null=True, verbose_name='\u5e2e\u52a9\u63d0\u793a', blank=True)),
                ('tags', tagging.fields.TagField(default=b'default', max_length=255, verbose_name='\u6807\u7b7e', blank=True)),
                ('rank_index', models.IntegerField(verbose_name='\u6392\u540d\u7ef4\u5ea6', choices=[(0, '\u672a\u77e5'), (1, '\u6309\u6700\u4f4e\u5f55\u53d6\u5206\u6570\u7ebf\u6392\u540d'), (2, '\u6309\u6700\u9ad8\u5f55\u53d6\u5206\u6570\u7ebf\u6392\u540d'), (3, '\u6309\u5e73\u5747\u5f55\u53d6\u5206\u6570\u7ebf\u6392\u540d'), (4, '\u6309\u4e13\u4e1a\u79cd\u7c7b')])),
                ('rank', models.IntegerField(default=0, verbose_name='\u6253\u5206')),
                ('school', models.ForeignKey(verbose_name='\u9ad8\u6821\u540d\u79f0', to='pi.MySchool')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
