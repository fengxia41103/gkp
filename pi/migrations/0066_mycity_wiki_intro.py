# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0065_auto_20150402_0332'),
    ]

    operations = [
        migrations.AddField(
            model_name='mycity',
            name='wiki_intro',
            field=models.TextField(null=True, verbose_name='Wiki', blank=True),
            preserve_default=True,
        ),
    ]
