# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0037_mycrawlerrequest_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mycrawlerrequest',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Using crawler machine timestamp'),
            preserve_default=True,
        ),
    ]
