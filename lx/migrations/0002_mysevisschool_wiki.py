# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lx', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysevisschool',
            name='wiki',
            field=models.TextField(null=True, verbose_name='Wiki text', blank=True),
            preserve_default=True,
        ),
    ]
