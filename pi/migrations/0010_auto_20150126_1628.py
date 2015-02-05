# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0009_myschool_raw_page'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyMajorCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=8, verbose_name='\u5b66\u79d1\u95e8\u7c7b')),
                ('code', models.CharField(max_length=4, verbose_name='\u4ee3\u7801')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyMajorSubcategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=8, verbose_name='\u4e13\u4e1a\u7c7b')),
                ('code', models.CharField(max_length=4, verbose_name='\u4ee3\u7801')),
                ('category', models.ForeignKey(verbose_name='\u5b66\u79d1\u95e8\u7c7b', blank=True, to='pi.MyMajorCategory', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='mymajor',
            name='category',
        ),
        migrations.RemoveField(
            model_name='mymajor',
            name='course_description',
        ),
        migrations.AddField(
            model_name='mymajor',
            name='course',
            field=models.TextField(max_length=8, null=True, verbose_name='\u4fee\u5b66\u5e74\u9650', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mymajor',
            name='is_gov_controlled',
            field=models.BooleanField(default=False, verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mymajor',
            name='is_specalized',
            field=models.BooleanField(default=False, verbose_name=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mymajor',
            name='subcategory',
            field=models.ForeignKey(verbose_name='\u4e13\u4e1a\u7c7b', blank=True, to='pi.MyMajorSubcategory', null=True),
        ),
    ]
