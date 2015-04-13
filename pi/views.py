#!/usr/bin/python  
# -*- coding: utf-8 -*-  

from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, logout, login
from django.template import RequestContext
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count,Max,Min,Avg

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.vary import vary_on_headers
# protect the view with require_POST decorator
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q

# map geometry lib
from shapely.geometry import box as Box
from shapely.geometry import Point
from django.template import loader, Context

# django-crispy-forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# django-filters
from django_filters import FilterSet, BooleanFilter
from django_filters.views import FilterView
import django_filters

# so what
import re,os,os.path,shutil,subprocess, testtools
import random,codecs,unittest,time, tempfile, csv, hashlib
from datetime import datetime as dt
from multiprocessing import Process, Queue
import simplejson as json
import googlemaps
from itertools import groupby
import urllib, lxml.html
from utility import MyUtility

from pi.models import *

###################################################
#
#	Common utilities
#
###################################################
def class_view_decorator(function_decorator):
	"""Convert a function based decorator into a class based decorator usable
	on class based Views.
	
	Can't subclass the `View` as it breaks inheritance (super in particular),
	so we monkey-patch instead.
	"""
	
	def simple_decorator(View):
		View.dispatch = method_decorator(function_decorator)(View.dispatch)
		return View
	
	return simple_decorator

###################################################
#
#	Static views
#
###################################################
class HomeView (TemplateView):
	template_name = 'pi/common/home_with_login_modal.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)

		user_auth_form = AuthenticationForm()
		user_registration_form = UserCreationForm()

		context['registration_form']=user_registration_form
		context['auth_form']=user_auth_form
		return context

###################################################
#
#	User views
#
###################################################
class LoginView(FormView):
	template_name = 'registration/login.html'
	success_url = reverse_lazy('school_rank', kwargs={'rank': 10})
	form_class = AuthenticationForm
	def form_valid(self,form):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user = authenticate(username=username, password=password)

		if user is not None and user.is_active:
		    login(self.request, user)
		    return super(LoginView, self).form_valid(form)
		else:
		    return self.form_invalid(form)

class LogoutView(TemplateView):
	template_name = 'registration/logged_out.html'
	def get(self,request):
		logout(request)
    	# Redirect to a success page.
		# messages.add_message(request, messages.INFO, 'Thank you for using our service. Hope to see you soon!')
		return HttpResponseRedirect (reverse_lazy('home'))

class UserRegisterView(FormView):
	template_name = 'registration/register_form.html'
	form_class = UserCreationForm
	success_url = reverse_lazy('login')
	def form_valid(self,form):
		user_name = form.cleaned_data['username']
		password = form.cleaned_data['password2']
		if len(User.objects.filter(username = user_name))>0:
			return self.form_invalid(form)
		else:
			user = User.objects.create_user(user_name, '', password)			
			user.save()

			return super(UserRegisterView,self).form_valid(form)

class UserProfileView(TemplateView):
	template_name='pi/user/profile.html'
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			user_profile,created = MyUserProfile.objects.get_or_create(owner=self.request.user)
			context['schools']=user_profile.school_bookmarks.all()
		else: context['schools'] = []
		return context

	def post(self,request):
		province = request.POST['province'].strip()
		student_type = request.POST['student_type'].strip()
		score = request.POST['score'].strip()
		degree_type = request.POST['degree_type'].strip()
		tags = request.POST['tags'].strip()

		# get user property obj
		user_profile,created = MyUserProfile.objects.get_or_create(owner=request.user)

		if not province: user_profile.province=None
		else:
			for p in MyProvince.objects.all():
				if p.province in province: 
					user_profile.province = p
					city = province.replace(p.province,'')
					if city: city_obj = MyCity.objects.filter(city = city, province=p)
					else: city_obj = MyCity.objects.filter(city = p.province, province=p)

					if city_obj: user_profile.city = city_obj[0]
					break

		if student_type: user_profile.student_type = student_type
		if score: user_profile.estimated_score = int(score)
		if degree_type: user_profile.degree_type = degree_type
		user_profile.save()

		# add tags
		user_profile.tags.all().delete()
		if tags:
			# MONEY: limit 10 tags per user
			for t in tags.replace(u'，',',').split(',')[:10]:
				if not t.strip(): continue
				tagged_item,created = MyTaggedItem.objects.get_or_create(tag=t[:16])
				# link to related majors
				MyMajor.objects.link_tag(tagged_item)

				# add to associated user profile
				user_profile.tags.add(tagged_item)

		# refresh current page, whatever it is.
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

@class_view_decorator(login_required)
class UserBookmark(TemplateView):
	template_name = 'pi/user/bookmark.html'
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		user_profile,created = MyUserProfile.objects.get_or_create(owner=self.request.user)
		context['schools']=user_profile.school_bookmarks.all()
		return context	

	def post(self,request):
		obj_id = request.POST['obj_id']
		school = MySchool.objects.get(id=int(obj_id))

		# get user property obj
		user_profile,created = MyUserProfile.objects.get_or_create(owner=request.user)

		if request.POST['action'] == '1': # toogle bookmark
			if school in user_profile.school_bookmarks.all(): user_profile.school_bookmarks.remove(school)
			else: user_profile.school_bookmarks.add(school)
			user_profile.school_xouts.remove(school)
		elif request.POST['action'] == '2': # toggle x-out
			user_profile.school_bookmarks.remove(school)
			if school in user_profile.school_xouts.all(): user_profile.school_xouts.remove(school)
			else: user_profile.school_xouts.add(school)			
		elif request.POST['action'] == '3': # add to x-out
			user_profile.school_bookmarks.remove(school)
			user_profile.school_xouts.add(school)
		elif request.POST['action'] == '4': # add to bookmark
			user_profile.school_bookmarks.add(school)
			user_profile.school_xouts.remove(school)			

		return HttpResponse(json.dumps({'status':'ok'}), 
			content_type='application/javascript')

@class_view_decorator(login_required)
class UserTagsDelete(TemplateView):
	template_name = ''
	def post(self,request):
		'''
			Remove tags
		'''
		obj_id = request.POST['obj_id']

		# get user property obj
		user_profile,created = MyUserProfile.objects.get_or_create(owner=request.user)
		user_profile.tags.remove(MyTaggedItem.objects.get(id=obj_id))
		# refresh current page, whatever it is.
		return HttpResponse(json.dumps({'status':'ok'}), 
			content_type='application/javascript')	

###################################################
#
#	Data import views
#
###################################################
class ImportGeneralUploadForm (forms.Form):
	myfile = forms.FileField(
			label = u'选择文件',
			help_text = u''	
		)

@login_required
def import_admission_by_school (request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = ImportGeneralUploadForm(request.POST, request.FILES)
		# check whether it's valid:
		if form.is_valid():
			content = request.FILES['myfile'].read().split('\n')
			MyCrawler().admission_by_school_persist([[a.decode('UTF-8') for a in c.split('\t')] for c in content])
			return HttpResponseRedirect(reverse_lazy('admission_school_list'))
						
	# if a GET (or any other method) we'll create a blank form
	else: 
		form = ImportGeneralUploadForm()
		content = ''
		return render(request, 'pi/import/upload.html', {'form': form})

@login_required
def import_admission_by_major (request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = ImportGeneralUploadForm(request.POST, request.FILES)
		# check whether it's valid:
		if form.is_valid():
			content = request.FILES['myfile'].read().split('\n')
			MyCrawler().admission_by_major_persist([[a.decode('UTF-8') for a in c.split('\t')] for c in content])
			return HttpResponseRedirect(reverse_lazy('admission_major_list'))
						
	# if a GET (or any other method) we'll create a blank form
	else: 
		form = ImportGeneralUploadForm()
		content = ''
		return render(request, 'pi/import/upload.html', {'form': form})			

###################################################
#
#	MyAdmissionBySchool views
#
###################################################
class MyAdmissionBySchoolListFilter (FilterSet):
	class Meta:
		model = MyAdmissionBySchool
		fields = {'school__name':['contains'],
				'province':['exact'],
				'category':['contains'],
				'year':['exact'],
				'batch':['contains'],				
				}

@class_view_decorator(login_required)
class MyAdmissionBySchoolList (FilterView):
	template_name = 'pi/admission/school_list.html'
	paginate_by = 10
	
	def get_filterset_class(self):
		return MyAdmissionBySchoolListFilter	

@class_view_decorator(login_required)
class MyAdmissionBySchoolAdd (CreateView):
	model = MyAdmissionBySchool
	template_name = 'pi/common/add_form.html'
	success_url = reverse_lazy('admission_school_list')
	
	def form_valid(self, form):
		form.instance.created_by = self.request.user
		return super(MyAdmissionBySchoolAdd, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(MyAdmissionBySchoolAdd, self).get_context_data(**kwargs)
		context['title'] = u'新建fenshuxian(admission)'
		context['list_url'] = reverse_lazy('admission_school_list')
		return context

@class_view_decorator(login_required)
class MyAdmissionBySchoolEdit (UpdateView):
	model = MyAdmissionBySchool
	template_name = 'pi/common/edit_form.html'
	
	def get_success_url(self):
		return reverse_lazy('admission_detail', kwargs={'pk':self.get_object().id})
			
	def get_context_data(self, **kwargs):
		context = super(MyAdmissionBySchoolEdit, self).get_context_data(**kwargs)
		context['title'] = u'编辑fenshuxian(admission)'
		context['list_url'] = reverse_lazy('admission_school_list')
		return context

@class_view_decorator(login_required)
class MyAdmissionBySchoolDelete (DeleteView):
	model = MyAdmissionBySchool
	template_name = 'pi/common/delete_form.html'
	success_url = reverse_lazy('admission_school_list')

	def get_context_data(self, **kwargs):
		context = super(MyAdmissionBySchoolDelete, self).get_context_data(**kwargs)
		context['title'] = u'删除fenshuxian(admission)'
		context['list_url'] = reverse_lazy('admission_school_list')
		return context

###################################################
#
#	MyAdmissionByMajor views
#
###################################################
from django_filters import CharFilter
class MyAdmissionByMajorListFilter (FilterSet):
	major=CharFilter(name='major__name',label="Majors")
	class Meta:
		model = MyAdmissionByMajor
		fields = {'school__name':['contains'],
				'province':['exact'],
				'category':['contains'],
				'year':['exact'],
				'major__name':['contains'],
				'batch':['contains'],								
				}

@class_view_decorator(login_required)
class MyAdmissionByMajorList (FilterView):
	template_name = 'pi/admission/major_list.html'
	paginate_by = 10
	
	def get_filterset_class(self):
		return MyAdmissionByMajorListFilter	

@class_view_decorator(login_required)
class MyAdmissionByMajorAdd (CreateView):
	model = MyAdmissionByMajor
	template_name = 'pi/common/add_form.html'
	success_url = reverse_lazy('admission_major_list')
	
	def form_valid(self, form):
		form.instance.created_by = self.request.user
		return super(MyAdmissionByMajorAdd, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(MyAdmissionByMajorAdd, self).get_context_data(**kwargs)
		context['title'] = u'新建fenshuxian(admission)'
		context['list_url'] = reverse_lazy('admission_major_list')
		return context

@class_view_decorator(login_required)
class MyAdmissionByMajorEdit (UpdateView):
	model = MyAdmissionByMajor
	template_name = 'pi/common/edit_form.html'
	
	def get_success_url(self):
		return reverse_lazy('admission_detail', kwargs={'pk':self.get_object().id})
			
	def get_context_data(self, **kwargs):
		context = super(MyAdmissionByMajorEdit, self).get_context_data(**kwargs)
		context['title'] = u'编辑fenshuxian(admission)'
		context['list_url'] = reverse_lazy('admission_major_list')
		return context

@class_view_decorator(login_required)
class MyAdmissionByMajorDelete (DeleteView):
	model = MyAdmissionByMajor
	template_name = 'pi/common/delete_form.html'
	success_url = reverse_lazy('admission_major_list')

	def get_context_data(self, **kwargs):
		context = super(MyAdmissionByMajorDelete, self).get_context_data(**kwargs)
		context['title'] = u'删除fenshuxian(admission)'
		context['list_url'] = reverse_lazy('admission_major_list')
		return context

###################################################
#
#	MyMajor views
#
###################################################
class MyMajorListFilter (FilterSet):
	class Meta:
		model = MyMajor
		fields = {
				'code':['contains'],		
				'name':['contains'],
				'subcategory':['exact'],
				'degree_type':['contains'],
				'degree':['contains'],
				'course':['contains'],
				}

class MyMajorList (FilterView):
	template_name = 'pi/major/list.html'
	paginate_by = 10
	
	def get_filterset_class(self):
		return MyMajorListFilter	

@class_view_decorator(login_required)
class MyMajorAdd (CreateView):
	model = MyMajor
	template_name = 'pi/common/add_form.html'
	success_url = reverse_lazy('major_list')
	
	def form_valid(self, form):
		form.instance.created_by = self.request.user
		return super(MyMajorAdd, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(MyMajorAdd, self).get_context_data(**kwargs)
		context['title'] = u'新建 Major'
		context['list_url'] = reverse_lazy('major_list')
		return context

@class_view_decorator(login_required)
class MyMajorEdit (UpdateView):
	model = MyMajor
	template_name = 'pi/common/edit_form.html'
	
	def get_success_url(self):
		return reverse_lazy('major_detail', kwargs={'pk':self.get_object().id})
			
	def get_context_data(self, **kwargs):
		context = super(MyMajorEdit, self).get_context_data(**kwargs)
		context['title'] = u'编辑 Major'
		context['list_url'] = reverse_lazy('major_list')
		return context

@class_view_decorator(login_required)
class MyMajorDelete (DeleteView):
	model = MyMajor
	template_name = 'pi/common/delete_form.html'
	success_url = reverse_lazy('major_list')

	def get_context_data(self, **kwargs):
		context = super(MyMajorDelete, self).get_context_data(**kwargs)
		context['title'] = u'删除 Major'
		context['list_url'] = reverse_lazy('major_list')
		return context

@class_view_decorator(login_required)
class MyMajorDetail(DetailView):
	model = MyMajor
	template_name = 'pi/major/detail.html'
	def get_context_data(self, **kwargs):
		context = super(DetailView, self).get_context_data(**kwargs)
		jobs = self.get_object().jobs.all().order_by('-created')[:50]

		context['jobs'] = jobs

		pynlpir.open() # must have this line!
		keywords = ','.join([''.join([j.title,j.location,j.req_degree]) for j in jobs])
		context['keywords']= pynlpir.get_key_words(keywords, max_words=25, weighted=True)
		pynlpir.close()


		return context
	def post(self,request,pk):
		# all related schools
		related_schools = self.get_object().schools.all()

		# filtered by user profile
		related_schools = MySchool.objects.filter_by_user_profile(self.request.user).filter(id__in =[s.id for s in related_schools])

		# client request
		draw = int(request.POST['draw'])
		start = int(request.POST['start'])
		length = int(request.POST['length'])
		search_value = request.POST['search[value]']

		for val in search_value.split(','):
			related_schools = related_schools.filter(Q(city__icontains=val) | Q(name__icontains=val))

		result = {
		"draw": draw,
		"recordsTotal": len(related_schools),
		"recordsFiltered": len(related_schools),
		"data":	[[s.city, s.name] for s in related_schools[start:start+length]]
		}
		# return to client
		return HttpResponse(json.dumps(result), content_type='application/javascript')			

class MyMajorSchoolDetail(TemplateView):
	template_name = 'pi/major/school_detail.html'
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		user_profile = MyUserProfile.objects.get(owner=self.request.user)
		school = MySchool.objects.get(id=int(kwargs['school_pk']))
		major = MyMajor.objects.get(id=int(kwargs['major_pk']))
		major_admissions = MyAdmissionByMajor.objects.filter(school=school,major=major).order_by('-year','province')

		context['school']=school
		context['major']=major
		context['admissions']=major_admissions
		context['other_majors'] = filter(lambda x: x.degree_type == user_profile.degree_type,school.majors.all())

		return context

class MyMajorRelatedSchools(TemplateView):
	template_name = 'pi/major/related_schools.html'
	def post(self,request):
		major = MyMajor.objects.get(id=int(request.POST['obj_id']))
		filtered_by_profile = int(request.POST['profiled'])

		# all related schools
		related_schools = major.schools.all()

		# filtered by user profile
		if filtered_by_profile: related_schools = MySchool.objects.filter_by_user_profile(self.request.user).filter(id__in =[s.id for s in related_schools]).order_by('province','city')
		else: related_schools = MySchool.objects.filter(id__in =[s.id for s in related_schools]).order_by('province','city')

		content = loader.get_template(self.template_name)
		html= content.render(Context({'objs':related_schools}))

		return HttpResponse(json.dumps({'html':html}), 
			content_type='application/javascript')

from django.db.models import Count
@class_view_decorator(login_required)
class MyMajorRank(TemplateView):
	template_name = 'pi/major/rank.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)		
		top_count = int(context['rank'])
		context['ranks'] = MyMajor.objects.exclude(Q(code__isnull=True) | Q(code__exact='')).order_by('-job_stat')[:top_count]
		return context

###################################################
#
#	MySchool views
#
###################################################
class MySchoolListFilter (FilterSet):
	class Meta:
		model = MySchool
		fields = {
				'name':['contains'],
				'province':['exact'],
				'city':['contains'],
				'take_bachelor':['exact'],
				}

class MySchoolList (FilterView):
	template_name = 'pi/school/list.html'
	paginate_by = 10
	
	def get_filterset_class(self):
		return MySchoolListFilter

@class_view_decorator(login_required)
class MySchoolAdd (CreateView):
	model = MySchool
	template_name = 'pi/common/add_form.html'
	success_url = reverse_lazy('school_list')
	
	def form_valid(self, form):
		form.instance.created_by = self.request.user
		return super(MyMajorAdd, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(MyMajorAdd, self).get_context_data(**kwargs)
		context['title'] = u'新建 School'
		context['list_url'] = reverse_lazy('school_list')
		return context

@class_view_decorator(login_required)
class MySchoolEdit (UpdateView):
	model = MySchool
	template_name = 'pi/common/edit_form.html'
	
	def get_success_url(self):
		return reverse_lazy('school_detail', kwargs={'pk':self.get_object().id})
			
	def get_context_data(self, **kwargs):
		context = super(MySchoolEdit, self).get_context_data(**kwargs)
		context['title'] = u'编辑 School'
		context['list_url'] = reverse_lazy('school_list')
		return context

@class_view_decorator(login_required)
class MySchoolDelete (DeleteView):
	model = MySchool
	template_name = 'pi/common/delete_form.html'
	success_url = reverse_lazy('school_list')

	def get_context_data(self, **kwargs):
		context = super(MySchoolDelete, self).get_context_data(**kwargs)
		context['title'] = u'删除 School'
		context['list_url'] = reverse_lazy('school_list')
		return context

@class_view_decorator(login_required)
class MySchoolDetail(DetailView):
	model = MySchool
	template_name = 'pi/school/detail.html'

	def get_context_data(self, **kwargs):
		context = super(MySchoolDetail, self).get_context_data(**kwargs)
		context['list_url'] = reverse_lazy('school_list')
		school = self.get_object()
		user_profile=MyUserProfile.objects.get(owner=self.request.user)

		# related list
		my_rank = MyRank.objects.select_related().get(rank_index=-1,school=school)

		# TODO: this is an expansive query. Adding "rank" column to DB index would help
		city = self.get_object().city
		tmp = MyRank.objects.filter(school__city = city).filter(rank_index=-1,rank__gte=(my_rank.rank-50),rank__lte=(my_rank.rank+50))
		context['related_schools']=[a for a in reversed(sorted(tmp,lambda x,y:cmp(x.rank,y.rank)))]

		# admission history
		school_admission = MyAdmissionBySchool.objects.filter_by_user_profile_and_school(self.request.user, school.id)
		school_admission_by_year = {}
		for year,admission_by_year_list in groupby(school_admission,lambda x:x.year):
			school_admission_by_year[year]=sorted(list(admission_by_year_list),lambda x,y:cmp(x.category,y.category))
		context['school_admission_by_year']=school_admission_by_year

		# school majors
		context['majors'] = filter(lambda x: x.degree_type == user_profile.degree_type,self.get_object().majors.all())

		# weixin accounts
		context['weixins'] = MyWeixinAccount.objects.filter(school=school)
		
		return context

@class_view_decorator(login_required)
class MySchoolMapDetail(TemplateView):
	'''
		AJAX post view
	'''
	template_name = 'pi/school/gmap_detail.html'

	def post(self,request):
		obj_id = request.POST['obj_id']
		school = MySchool.objects.get(id=int(obj_id))
		content = loader.get_template(self.template_name)
		html= content.render(Context({'obj':school}))

		return HttpResponse(json.dumps({'html':html}), 
			content_type='application/javascript')	

from itertools import groupby
class MySchoolEchartMapFilter(TemplateView):
	template_name = 'pi/school/emap.html'
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)

		# echart data, group by province
		result = {}
		if self.request.user.is_authenticated():
			schools = MySchool.objects.filter_by_user_profile(self.request.user).values('id','name','province__id','province__province','city__city')
			echart_data = MySchool.objects.filter_by_user_profile(self.request.user).values('province__province','province__id').annotate(count=Count('province__province'))			
		else: 
			# this is when browsing anonymously
			schools = MySchool.objects.values('id','name','province__id','province__province','city__city')
			echart_data = MySchool.objects.values('province__province','province__id').annotate(count=Count('province__province'))			

		context['schools'] =  schools.order_by('province__id','city__city')
		context['provinces'] = MyProvince.objects.all()
		
		# echart data
		context['echart_data'] = echart_data
		try: context['echart_data_min'] = min([a['count'] for a in echart_data])
		except: context['echart_data_min'] = 0
		try: context['echart_data_max'] = max([a['count'] for a in echart_data])
		except: context['echart_data_max'] = 0

		return context

@class_view_decorator(login_required)
class MySchoolRank(TemplateView):
	template_name = 'pi/school/rank.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)		
		top_count = int(context['rank'])
		schools = MySchool.objects.filter_by_user_profile(self.request.user)

		# related majors
		user_profile = MyUserProfile.objects.get(owner=self.request.user)
		tags_related_majors = [major for tag in user_profile.tags.all() for major in tag.mymajor_set.all()]

		# this is how we measure a TOP 10!
		context['ranks'] = MyRank.objects.filter(rank_index=-1,school__in=schools).order_by('-rank')[:top_count]
		return context

@class_view_decorator(login_required)
class MySchoolMajorsFilterByTags(TemplateView):
	'''
		AJAX post view
	'''	
	template_name = 'pi/school/majors_filter_by_tags.html'
	def post(self,request):		
		# user profile and profile tags to get tag linked majors
		user_profile = MyUserProfile.objects.get(owner=self.request.user)
		rank = MyRank.objects.get(id=int(request.POST['obj_id']))		
		
		if user_profile.tags.all():
			tags_related_majors = [major for tag in user_profile.tags.all() for major in tag.mymajor_set.all()]
			related_majors = set(tags_related_majors).intersection(rank.school.majors.all())
		else: related_majors = rank.school.majors.all()

		content = loader.get_template(self.template_name)
		html= content.render(Context({'objs':related_majors}))

		return HttpResponse(json.dumps({'html':html}), 
			content_type='application/javascript')		

@class_view_decorator(login_required)
class MySchoolWeixin(TemplateView):
	template_name = 'pi/school/weixin.html'	
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		school = MySchool.objects.get(id=int(kwargs['pk']))
		context['object']=school
		context['objs'] = MyWeixinAccount.objects.filter(school=school)

		return context

###################################################
#
#	Googlemap views
#
###################################################
class MySchoolMapInfo (TemplateView):
	info_template_name = 'pi/school/gmap_info.html'
	def post(self,request):
		school = MySchool.objects.get(id=int(request.POST['obj_id']))
		info_win_template = loader.get_template(self.info_template_name)
		# infowin Context for html rendering
		c = Context({
			'user': request.user,
			'ip_address': request.META['REMOTE_ADDR'],
			'obj': school
		})
		# return to client
		return HttpResponse(json.dumps({ 
				'info_win_html': info_win_template.render(c)
			}), content_type='application/javascript')			

class MySchoolMapFilter (TemplateView):
	template_name = 'pi/school/gmap.html'
	visible_template_name = 'pi/school/gmap_visible_list.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)

		# TODO: center is now WuHan. Should be based on User's location
		context['center'] = {'lat':30.593099,'lng':114.305393}
		context['marker_url']=reverse('school_map_filter')
		context['detail_url']=reverse('school_map_detail')
		context['info_win_url']=reverse('school_map_info')
		return context

	def post(self, request):
		coords=request.POST # viewport bounds
		
		# based on filter criteria we conclude a list
		filtered_objs = MySchool.objects.visible((float(coords['sw.k']),float(coords['sw.D']), float(coords['ne.k']),float(coords['ne.D'])))

		markers = []
		visible_template = loader.get_template(self.visible_template_name)

		for s in filtered_objs:
			# Compose data array for client
			markers.append({
					'lat': s.lat,
					'lng': s.lng,	

					# custom data					
					'hash': s.hash,
					'obj_id':s.id,
					'name':s.name,
					'edit': reverse('school_edit',args = [s.id]),
				})

		# Write list html
		# sort is important for using template groupby function
		visible_html = visible_template.render(Context({'objs':filtered_objs, 'total':len(filtered_objs)}))
		
		# return to client
		return HttpResponse(json.dumps({
				'markers':markers, 
				'marker_list_html':visible_html,
				}), content_type='application/javascript')

###################################################
#
#	Analysis views
#
###################################################
class CategorizeSchoolHelper:
	'''
		This is a helper class.
	'''
	def __init__(self,post_data,user):
		'''
			Based on request.POST to compose a filter that can be used by self.get_objects
			param: request.POST, JSON data
		'''
		self.filters = {key:post_data[key] for key in post_data}

		# reverse json loads
		try:
			self.filters['cats']=json.loads(self.filters['cats'])
		except: self.filters['cats']=None

		# request user
		self.filters['user']=user

		self.schools = None

	def get_objects(self):
		# set up filters
		province = self.filters.get('province')
		city = self.filters.get('city')
		school_type = self.filters.get('school_type')
		batch = self.filters.get('batch')
		
		# filter by province
		schools = MySchool.objects.filter(province=province)

		# filter by city
		if city: schools = schools.filter(city=city)

		# filter by school_type
		if school_type: schools=schools.filter(school_type = school_type)

		self.schools=schools
		return schools

	def categorize_schools(self):
		'''
			Group schools into aggregated groups for analysis.
			param: schools
		'''
		self.schools = self.get_objects()
		return {
				u'本科':self.schools.filter(take_bachelor=True),
				u'专科':self.schools.filter(take_associate=True),
				u'既有本科也有专科':self.schools.filter(take_bachelor=True,take_associate=True),
				u'提前招生':self.schools.	filter(take_pre=True)		
			}

class AnalysisSchoolSummaryAJAX(TemplateView):
	summary_template_name = 'pi/analysis/schools_by_province_summary.html'

	def post(self,request):
		helper = CategorizeSchoolHelper(request.POST,request.user)
		categories = helper.categorize_schools()

		# available vs. active
		available_cats = categories.keys()		
		active_cats = helper.filters['cats'] or available_cats

		# render summary html
		summary = loader.get_template(self.summary_template_name)
		my_context = Context({
			'p_id':helper.filters['province'],
			'schools':helper.schools,
			'categories': categories,
			'available_cats':available_cats,
			'active_cats':active_cats
			})
		html= summary.render(my_context)
		return HttpResponse(json.dumps({'html':html}), 
			content_type='application/javascript')	

class AnalysisSchoolDetailAJAX(TemplateView):
	detail_template_name = 'pi/analysis/schools_detail.html'
	def post(self,request):
		helper = CategorizeSchoolHelper(request.POST,request.user)
		categories = helper.categorize_schools()

		# details per section
		detail = loader.get_template(self.detail_template_name)
		html=''
		for cat in helper.filters['cats']:
			objs = categories[cat.strip()]
			tmp = MyAdmissionBySchool.objects.filter(school__in=objs).values_list('max_score',flat=True)
			try: 
				max_score = max(tmp)
				max_score = MyAdmissionBySchool.objects.filter(school__in=objs).filter(max_score = max_score)[0]
			except: max_score=None

			tmp = MyAdmissionBySchool.objects.filter(school__in=objs).values_list('min_score',flat=True)
			try: 
				min_score = min(tmp)
				min_score = MyAdmissionBySchool.objects.filter(school__in=objs).filter(min_score = min_score)[0]
			except: min_score = None
						
			my_context=Context({
				'subject':cat.strip(),
				'objs':objs,
				'max_score':max_score,
				'min_score':min_score,
				})

			my_context['by_batch']=(
				(u'一批',objs.filter(take_1st_batch=True)),
				(u'二批',objs.filter(take_2nd_batch=True)),
				(u'三批',objs.filter(take_3rd_batch=True))
			)

			html+= detail.render(my_context)
		return HttpResponse(json.dumps({'html':html}), 
			content_type='application/javascript')	

class AnalysisSchoolByProvince(TemplateView):		
	template_name = 'pi/analysis/schools_by_province.html'
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		province = MyProvince.objects.get(id=int(kwargs['pk']))
		context['province'] = province 

		context['schools'] = MySchool.objects.filter(province=province)
		return context

@class_view_decorator(login_required)
class AnalysisSchoolByCity(TemplateView):
	template_name = 'pi/analysis/schools_by_city.html'
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		city = MyCity.objects.get(id=int(kwargs['pk']))
		context['obj'] = city

		# trains
		context['trains'] = MyTrainStop.objects.filter(stop_name__icontains = city.city)
		return context

@class_view_decorator(login_required)
class AnalysisMajorByCategory(TemplateView):
	template_name = 'pi/analysis/major_by_category.html'
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		cat = MyMajorCategory.objects.get(id=int(kwargs['pk']))
		context['obj'] = cat
		context['total_subcats'] = len(cat.subs.all())
		context['total_majors'] = MyMajor.objects.filter(subcategory__in = cat.subs.all()).count()
		return context

import random
@class_view_decorator(login_required)
class AnalysisMajorBySubcategory(TemplateView):
	template_name = 'pi/analysis/major_by_subcategory.html'
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		cat = MyMajorSubcategory.objects.get(id=int(kwargs['pk']))
		context['obj'] = cat

		jobs = [job for major in cat.mymajor_set.all() for job in major.jobs.all()]
		context['jobs'] = random.sample(jobs,100)
		return context

###################################################
#
#	3rd party data integration views
#
###################################################
from tasks import baidu_consumer
import pynlpir # http://pynlpir.readthedocs.org/en/latest/api.html#module-pynlpir.nlpir

@class_view_decorator(login_required)
class IntegrationBaiduTiebaAJAX(TemplateView):
	'''
		AJAX post view
	'''
	template_name = 'pi/3rd/school_baidu_tieba.html'
	newsticker_template_name = 'pi/3rd/newstickers.html'
	def post(self,request):
		obj_id = request.POST['obj_id']
		school = MySchool.objects.get(id=int(obj_id))
		feeds = []

		# weibo
		# App Key：802677147
		# App Secret：f75be23800d779cc9dbbf6b467b7ff61		
		# Redirect url: https://api.weibo.com/oauth2/default.html
		# code: 4ccb7879bf204466b80e02c106d09727

		# read baidu
		params = {'keyword':school.name}

		# send a 3rd party service request
		baidu_consumer.delay(params)

		# read saved feeds
		feeds = MyBaiduStream.objects.filter(school=school).order_by('-last_updated')[:100]
		content = loader.get_template(self.template_name)
		tieba_html= content.render(Context({
			'obj':school,
			'feeds': feeds,
			}))

		# hot topics
		pynlpir.open() # must have this line!
		topics = feeds[:20]
		content = loader.get_template(self.newsticker_template_name)
		newsticker_html= content.render(Context({
			'objs':topics,
			'keywords': pynlpir.get_key_words(''.join([f.name+f.description for f in feeds]), max_words=50, weighted=True)
			}))
		pynlpir.close()

		return HttpResponse(json.dumps({'bd_html':tieba_html,'news_html':newsticker_html}), 
			content_type='application/javascript')

class BaiduImages(TemplateView):
	template_name = 'pi/3rd/baidu_images.html'
	def post(self,request):
		obj_id = request.POST['obj_id']
		school = MySchool.objects.get(id=int(obj_id))
		imgs = []
		for feeds in school.mybaidustream_set.all():
			imgs += [img.file.url for img in feeds.attachments.all()]

		content = loader.get_template(self.template_name)
		html= content.render(Context({'objs':imgs[:25]}))
		return HttpResponse(json.dumps({'html':html}), 
			content_type='application/javascript')

###################################################
#
#	Train views
#
###################################################		
@class_view_decorator(login_required)
class MyTrainRoute(TemplateView):
	template_name = 'pi/train/route.html'
	def post(self,request):
		start_province = request.POST['p'].strip()
		start_city = request.POST['c'].strip()

		# get starting point data
		dest = MyCity.objects.get(id=int(request.POST['h']))

		# get destination data
		if start_province: province = MyProvince.objects.filter(province__icontains=start_province)
		else: province = None

		if province and len(province) and start_city: start = MyCity.objects.filter(city__icontains=start_city, province=province[0])
		elif start_city: start = MyCity.objects.filter(city__icontains=start_city)
		else: start = None

		# get train that connects these starting point - dest
		trains = []
		group_by_category={}		
		if start and len(start):
			start = start[0]
			all_stops = MyTrainStop.objects.filter_by_start_end(start.city, dest.city)
			train_ids = set(all_stops.all().values_list('train_id',flat=True))

			# group train for display
			trains = [all_stops.filter(train_id=id).order_by('stop_index') for id in train_ids]
			group_by_category = {'G':[],'D':[],'Z':[],'T':[],'K':[],'MISC':[]}
			categories = group_by_category.keys()
			for train in trains:
				if train[0].category in categories: key = train[0].category
				else: key = 'MISC'

				tmp = {'stops': train}
				for stop in train:
					if start.city in stop.stop_name: tmp['start'] = stop
					elif dest.city in stop.stop_name: tmp['dest'] = stop
				segment = (tmp['dest'].arrival - tmp['start'].arrival).total_seconds()
				tmp['segment_duration_hours'], remain = divmod(segment,3600) 
				tmp['segment_duration_minutes'], remain = divmod(remain,60) 

				tmp['duration'] = list(train)[-1].arrival - train[0].arrival
				tmp['train_id'] = train[0].train_id

				# add to grouping
				group_by_category[key].append(tmp)

		content = loader.get_template(self.template_name)
		html= content.render(Context({
			'objs':trains,
			'start': start,
			'dest': dest,
			'req_start_province': start_province,
			'req_start_city': start_city,
			'group_by_category': group_by_category
		}))

		return HttpResponse(json.dumps({'html':html}), 
			content_type='application/javascript')	