# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0035_auto_20150317_1340'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyCrawlerRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.IntegerField(verbose_name='\u6570\u636e\u6e90', choices=[(1, '\u767e\u5ea6\u8d34\u5427'), (2, '\u65b0\u6d6a\u5fae\u535a')])),
                ('params', annoying.fields.JSONField(verbose_name='\u6570\u636e\u53c2\u6570')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
