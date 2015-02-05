# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myschool',
            name='created_by',
        ),
    ]
