# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0042_auto_20150317_1604'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mybaidustream',
            old_name='posted',
            new_name='last_updated',
        ),
    ]
