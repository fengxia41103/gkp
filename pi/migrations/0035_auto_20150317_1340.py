# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0034_myschool_accepting_province'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyBaiduStream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=None, max_length=64, verbose_name='\u540d\u79f0')),
                ('description', models.TextField(null=True, verbose_name='\u63cf\u8ff0', blank=True)),
                ('help_text', models.CharField(max_length=64, null=True, verbose_name='\u5e2e\u52a9\u63d0\u793a', blank=True)),
                ('tags', tagging.fields.TagField(default=b'default', max_length=255, verbose_name='\u6807\u7b7e', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Using crawler machine timestamp')),
                ('author', models.CharField(max_length=64, verbose_name='\u4f5c\u8005')),
                ('reply_num', models.IntegerField(verbose_name='\u56de\u590d\u6570')),
                ('school', models.ForeignKey(verbose_name='\u6240\u5c5e\u5b66\u6821', to='pi.MySchool')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='myschool',
            name='accepting_province',
            field=models.ManyToManyField(related_name='accepting_schools', verbose_name='\u62db\u751f\u5b66\u6821', to='pi.MyAddress'),
            preserve_default=True,
        ),
    ]
