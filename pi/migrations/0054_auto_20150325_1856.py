# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0053_myrank'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myrank',
            name='description',
        ),
        migrations.RemoveField(
            model_name='myrank',
            name='hash',
        ),
        migrations.RemoveField(
            model_name='myrank',
            name='help_text',
        ),
        migrations.RemoveField(
            model_name='myrank',
            name='name',
        ),
        migrations.RemoveField(
            model_name='myrank',
            name='tags',
        ),
    ]
