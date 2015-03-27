# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pi', '0055_auto_20150326_1556'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyTaggedItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.SlugField(default=b'', max_length=16, verbose_name='Tag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='mybaidustream',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='mymajor',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='myschool',
            name='tags',
        ),
        migrations.AddField(
            model_name='myuserprofile',
            name='tags',
            field=models.ManyToManyField(to='pi.MyTaggedItem'),
            preserve_default=True,
        ),
    ]
