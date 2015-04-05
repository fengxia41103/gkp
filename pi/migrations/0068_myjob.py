# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0067_myuserprofile_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Using crawler machine timestamp')),
                ('source_url', models.URLField(max_length=512, verbose_name='Job post source URL')),
                ('total_count', models.IntegerField(default=0, verbose_name='Found total job post count')),
                ('co_name', models.CharField(max_length=128, null=True, verbose_name='Employer name', blank=True)),
                ('co_type', models.CharField(max_length=16, null=True, verbose_name='Employer type', blank=True)),
                ('co_size', models.CharField(max_length=64, null=True, verbose_name='Employer size', blank=True)),
                ('title', models.CharField(max_length=64, null=True, verbose_name='Job title', blank=True)),
                ('location', models.CharField(max_length=32, null=True, verbose_name='Job location', blank=True)),
                ('req_degree', models.CharField(max_length=8, null=True, verbose_name='Degree requirement', blank=True)),
                ('req_experience', models.CharField(max_length=16, null=True, verbose_name='Experience requirement', blank=True)),
                ('majors', models.ManyToManyField(related_name='jobs', verbose_name='Related major', to='pi.MyMajor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
