# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from django.forms import ModelForm
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from tagging.fields import TagField
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone
from datetime import datetime

class MyBaseModel (models.Model):
	# basic value fields
	name = models.CharField(
			default = None,
			max_length = 64,
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
		
	# tags
	tags = TagField( 
			default = 'default',
			verbose_name = u'标签'
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
#	Attachments
#
#####################################################
class Attachment (models.Model):
	# generic foreign key to base model
	# so we can link attachment to any model defined below
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

	# instance fields
	created_by = models.ForeignKey (
			User,
			default = None,
			verbose_name = u'创建用户',
			help_text = ''
		)
		
	# basic value fields
	name = models.CharField(
			default = 'default name',
			max_length = 64,
			verbose_name = u'附件名称'
		)
	description = models.CharField (
			max_length = 64,
			default = 'default description',
			verbose_name = u'附件描述'
		)
	
	file = models.FileField (
			upload_to = 'files/%Y/%m/%d',
			verbose_name = u'附件',
			help_text = u'附件'
		)	

	def __unicode__(self):
		return self.file.name

class AttachmentForm(ModelForm):
	class Meta:
		model = Attachment
		fields = ['description','file']

######################################################
#
#	App specific models
#
#####################################################
class MyAddress (models.Model):
	province = models.CharField (
			max_length = 8,
			verbose_name = u'省份',
		)	

	def __unicode__(self):
		return self.province

class MyMajorCategory (models.Model):
	name = models.CharField(
		max_length = 16,
		default = '',
		verbose_name = u'学科门类'
	)
	code = models.CharField(
		max_length = 4,
		verbose_name = u'代码'
	)
	def __unicode__(self):
		return '%s (%s)' %(self.name, self.code)

class MyMajorSubcategory (models.Model):
	name = models.CharField(
		max_length = 16,
		default = '',
		verbose_name = u'专业类'
	)
	code = models.CharField(
		max_length = 4,
		verbose_name = u'代码'
	)
	category = models.ForeignKey (
			MyMajorCategory,
			null = True,
			blank = True,
			verbose_name = u'学科门类'
		)
	def __unicode__(self):
		return u'%s (%s)' %(self.name,self.code)

class MyMajor (MyBaseModel):
	DEGREE_TYPE_CHOICES = (
		('',''),
		(u'本科', u'本科'),
		(u'专科', u'专科'),
		(u'职业教育', u'职业教育'),
	)

	code = models.CharField (
			max_length = 16,
			default = '',
			verbose_name = u'专业代码',
		)
	subcategory = models.ForeignKey (
			MyMajorSubcategory,
			null = True,
			blank = True,
			verbose_name = u'专业类'
		)
	degree_type = models.CharField (
			max_length = 8,
			null = True,
			blank = True,
			verbose_name = u'教育类别',
			choices = DEGREE_TYPE_CHOICES
		)
	degree = models.CharField (
			null = True,
			blank = True,
			max_length = 32,
			verbose_name = u'授予学位'
		)
	how_long = models.CharField (
			null = True,
			blank = True,
			max_length = 16,
			verbose_name = u'修学年限'
		)
	course = models.TextField(
			null = True,
			blank = True,
			max_length = 8,
			verbose_name = u'修学年限'
		)
	is_specialized = models.BooleanField (
			default = False,
			verbose_name = u''
		)
	is_gov_controlled = models.BooleanField (
			default = False,
			verbose_name = u''
		)

	# related models
	schools = models.ManyToManyField ('MySchool')
	related_majors = models.ManyToManyField('MyMajor')

	def __unicode__(self):
		return '%s (%s)' % (self.name, self.code)

class MyAdmissionBySchool (models.Model):
	CATEGORY_CHOICES = (
		(u'文科',u'文科'), 
		(u'理科',u'理科'), 
		(u'综合',u'综合'), 
		(u'其他',u'其他'), 
	)
	
	school = models.ForeignKey (
			'MySchool',
			verbose_name = u'高校名称'
		)
	province = models.ForeignKey (
			MyAddress,
			verbose_name = u'招生地区'	
		)
	category = models.CharField (
			max_length = 8,
			choices = CATEGORY_CHOICES						
		)
	year = models.IntegerField ()
	batch = models.CharField (
			max_length = 16,
			verbose_name = u'录取批次'
		)
	min_score = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'最低分'
		)
	max_score = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'最高分'
		)
	avg_score = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'平均分'
		)
	province_score = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'省控分'
		)

class MyAdmissionByMajor (models.Model):
	CATEGORY_CHOICES = (
		(u'文科',u'文科'), 
		(u'理科',u'理科'), 
		(u'综合',u'综合'), 
		(u'其他',u'其他'), 
	)
	
	school = models.ForeignKey (
			'MySchool',
			verbose_name = u'高校名称'
		)
	major = models.ForeignKey (
			MyMajor,
			verbose_name = u'专业名称'
		)
	province = models.ForeignKey (
			MyAddress,
			verbose_name = u'招生地区'	
		)
	category = models.CharField (
			max_length = 8,
			choices = CATEGORY_CHOICES						
		)
	year = models.IntegerField ()
	batch = models.CharField (
			max_length = 16,
			verbose_name = u'录取批次'
		)
	max_score = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'最高分'
		)
	avg_score = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'平均分'
		)

class MySchool (MyBaseModel):
	raw_page = models.TextField (
		null = True,
		blank = True,
		verbose_name = u'原始html data. Research used ONLY!'
	)
	en_name = models.CharField (
			max_length = 256,
			null = True,
			blank = True,
			verbose_name = u'英文名'
		)
	founded = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'创建时间'
		)
	school_type = models.CharField (
			max_length = 16,
			null=True, 
			blank=True,
			verbose_name = u'学校类型'
		)
	no_key_major = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'重点学科数目'
		)
	no_fellow = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'院士人数'
		)
	no_student = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'学生人数'
		)
	no_phd_program = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'博士点个数'
		)
	no_master_program = models.IntegerField (
			null=True, 
			blank=True,
			verbose_name = u'硕士点个数'
		)
