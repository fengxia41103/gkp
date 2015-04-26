# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from django.forms import ModelForm
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from annoying.fields import JSONField # django-annoying
from django.db.models import Q
from datetime import datetime as dt
from pi.models import Attachment

class MyBaseModel (models.Model):
	# fields
	hash = models.CharField (
		max_length = 256, # we don't expect using a hash more than 256-bit long!
		null = True,
		blank = True,
		default = '',
		verbose_name = u'MD5 hash'
	)
		
	# basic value fields
	name = models.CharField(
			default = None,
			max_length = 128,
			verbose_name = u'名称'
		)
	description = models.TextField (
			null=True, 
			blank=True,
			verbose_name = u'描述'
		)
	
	# help text
	help_text = models.CharField (
			max_length = 64,
			null = True,
			blank = True,
			verbose_name = u'帮助提示'
		)

	# attachments
	attachments = GenericRelation('Attachment')
	
	# this is an Abstract model
	class Meta:
		abstract=True

	def __unicode__(self):
		return self.name

######################################################
#
#	Tags
#
#####################################################
class MyTaggedItem (models.Model):
	# basic value fields
	tag = models.SlugField(
			default = '',
			max_length = 16,
			verbose_name = u'Tag'
	)	
	def __unicode__(self):
		return self.tag

######################################################
#
#	App specific models
#
#####################################################
class MyZip(models.Model):
	zipcode = models.CharField(
		max_length = 16,
		default = '',
		verbose_name = u'Zip'
	)
	city = models.CharField(
		max_length = 32,
		verbose_name = u'City'
	)
	state = models.CharField(
		max_length = 8,
		verbose_name = u'State abbr'
	)
	def __unicode__(self):
		return ','.join([self.city, self.state, self.zipcode])

class MySEVISSchool(models.Model):
	def __unicode__(self):
		return self.name

	# we saved SEVIS HTML page
	raw_html = models.TextField()

	wiki = models.TextField(
		blank = True,
		null = True,
		verbose_name = u'Wiki text'
	)
	wiki_quick_facts = models.TextField(
		blank = True,
		null = True,
		verbose_name = u'Wiki quick facts'
	)

	# models
	name = models.CharField(
		max_length = 128,
	)
	campus = models.CharField(
		null = True,
		blank = True,
		max_length = 128
	)
	campus_id = models.IntegerField()
	f_1 = models.BooleanField(
		default = False
	)
	m_1 = models.BooleanField(
		default = False
	)
	mailing_address = models.TextField(
	)
	mailing_zip = models.ForeignKey(
		'MyZip',
		null = True,
		blank = True,
		related_name = 'mailing_zip'
	)
	sevis_mailing = models.CharField(
		max_length = 128,
		null = True,
		blank = True,
	)
	physical_address = models.TextField(
	)
	physical_zip = models.ForeignKey(
		'MyZip',
		null = True,
		blank = True,
		related_name = 'physical_zip'
	)
	sevis_physical = models.CharField(
		max_length = 128,
		null = True,
		blank = True,
	)
	google_placeid = models.CharField (
		max_length = 256,
		null = True,
		blank = True,
		default = '',
		verbose_name = u'Google geocoding place id'
	)
	google_geocode = JSONField (
		null = True,
		blank = True,
		verbose_name = u'Google geocode result'
	)
	baidu_geocode = JSONField (
		null = True,
		blank = True,
		verbose_name = u'Baidu geocode result'
	)
	lat = models.DecimalField (
		max_digits = 20,
		decimal_places = 15,
		null = True,
		blank = True,
		default = 0,
		verbose_name = u'Geo lat'
	)
	lng = models.DecimalField (
		max_digits = 20,
		decimal_places = 15,
		null = True,
		blank = True,
		default = 0,
		verbose_name = u'Geo lng'
	)
	formatted_address = models.CharField (
		max_length = 256,
		null=True,
		blank=True,
		verbose_name = u'Google geocode address'
	)				