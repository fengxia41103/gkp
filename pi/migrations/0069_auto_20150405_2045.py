# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0068_myjob'),
    ]

    operations = [
        migrations.AddField(
            model_name='mymajor',
            name='job_stat',
            field=models.IntegerField(default=0, verbose_name='Job count'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mymajorsubcategory',
            name='category',
            field=models.ForeignKey(related_name='subs', verbose_name='\u5b66\u79d1\u95e8\u7c7b', blank=True, to='pi.MyMajorCategory', null=True),
            preserve_default=True,
        ),
    ]
