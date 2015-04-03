# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0066_mycity_wiki_intro'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuserprofile',
            name='city',
            field=models.ForeignKey(verbose_name='City', blank=True, to='pi.MyCity', null=True),
            preserve_default=True,
        ),
    ]
