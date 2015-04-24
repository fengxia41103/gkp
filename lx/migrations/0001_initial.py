# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MySEVISSchool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw_html', models.TextField()),
                ('name', models.CharField(max_length=128)),
                ('campus', models.CharField(default=b'', max_length=128)),
                ('campus_id', models.IntegerField()),
                ('f_1', models.BooleanField(default=False)),
                ('m_1', models.BooleanField(default=False)),
                ('mailing_address', models.TextField()),
                ('sevis_mailing', models.CharField(max_length=128, null=True, blank=True)),
                ('physical_address', models.TextField()),
                ('sevis_physical', models.CharField(max_length=128, null=True, blank=True)),
                ('google_placeid', models.CharField(default=b'', max_length=256, null=True, verbose_name='Google geocoding place id', blank=True)),
                ('google_geocode', annoying.fields.JSONField(null=True, verbose_name='Google geocode result', blank=True)),
                ('baidu_geocode', annoying.fields.JSONField(null=True, verbose_name='Baidu geocode result', blank=True)),
                ('lat', models.DecimalField(decimal_places=15, default=0, max_digits=20, blank=True, null=True, verbose_name='Geo lat')),
                ('lng', models.DecimalField(decimal_places=15, default=0, max_digits=20, blank=True, null=True, verbose_name='Geo lng')),
                ('formatted_address', models.CharField(max_length=256, null=True, verbose_name='Google geocode address', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
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
        migrations.CreateModel(
            name='MyZip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zipcode', models.CharField(default=b'', max_length=16, verbose_name='Zip')),
                ('city', models.CharField(max_length=32, verbose_name='City')),
                ('state', models.CharField(max_length=8, verbose_name='State abbr')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='mysevisschool',
            name='mailing_zip',
            field=models.ForeignKey(related_name='mailing_zip', blank=True, to='lx.MyZip', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mysevisschool',
            name='physical_zip',
            field=models.ForeignKey(related_name='physical_zip', blank=True, to='lx.MyZip', null=True),
            preserve_default=True,
        ),
    ]
