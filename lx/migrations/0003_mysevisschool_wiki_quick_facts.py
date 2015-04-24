# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lx', '0002_mysevisschool_wiki'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysevisschool',
            name='wiki_quick_facts',
            field=models.TextField(null=True, verbose_name='Wiki quick facts', blank=True),
            preserve_default=True,
        ),
    ]
