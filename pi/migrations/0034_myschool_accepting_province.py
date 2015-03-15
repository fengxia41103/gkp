# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0033_auto_20150315_0259'),
    ]

    operations = [
        migrations.AddField(
            model_name='myschool',
            name='accepting_province',
            field=models.ManyToManyField(related_name='accepting_provinces', verbose_name='\u62db\u751f\u5730\u533a', to='pi.MyAddress'),
            preserve_default=True,
        ),
    ]
