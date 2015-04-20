# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0074_myschool_hudong'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='hudong_raw_html',
            field=models.TextField(null=True, verbose_name='Hudong wiki raw html. Research used ONLY!', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='hudong_summary_table',
            field=models.TextField(null=True, verbose_name='Hudong summary table', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myschool',
            name='hudong_toc',
            field=models.TextField(null=True, verbose_name='Hudong table of contents', blank=True),
            preserve_default=True,
        ),
    ]
