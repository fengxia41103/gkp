# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0063_mytrainstop'),
    ]

    operations = [
        migrations.AddField(
            model_name='mytrainstop',
            name='category',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='\u7c7b\u522b', choices=[(b'PK', '\u666e\u5feb'), (b'MM', '\u6162\u8f66'), (b'G', '\u9ad8\u94c1'), (b'Z', '\u76f4\u8fbe\u7279\u5feb'), (b'C', '\u57ce\u9645'), (b'T', '\u7279\u5feb'), (b'K', '\u5feb\u8f66'), (b'D', '\u52a8\u8f66')]),
            preserve_default=True,
        ),
    ]
