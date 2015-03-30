# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0061_auto_20150329_0230'),
    ]

    operations = [
        migrations.AddField(
            model_name='mybaidustream',
            name='author_id',
            field=models.CharField(max_length=64, null=True, verbose_name='\u4f5c\u8005ID', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myrank',
            name='rank_index',
            field=models.IntegerField(verbose_name='\u6392\u540d\u7ef4\u5ea6', choices=[(-1, '\u7efc\u5408\u8bc4\u5206'), (0, '\u672a\u77e5'), (1, '\u6309\u6700\u4f4e\u5f55\u53d6\u5206\u6570\u7ebf\u6392\u540d'), (2, '\u6309\u6700\u9ad8\u5f55\u53d6\u5206\u6570\u7ebf\u6392\u540d'), (3, '\u6309\u5e73\u5747\u5f55\u53d6\u5206\u6570\u7ebf\u6392\u540d')]),
            preserve_default=True,
        ),
    ]
