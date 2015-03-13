# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0031_auto_20150313_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuserprofile',
            name='owner',
            field=models.OneToOneField(default=None, to=settings.AUTH_USER_MODEL, help_text=b'', verbose_name='\u7528\u6237'),
            preserve_default=True,
        ),
    ]
