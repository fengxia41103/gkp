# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0077_myadmissionplan_tmp_school_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='myadmissionplan',
            name='major',
            field=models.ForeignKey(verbose_name='Major', blank=True, to='pi.MyMajor', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myadmissionplan',
            name='province',
            field=models.ForeignKey(default=None, verbose_name=b'Admission province', to='pi.MyProvince'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='myadmissionplan',
            name='school',
            field=models.ForeignKey(verbose_name=b'School', blank=True, to='pi.MySchool', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myadmissionplan',
            name='tmp_major',
            field=models.CharField(max_length=b'128', null=True, verbose_name=b'Major temp', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myadmissionplan',
            name='tmp_school_name',
            field=models.CharField(max_length=128, null=True, blank=True),
            preserve_default=True,
        ),
    ]
