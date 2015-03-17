# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0045_attachment_source_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(help_text='\u9644\u4ef6', upload_to=b'%Y/%m/%d', verbose_name='\u9644\u4ef6'),
            preserve_default=True,
        ),
    ]
