# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0070_remove_myjob_total_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='MySogouStream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(default=b'', max_length=256, null=True, verbose_name='MD5 hash', blank=True)),
                ('name', models.CharField(default=None, max_length=128, verbose_name='\u540d\u79f0')),
                ('description', models.TextField(null=True, verbose_name='\u63cf\u8ff0', blank=True)),
                ('help_text', models.CharField(max_length=64, null=True, verbose_name='\u5e2e\u52a9\u63d0\u793a', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Using crawler machine timestamp')),
                ('author', models.CharField(max_length=64, null=True, verbose_name='\u4f5c\u8005', blank=True)),
                ('author_id', models.CharField(max_length=64, null=True, verbose_name='\u4f5c\u8005ID', blank=True)),
                ('url_original', models.URLField(default=b'', max_length=512, verbose_name='Data source original link')),
                ('last_updated', models.DateTimeField(null=True, verbose_name='Posted timestamp read from the source site', blank=True)),
                ('school', models.ForeignKey(verbose_name='\u6240\u5c5e\u5b66\u6821', blank=True, to='pi.MySchool', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyWeixinAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(default=b'', max_length=256, null=True, verbose_name='MD5 hash', blank=True)),
                ('name', models.CharField(default=None, max_length=128, verbose_name='\u540d\u79f0')),
                ('description', models.TextField(null=True, verbose_name='\u63cf\u8ff0', blank=True)),
                ('help_text', models.CharField(max_length=64, null=True, verbose_name='\u5e2e\u52a9\u63d0\u793a', blank=True)),
                ('account', models.CharField(max_length=32, verbose_name='Account ID')),
                ('icon', models.FileField(upload_to=b'weixin/icon', verbose_name='icon')),
                ('barcode', models.FileField(upload_to=b'weixin/barcode', verbose_name='barcode')),
                ('school', models.ForeignKey(verbose_name='Related \u5b66\u6821', blank=True, to='pi.MySchool', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
