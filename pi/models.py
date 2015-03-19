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
from annoying.fields import JSONField # django-annoying
from django.db.models import Q
from datetime import datetime as dt

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
			blank = True,
			null = True,
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
	source_url = models.URLField(
			max_length=512,
			verbose_name = u'File origin url'
		)

	file = models.FileField (
			upload_to = '%Y/%m/%d',
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
	province_en = models.CharField (
			max_length = 32,
			verbose_name = u'in English'
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
			verbose_name = u'专业课程'
		)
	is_specialized = models.BooleanField (
			default = False,
			verbose_name = u'特设专业'
		)
	is_gov_controlled = models.BooleanField (
			default = False,
			verbose_name = u'国家控制布点专业'
		)
	student_type = models.CharField (
			max_length = 8,
			null = True,
			blank = True,
			verbose_name = u'文理科',
		)
	# related models
	schools = models.ManyToManyField ('MySchool')
	related_majors = models.ManyToManyField('MyMajor')

	def __unicode__(self):
		return self.name

class MyAdmissionBySchoolCustomManager(models.Manager):
	def filter_by_user_profile_and_school(self,user,school_id):
		data = self.get_queryset().filter(school=school_id)

		# get user profile
		user_profile,created = MyUserProfile.objects.get_or_create(owner = user)
		if created: return data

		# filter based on user profile
		province = user_profile.province
		student_type = user_profile.student_type
		estimated_score = user_profile.estimated_score
		degree_type = user_profile.degree_type

		# filter by user profile location
		if province: data = data.filter(province=province)
		if student_type: data = data.filter(category = student_type)
		if degree_type == u'本科': data=data.filter(school__take_bachelor=True)
		if degree_type == u'专科': data=data.filter(school__take_associate=True)

		# for scores, we set up a band around estimated_score
		SCORE_BAND=25
		if estimated_score: 
			data = data.filter(Q(min_score__lte = estimated_score+SCORE_BAND) & Q(min_score__gte=estimated_score-SCORE_BAND))
		return data

class MyAdmissionBySchool (models.Model):
	CATEGORY_CHOICES = (
		('',''),		
		(u'文科',u'文科'), 
		(u'理科',u'理科'), 
		(u'综合',u'综合'), 
		(u'其他',u'其他'), 
	)
	objects=MyAdmissionBySchoolCustomManager()
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
		('',''),		
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

from shapely.geometry import box as Box
from shapely.geometry import Point
class MySchoolCustomManager(models.Manager):
	def get_queryset(self):
		'''
			Only school with province is visible (and useful), ever!
		'''
		return super(MySchoolCustomManager, self).get_queryset().filter(province__isnull=False)

	def visible(self,bound):
		filtered_objs = []

		# return objects whose geocode is within given bound
		sw_lat,sw_lng,ne_lat,ne_lng = bound
		bound = Box(sw_lat, sw_lng,ne_lat,ne_lng)

		# filter schools for the ones that are visible at current Zoom level and viewport
		for s in [x for x in self.get_queryset().order_by('province')]:
			# we are iterating all geocode in DB
			# TODO: some geocode are not correct. We need to clean that data.
			# for g in filter(lambda x: x.has_key('geometry'), s.google_geocode):
			#	lat,lng = float(g[u'geometry'][u'location'][u'lat']), float(g[u'geometry'][u'location'][u'lng'])
			if bound.contains(Point(s.lat,s.lng)) and s not in filtered_objs: filtered_objs.append(s)
		return filtered_objs

	def bachelors(self):
		return self.get_queryset().filter(take_bachelor=True)

	def associates(self):
		return self.get_queryset().filter(take_associate=True)

	def bachelor_and_associate(self):
		return self.get_queryset().filter(take_bachelor=True,take_associate=True)

	def pres(self):
		return self.get_queryset().filter(take_pre=True)

	def filter_by_user_profile(self,user):
		data = self.get_queryset()

		# get user profile
		user_profile,created = MyUserProfile.objects.get_or_create(owner = user)
		if created: return data

		# filter based on user profile
		province = user_profile.province
		student_type = user_profile.student_type
		estimated_score = user_profile.estimated_score
		degree_type = user_profile.degree_type

		# filter by user profile location
		if province: data = data.filter(accepting_province=province)

		if degree_type == u'本科': data = data.filter(take_bachelor=True)
		elif degree_type == u'专科': data = data.filter(take_associate=True)

		# for scores, we set up a band around estimated_score
		SCORE_BAND=25
		school_ids = []
		if estimated_score and province and student_type:
			school_ids = MyAdmissionBySchool.objects.filter(
				Q(school__in=data) & 
				Q(min_score__lte = estimated_score+SCORE_BAND) & 
				Q(min_score__gte=estimated_score-SCORE_BAND) &
				Q(province=province) &
				Q(category=student_type)).values_list('school',flat=True)
		elif estimated_score and province:
			school_ids = MyAdmissionBySchool.objects.filter(
				Q(school__in=data) & 
				Q(min_score__lte = estimated_score+SCORE_BAND) & 
				Q(min_score__gte=estimated_score-SCORE_BAND) &
				Q(province=province)).values_list('school',flat=True)
		elif estimated_score and student_type:
			school_ids = MyAdmissionBySchool.objects.filter(
				Q(school__in=data) & 
				Q(min_score__lte = estimated_score+SCORE_BAND) & 
				Q(min_score__gte=estimated_score-SCORE_BAND) &
				Q(category=student_type)).values_list('school',flat=True)
		elif estimated_score:
			school_ids = MyAdmissionBySchool.objects.filter(
				Q(school__in=data) & 
				Q(min_score__lte = estimated_score+SCORE_BAND) & 
				Q(min_score__gte=estimated_score-SCORE_BAND)).values_list('school',flat=True)			
		data = data.filter(id__in=school_ids)

		return data

class MySchool (MyBaseModel):
	# custom managers
	# Note: the 1st one defined will be taken as the default!
	objects = MySchoolCustomManager()

	def __unicode__(self):
		return self.name

	google_placeid = models.CharField (
		max_length = 64,
		null = True,
		blank = True,
		default = '',
		verbose_name = u'Google geocoding place id'
	)
	raw_page = models.TextField (
		null = True,
		blank = True,
		verbose_name = u'原始html data. Research used ONLY!'
	)
	admission_office_phone = models.CharField(
			max_length=64,
			null = True,
			blank = True,
			default = '',
			verbose_name = u'招生电话'
		)
	admission_office_email = models.EmailField(
			null = True,
			blank = True,
			default = '',
			verbose_name = u'招生电子邮箱'
		)	
	address = models.CharField (
			max_length=256,
			null = True,
			blank = True,
			default = '',
			verbose_name = u'学校地址'
		)
	lat = models.DecimalField (
			max_digits = 20,
			decimal_places = 15,
			null = True,
			blank = True,
			default = 0,
			verbose_name = u'Address lat'
		)
	lng = models.DecimalField (
			max_digits = 20,
			decimal_places = 15,
			null = True,
			blank = True,
			default = 0,
			verbose_name = u'Address lng'
		)	
	province = models.ForeignKey (
			'MyAddress',
			null = True,
			blank = True,
			verbose_name = u'所处省'			
		)
	city = models.CharField (
			max_length=64,
			null = True,
			blank = True,
			default = '',
			verbose_name = u'所处城市'			
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
	formatted_address_en = models.CharField (
			max_length = 256,
			null=True,
			blank=True,
			verbose_name = u'Google geocode address'
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

	take_bachelor = models.NullBooleanField(
			null=True, 
			blank=True,
			default=False,
			verbose_name = u'招收本科生'		
		)
	take_associate = models.NullBooleanField(
			null=True, 
			blank=True,
			default=False,
			verbose_name = u'招收专科生'		
		)
	take_pre = models.NullBooleanField(
			null=True, 
			blank=True,
			default=False,
			verbose_name = u'提前招生'		
		)
	take_1st_batch = models.NullBooleanField(
			null=True, 
			blank=True,
			default=False,
			verbose_name = u'招收本科一批'		
		)
	take_2nd_batch = models.NullBooleanField(
			null=True, 
			blank=True,
			default=False,
			verbose_name = u'招收本科二批'		
		)
	take_3rd_batch = models.NullBooleanField(
			null=True, 
			blank=True,
			default=False,
			verbose_name = u'招收本科三批'		
		)
	accepting_province=models.ManyToManyField(
			'MyAddress',
			related_name='accepting_schools',
			verbose_name=u'招生学校'
		)

class MyUserProfile(models.Model):
	DEGREE_TYPE_CHOICES = (
		('',''),
		(u'本科', u'本科'),
		(u'专科', u'专科'),
	)	
	STUDENT_TYPE_CHOICES = (
		('',''),
		(u'文科', u'文科'),
		(u'理科', u'理科'),
	)	
	owner = models.OneToOneField (
			User,
			default = None,
			verbose_name = u'用户',
			help_text = ''
		)
	province = models.ForeignKey (
			'MyAddress',
			null = True,
			blank = True,
			verbose_name = u'入考省份',
		)
	estimated_score = models.IntegerField(
			default = -1, # -1 means no filter applied based on score
			verbose_name = u'分数',		
		)
	student_type = models.CharField(
			max_length = 8,
			null = True,
			blank = True,
			verbose_name = u'考生类别',
			choices = STUDENT_TYPE_CHOICES		
		)
	degree_type = models.CharField(
			max_length = 8,
			null = True,
			blank = True,
			verbose_name = u'学位类别',
			choices = DEGREE_TYPE_CHOICES		
		)

class MyCrawlerRequest(models.Model):
	'''
		Internal used ONLY! 
		Should be replaced by a queue system on the background later.
	'''
	DATA_SOURCE_CHOICES	=(
		(1, u'百度贴吧'),
		(2, u'新浪微博'),
		)
	created = models.DateTimeField(
		auto_now_add=True,
		verbose_name=u'Using crawler machine timestamp'
		)	
	source = models.IntegerField(
			verbose_name = u'数据源',
			choices = DATA_SOURCE_CHOICES
		)
	params = JSONField (
			verbose_name = u'数据参数'
		)

class MyBaiduStream(MyBaseModel):
	school = models.ForeignKey(
		MySchool,
		verbose_name=u'所属学校'
		)
	created = models.DateTimeField(
		auto_now_add=True,
		verbose_name=u'Using crawler machine timestamp'
		)
	author = models.CharField(
		max_length=64,
		verbose_name = u'作者'
		)
	reply_num = models.IntegerField(
		verbose_name = u'回复数'
		)
	url_original = models.URLField(
		default = '',
		verbose_name = u'Data source original link'
		)
	last_updated = models.DateTimeField(
		blank = True,
		null = True,
		verbose_name = u'Posted timestamp read from the source site'
		)

	def _age(self):
		'''
			Calculate object age based on NOW and its creation timestamp
		'''
		return (dt.now()-self.created).total_seconds()
	age = property(_age)
