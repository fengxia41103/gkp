# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0013_auto_20150128_0002'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mymajor',
            old_name='is_specalized',
            new_name='is_specialized',
        ),
        migrations.AlterField(
            model_name='mymajorcategory',
            name='name',
            field=models.CharField(default=b'', max_length=16, verbose_name='\u5b66\u79d1\u95e8\u7c7b'),
        ),
        migrations.AlterField(
            model_name='mymajorsubcategory',
            name='name',
            field=models.CharField(default=b'', max_length=16, verbose_name='\u4e13\u4e1a\u7c7b'),
        ),
    ]
