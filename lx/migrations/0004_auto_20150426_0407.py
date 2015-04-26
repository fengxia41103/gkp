# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lx', '0003_mysevisschool_wiki_quick_facts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysevisschool',
            name='campus',
            field=models.CharField(max_length=128, null=True, blank=True),
            preserve_default=True,
        ),
    ]
