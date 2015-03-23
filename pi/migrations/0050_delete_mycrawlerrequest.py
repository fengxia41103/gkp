# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0049_auto_20150320_2222'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MyCrawlerRequest',
        ),
    ]
