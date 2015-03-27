# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0056_auto_20150326_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='mymajor',
            name='tags',
            field=models.ManyToManyField(to='pi.MyTaggedItem'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mymajor',
            name='schools',
            field=models.ManyToManyField(related_name='majors', to='pi.MySchool'),
            preserve_default=True,
        ),
    ]
