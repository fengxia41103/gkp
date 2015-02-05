# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0002_remove_myschool_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myaddress',
            name='province',
            field=models.CharField(max_length=8, verbose_name='\u7701\u4efd'),
        ),
    ]
