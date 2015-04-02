# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0064_auto_20150402_0325'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyCity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city', models.CharField(max_length=32, verbose_name='City')),
                ('city_en', models.CharField(max_length=32, verbose_name='in English')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='MyAddress',
            new_name='MyProvince',
        ),
        migrations.AddField(
            model_name='mycity',
            name='province',
            field=models.ForeignKey(verbose_name='Province', blank=True, to='pi.MyProvince', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mytrainstop',
            name='category',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='\u7c7b\u522b', choices=[(b'PK', '\u666e\u5feb'), (b'MM', '\u6162\u8f66'), (b'G', '\u9ad8\u94c1'), (b'Z', '\u76f4\u8fbe\u7279\u5feb'), (b'C', '\u57ce\u9645'), (b'T', '\u7279\u5feb'), (b'K', '\u5feb\u8f66'), (b'D', '\u52a8\u8f66')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myschool',
            name='city',
            field=models.ForeignKey(verbose_name='\u6240\u5904\u57ce\u5e02', blank=True, to='pi.MyCity', null=True),
            preserve_default=True,
        ),
    ]
