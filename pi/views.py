#!/usr/bin/python  
# -*- coding: utf-8 -*-  

from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, login
from django.template import RequestContext
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt

# django-crispy-forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# django-filters
from django_filters import FilterSet, BooleanFilter
from django_filters.views import FilterView
import django_filters

# so what
import re,os,os.path,json,shutil,subprocess, testtools
import random,codecs,unittest,time, tempfile, csv
from datetime import datetime as dt
from multiprocessing import Process, Queue
from pi.models import *
from utility import MyUtility
from crawler import MyCrawler

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
def home_view (request):
	user_auth_form = AuthenticationForm()
	user_registration_form = UserCreationForm()

	forms = {'registration_form':user_registration_form,
			'auth_form':user_auth_form
			}

	csrfContext = RequestContext(request,forms)
	return render_to_response('pi/common/home.html', csrfContext)

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
#	User views
#
###################################################
def user_register_view (request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = UserCreationForm(request.POST)
		# check whether it's valid:
		if form.is_valid():
			user_name = form.cleaned_data['username']
			password = form.cleaned_data['password2']
			user = User.objects.create_user(user_name, '', password)			
			user.save()
			return HttpResponseRedirect (reverse_lazy('login'))
	# if a GET (or any other method) we'll create a blank form
	else: 
		form = UserCreationForm()
	return render(request, 'registration/register_form.html', {'registration_form': form})	

@login_required
def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse_lazy('home'))

###################################################
#
#	MyAdmissionBySchool views
#
###################################################
class MyAdmissionBySchoolListFilter (FilterSet):
	class Meta:
		model = MyAdmissionBySchool
		fields = {'school':['exact'],
				'province':['exact'],
				'category':['contains'],
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

def admission_school_crawler_view (request):
	base_url = 'http://www.gaokaopai.com/fenshuxian'
	crawler = MyCrawler()
	crawler.thread_fenshu_crawler(base_url, 'school')

	return HttpResponseRedirect(reverse_lazy('admission_school_list'))

###################################################
#
#	MyAdmissionByMajor views
#
###################################################
class MyAdmissionByMajorListFilter (FilterSet):
	class Meta:
		model = MyAdmissionByMajor
		fields = {'school':['exact'],
				'province':['exact'],
				'category':['contains'],
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

def admission_major_crawler_view (request):
	base_url = 'http://www.gaokaopai.com/fenshuxian-sct-2-p'
	crawler = MyCrawler()
	crawler.thread_fenshu_crawler(base_url, 'major')

	return HttpResponseRedirect(reverse_lazy('admission_major_list'))	

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

@class_view_decorator(login_required)
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

def import_major (request):
	code_pat=re.compile('\d+[TK]*')
	degree_pat = re.compile('(?P<name>[^(]+)[(](?P<degree>[^)]+)[)]')

	content = open(os.path.join(settings.MEDIA_ROOT,'major_std_2.csv'), 'r').read().split('\n')
	for (code,name) in filter(lambda x: len(x)==2 and code_pat.search(x[0]) is not None, [c.split(',') for c in content]):
		code = code_pat.search(code.strip()).group()
	
		if degree_pat.search(name):
			degree = degree_pat.search(name).group('degree')
			name = degree_pat.search(name).group('name')			
		else:
			degree = None
		if '应用化学' in name: print 'here', code, name, degree

		if len(code) == 2: # this is category
			cat, created = MyMajorCategory.objects.get_or_create(code=code,name=name)
		elif len(code) == 4: # this is subcategory
			subcat, created = MyMajorSubcategory.objects.get_or_create(code=code,name=name)
			cat,created = MyMajorCategory.objects.get_or_create(code=code[:2])
			subcat.category=cat
			subcat.save()
		else: # this is major
			major,created = MyMajor.objects.get_or_create(name=name.strip())
			major.code = code.strip()
			
			if 'T' in code: major.is_specialized = True
			if 'K' in code: major.is_gov_controlled = True

			subcat, created = MyMajorSubcategory.objects.get_or_create(code=code[:4])
			major.subcategory = subcat
			major.degree = degree
			if int(major.code[:2])>13:
				major.how_long = u'三年'
				major.degree_type = u'专科'
			else:
				major.how_long = u'四年'
				major.degree_type = u'本科'
			major.save()
	return HttpResponseRedirect(reverse_lazy('major_list'))	

def major_crawler_view (request):
	crawler = MyCrawler()
	crawler.thread_major_crawler()
	return HttpResponseRedirect(reverse_lazy('major_list'))	

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
				'en_name':['contains'],
				}

@class_view_decorator(login_required)
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

def school_crawler_view (request):
	base_url = 'http://www.gaokaopai.com/daxue-jianjie'
	crawler = MyCrawler()
	crawler.thread_school_crawler(base_url)

	return HttpResponseRedirect(reverse_lazy('school_list'))	

###################################################
#
#	Googlemap views
#
###################################################
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.vary import vary_on_headers
# protect the view with require_POST decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from shapely.geometry import box as Box
from shapely.geometry import Point
import json, googlemaps
from django.template import loader, Context

class MySchoolMapFilter (TemplateView):
	template_name = 'pi/common/gmap.html'
	info_template_name = 'pi/school/gmap_info.html'

	def get_context_data(self, **kwargs):
	    context = super(TemplateView, self).get_context_data(**kwargs)

	    # TODO: center is now WuHan. Should be based on User's location
	    context['center'] = {'lat':30.593099,'lng':114.305393}
	    context['data_url']=reverse('school_map_filter')
	    return context

	def post(self, request):
		markers = []
		coords=request.POST # viewport bounds
		bound = Box(float(coords['sw.k']),float(coords['sw.D']), float(coords['ne.k']),float(coords['ne.D']))
		info_win = loader.get_template(self.info_template_name)

		# filter schools for the ones that are visible at current Zoom level and viewport
		for s in MySchool.objects.all():
			# we are iterating all geocode in DB
			# TODO: some geocode are not correct. We need to clean that data.
			for g in filter(lambda x: x.has_key('geometry'), s.google_geocode):
				lat,lng = float(g[u'geometry'][u'location'][u'lat']), float(g[u'geometry'][u'location'][u'lng'])
				if bound.contains(Point(lat,lng)):
					c = Context({
						'id': 'schoold_%d'%s.id,
						'user': request.user,
						'ip_address': request.META['REMOTE_ADDR'],
						'title': s.name,
						'obj': s
					})
					markers.append({
							'lat': lat,
							'lng': lng,
							'name':s.name,
							'edit': reverse('school_edit',args = [s.id]),
							'info_win': info_win.render(c)
						})
		return HttpResponse(json.dumps(markers), content_type='application/javascript')	