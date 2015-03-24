# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0050_delete_mycrawlerrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuserprofile',
            name='school_bookmarks',
            field=models.ManyToManyField(to='pi.MySchool'),
            preserve_default=True,
        ),
    ]
