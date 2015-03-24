# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0051_myuserprofile_school_bookmarks'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuserprofile',
            name='school_xouts',
            field=models.ManyToManyField(related_name='xouts', to='pi.MySchool'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myuserprofile',
            name='school_bookmarks',
            field=models.ManyToManyField(related_name='bookmarks', to='pi.MySchool'),
            preserve_default=True,
        ),
    ]
