#!/usr/bin/python  
# -*- coding: utf-8 -*- 
import sys,time,os,gc,csv
import lxml.html
import urllib
import simplejson as json

# setup Django
import django
sys.path.append(os.path.join(os.path.dirname(__file__), 'gaokao'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gaokao.settings")
from django.conf import settings

from django.utils import timezone

# import models
from pi.models import *

def admission_by_school_persist (r):
	# if we choose to write to DB directly
	school, created = MySchool.objects.get_or_create(name=r[0].strip())
	province, created = MyAddress.objects.get_or_create(province=r[1].strip())
	cat = r[2].strip()
	try:
		yr = int(r[3])
	except: yr = 0
	batch = r[4].strip()
	
	try:
		min_score = int(r[5])
	except: min_score=None
	try:
		max_score = int(r[6])
	except: max_score=None
	try:
		avg_score = int(r[7])
	except: avg_score=None
	try:
		p_score = int(r[8])
	except: p_score=None
	
	admission = MyAdmissionBySchool(
		school = school,
		province = province,
		category = cat,
		year = yr,
		batch = batch,
		min_score = min_score,
		max_score = max_score,
		avg_score = avg_score,
		province_score = p_score
	)
	return admission

def admission_by_major_persist (r):
	# if choose to write to DB directly
	major,created = MyMajor.objects.get_or_create(name=r[0].strip())		
	school,created = MySchool.objects.get_or_create(name=r[1].strip())

	try:
		avg_score = int(r[2])
	except: avg_score=None
	try:
		max_score = int(r[3])
	except: max_score=None
	
	province,created = MyAddress.objects.get_or_create(province=r[4].strip())
	
	cat = r[5].strip()
	try:
		yr = int(r[6])
	except: yr = 0
	batch = r[7].strip()
		
	admission = MyAdmissionByMajor(
		school = school,
		major = major,
		province = province,
		category = cat,
		year = yr,
		batch = batch,
		max_score = max_score,
		avg_score = avg_score
	)
	return admission

def import_admission_by_school(filename, batch_no, start_at=0, batch_size = 1000):
	start = time.time()
	idx = 0
	records = None
	save_list = []
	stop_at = None
	eof = False
	with open(filename,'r') as fp:
		fp.seek(start_at)
		while idx < batch_size:
			try:
				records = fp.readline().decode('utf-8').split('\t')
				if len(records) != 9: raise EOFError
				save_list.append(admission_by_school_persist(records))
				idx += 1
			except EOFError: 				
				eof = True
				break
		MyAdmissionBySchool.objects.bulk_create(save_list)			
		stop_at = fp.tell()

		elapsed = (time.time()-start)/3600
		sys.stdout.write('%d-'%batch_no)
		sys.stdout.flush()
	return (stop_at,eof,elapsed)

def import_admission_by_major(filename, batch_no, start_at=0, batch_size = 1000):
	start = time.time()
	idx = 0
	records = None
	save_list = []
	stop_at = None
	eof = False
	with open(filename,'r') as fp:
		fp.seek(start_at)
		while idx < batch_size:
			try:
				records = fp.readline().decode('utf-8').split('\t')
				if len(records) != 8: raise EOFError
				save_list.append(admission_by_major_persist(records))
				idx += 1
			except EOFError: 				
				eof = True
				break
		MyAdmissionByMajor.objects.bulk_create(save_list)			
		stop_at = fp.tell()

		elapsed = (time.time()-start)/3600
		sys.stdout.write('%d-'%batch_no)
		sys.stdout.flush()
	return (stop_at,eof,elapsed)

def import_school_major_relation(filename):
	start = time.time()
	idx = 1
	r=school=major=None
	for line in open(filename):
		print '%d is being processed' % idx
		idx += 1
		r = [a.decode('UTF-8') for a in line.strip().split('\t')]
		major = MyMajor.objects.get(name = r[0].strip())
		school = MySchool.objects.get(name = r[1].strip())
		major.schools.add(school)
		
	print 'Total elapsed time: %f' % ((time.time()-start)/3600.0)

def import_school_major_csv():
	django.setup()
	stop_at = int(sys.argv[1])
	eof=False
	batch_no = 1
	profile=[]
	while eof is not True and batch_no <= 500:
		#stop_at,eof,elapsed = import_admission_by_school('data/school.csv', batch_no = batch_no, batch_size=1000, start_at = stop_at)
		stop_at,eof,elapsed = import_admission_by_major('data/major.csv', batch_no = batch_no, batch_size=1000, start_at = stop_at)
		batch_no += 1
		profile.append(elapsed)
	if eof is False: print 'stopped at ', stop_at
	print 'Total time: %f' % sum(profile)
	print 'Avg time: %f' % np.mean(profile)

def add_school_address():
	objs = filter(lambda x: x.raw_page, MySchool.objects.all())
	we_want = [u'招生电话：',u'学校地址：',u'所处城市：',u'电子邮箱：']

	for s in objs:
		html = lxml.html.document_fromstring(s.raw_page.encode('utf-8'))
		infos = html.xpath('//div[@class="infos"]/ul/li')
		# 鹤壁能源化工职业学院, the page is essentially empty
		if len(infos) == 0: continue

		for i in infos:
			node = i.text_content()
			label = i.xpath('label')
			if len(label) and label[0].text_content() in we_want:
				label = label[0].text_content()
				val = node[len(label):]
				val=val.replace(u'...','').strip()
				if u'暂无' in val: val=''

				print label, val

				if label == u'招生电话：':
					s.admission_office_phone = val 
				elif label == u'学校地址：':
					s.address = val 
				elif label == u'所处城市：':
					s.city = val
				elif label == u'电子邮箱：':
					s.admission_office_email = val
		s.save()

import urllib2,json
from time import sleep
def baidu_geocoding():
	failed = []
	for idx, s in enumerate(MySchool.objects.all()):
		if s.baidu_geocode: continue
		print idx, ':', s.name
		
		# compose url
		#if len(s.address): val=s.address
		#else: val = s.name
		if not baidu_geocoding_2(s.name) and s.address is not None:
			if not baidu_geocoding_2(s.address):
				print 'Baidu failed completely!'
				if s.google_geocode is None or len(s.google_geocode)==0:
					print 'we have no GEO on file!'
					failed.appends(s)
		elif s.address is None and (s.google_geocode is None or len(s.google_geocode)==0):
			print 'we have no GEO on file!'
			failed.append(s)

	# list that has no GEO from both Baidu and Google
	print [s.name for s in failed]

from shapely.geometry import Point
from decimal import Decimal
def populate_school_province():
	states = MyAddress.objects.all()
	for idx, s in enumerate(MySchool.objects.all()):
		if s.address is None and s.city is None: continue

		for p in states:
			if p.province in s.address or p.province in s.city:
				s.province = p
				print s.name, ':', p.province
				s.save()
				break

def populate_school_geo():
	# wow, this is a hard find: Baidu's geocode is not correct on Google map!
	# So we use Baidu's as a reference, and iterate through all available Google's geocode
	# results by distance match, and find the closest one to use!
	for idx, s in enumerate(MySchool.objects.all()):
		if not (s.google_geocode and s.lat and s.lng): continue
		print idx, s.name
		ref = Point(s.lat,s.lng)
		min_dist = 1000000
		min_pair = None
		for g in filter(lambda x: x.has_key('geometry'), s.google_geocode):
			lat,lng = Decimal(g[u'geometry'][u'location'][u'lat']), Decimal(g[u'geometry'][u'location'][u'lng'])
			dist = ref.distance(Point(lat,lng))
			if dist < min_dist: 
				min_dist = dist
				min_pair = (lat,lng)
		if min_pair:
			s.lat, s.lng = min_pair
			s.save()
			print idx, 'updated...... next >'

		#except:
		#	print s.id, s.name
		#	continue

from difflib import SequenceMatcher, get_close_matches
def cleanup_school_name ():
	for idx, s in enumerate(MySchool.objects.all()):
		if idx > 2400: continue
		print idx, s.name
		try:
			if not s.google_geocode.has_key('status') or s.google_geocode['status'] != 'OK': continue
		except:
			continue
		pois = []
		similarity = 0
		closest_match = None
		exact = False		
		for addr in filter(lambda x: x.has_key('geometry') and x.has_key('address_components'), s.google_geocode['results']):
			for p in filter(lambda x: 'point_of_interest' in x['types'], addr['address_components']):
				possible_name = p['long_name']
				diff = SequenceMatcher(None,possible_name,s.name).ratio()
				if diff > 0.99: # exact match!
					s.name = possible_name
					closest_match = addr
					exact = True
					break
				elif diff > similarity: 
					s.name = possible_name
					similarity = diff
					closest_match = addr
			if exact: break
		if closest_match:
			if s.address is '': 
				s.address= addr['formatted_address']
			s.lat = addr['geometry']['location']['lat']
			s.lng = addr['geometry']['location']['lng']
			s.save()
			print 'updating ',s.name

def baidu_geocoding_2(val):
	ak = '15a027206f52227322d641d63057dde8';
	url = 'http://api.map.baidu.com/geocoder/v2/';

	retry = 3
	result = None
	post_url = url+'?address='+val.encode('utf-8')+'&output=json&ak='+ak

	while retry:
		try:
			result = urllib2.urlopen(post_url, timeout=5)
			break
		except: 
			print 'retrying....', retry
			retry -= 1

	if result is None:
		print 'timed out'
		return False		
	else:
		try:
			geo = json.loads(result.read())
			if geo[u'status'] == 0:
				location = geo[u'result'][u'location']
				s.lat = location[u'lat']
				s.lng = location[u'lng']
				s.baidu_geocode = geo
				s.save()
			else: print 'Status is not 0'
			return True
		except:
			print 'json loading failed'
			print result.read()
			return False
	return True

def google_geocoding():
	#https://maps.googleapis.com/maps/api/geocode/json?address=&sensor=false&key=AIzaSyBs9Lh9SBeGg8azzB5h50y8DDjxFO4SLwA&language=zh-cn
	# https://code.google.com/apis/console/?noredirect&pli=1#project:871463256694:access
	key='AIzaSyBs9Lh9SBeGg8azzB5h50y8DDjxFO4SLwA'
	for idx, s in enumerate(MySchool.objects.all()):
		if u'民办' in s.name: s.name = s.name.replace(u'民办','')
		if idx < 3267: continue

		print idx, ': Working on ', s.name
		# renew: 2849
		query = urllib.urlencode({
			'address':s.name.encode('utf-8'),
			'sensor':'false',
			'key':key,
			'language':'zh-cn'
		})

		post_url = 'https://maps.googleapis.com/maps/api/geocode/json?' + query
		result = urllib2.urlopen(post_url, timeout=5)
		geo = json.loads(result.read())
		if geo['status'] != 'OK':
			print 'Error: ',s.name 
			raw_input()
			continue
		if len(geo['results'])>1:
			print ">1 results!"

		s.google_geocode = geo
		s.google_placeid = geo['results'][0]['place_id']
		s.formatted_address_cn = geo['results'][0]['formatted_address']
		s.lat = geo['results'][0]['geometry']['location']['lat']
		s.lng = geo['results'][0]['geometry']['location']['lng']
		s.save()

import hashlib
def populate_hash ():
	for s in MySchool.objects.all():
		md5 = hashlib.md5()
		md5.update(s.name.encode('utf-8'))
		s.hash = md5.hexdigest()
		s.save()

def cleanupSchoolAdmission():
	large_qs = MyAdmissionBySchool.objects.all().values_list("id", flat=True)
	for idx, id in enumerate(large_qs):
		s = MyAdmissionBySchool.objects.get(id=id)
		print idx, s.school.name
		if s.batch == u'':
			s.batch = u'一批'
		elif u'本科第二批' in s.batch:
			s.batch = u'二批'
		elif s.batch == u'本科3批':
			s.batch = u'三批'
		s.save()

def cleanupProvince():
	provinces = MyAddress.objects.all()
	for s in MySchool.objects.all():
		for p in provinces:
			if p.province in s.city:
				print 'updating:',s.name,p.province
				s.province=p
				s.save()
				break

def cleanupSchoolDescription():
	for s in MySchool.objects.all():
		if s.description is None: continue
		if s.description.strip()=='<p></p>':
			s.description = None
			print 'updating ', s.name
			s.save()

def populateMajorSchoolRelationship():
	for s in MyMajor.objects.all():
		print 'Processing ',s.name

		if MyAdmissionByMajor.objects.filter(major=s).count()>0:
			school_list = list(set([a['school'] for a in MyAdmissionByMajor.objects.filter(major=s).values('school')]))

			print 'Updating ',s.name, len(school_list)
			s.schools.add(*school_list)
			s.save()

def cleanupMajor():
	for m in MyMajor.objects.all():
		if m.student_type and ',' in m.student_type:
			print 'Updating', m.name
			m.student_type = u'文理兼收'
			m.save()

def populateSchoolAttribute():
	for s in MySchool.objects.all():
		admission = MyAdmissionBySchool.objects.filter(school=s).values('province')
		s.accepting_province.clear()
		s.accepting_province.add(*list(set([a['province'] for a in admission])))
		s.save()
		print 'Updating', s.name

def fixBatch():
	ids = MyAdmissionByMajor.objects.filter(batch__in=[u'专科第1批',u'专科第2批']).values_list('id',flat=True)
	for idx,id in enumerate(list(set(ids))):
		s = MyAdmissionByMajor.objects.get(id=id)
		if s.batch == u'专科第1批': s.batch = u'专科1批'
		elif s.batch == u'专科第2批': s.batch = u'专科2批'
		print 'Updating', idx,'/',len(ids),':',s.school.name
		s.save()

def blanketRequest():
	for s in MySchool.objects.all():
		params = {'keyword':s.name}
		MyCrawlerRequest(source=1,params=json.dumps(params)).save()
		print 'Requesting', s.name		

from django.db.models import Avg
def populateRank():
	ids = MySchool.objects.values_list('id',flat=True)
	for id in ids:
		avg_score = MyAdmissionBySchool.objects.filter(school=id).aggregate(Avg('avg_score'))
		try: avg_score = int(avg_score['avg_score__avg'])
		except: avg_score = 0
		rank, created = MyRank.objects.get_or_create(school=MySchool.objects.get(id=id),rank_index=3,rank=avg_score)
		print id, avg_score

def populateOverallRank():
	# how we are to give each school an overall score
	# weighted average: 0.6
	min_score_weight = 1
	max_score_weight = 0.8
	avg_score_weight = 0.5
	no_fellow_weight = 5.0
	no_phd_program_weight = 3.0
	no_master_program_weight = 2.0
	weights = [min_score_weight,max_score_weight,avg_score_weight,no_fellow_weight,no_phd_program_weight,no_master_program_weight]

	ids = MySchool.objects.values_list('id',flat=True)
	for id in ids:
		min_score = MyRank.objects.get(school=id,rank_index=1)
		max_score = MyRank.objects.get(school=id,rank_index=2)
		avg_score = MyRank.objects.get(school=id,rank_index=3)
		scores = [min_score.rank,max_score.rank,avg_score.rank]

		rank = MyRank.objects.get(school=id,rank_index=-1)
		if rank.school.no_fellow: scores.append(rank.school.no_fellow)
		else: scores.append(0)

		if rank.school.no_phd_program: scores.append(rank.school.no_phd_program)
		else: scores.append(0)

		if rank.school.no_master_program: scores.append(rank.school.no_master_program)
		else: scores.append(0)

		rank.rank = int(sum([a*b for a,b in zip(weights,scores)])/sum(weights))
		rank.save
		print id, rank.rank

def cleanupSchoolName():
	for s in MySchool.objects.all():
		if s.description and s.name not in s.description:
			print s.name

from pi.tasks import train_consumer
def crawl_train():
	# 'G','D','Z','K','T','C'
	for key in ['G','D','Z','K','T','C','']:
		for index, train_id in enumerate(['%s%d'%(key,i) for i in range(1,9999)]):
			train_consumer.delay(train_id)

def cleanup_city():
	for s in MySchool.objects.all():
		if s.province and s.city2:
			city,created = MyCity.objects.get_or_create(city=s.city2,province=s.province)
			s.city = city
			s.save()
			print s.name
		else:
			print 'not complete: ',s.name

import googlemaps
def main():
	django.setup()
	#google_geocoding()posted
	#add_school_address()
	#google_geocoding()
	#baidu_geocoding()
	#populate_school_geo()
	#populate_school_province()
	#populate_hash()
	#cleanup_school_name()
	#cleanupSchoolAdmission()
	#cleanupProvince()
	#cleanupSchoolDescription()
	#populateMajorSchoolRelationship()
	#cleanupMajor()
	#populateSchoolAttribute()
	#fixBatch()
	#baidu_crawler()
	#blanketRequest()
	#populateRank()
	#cleanupSchoolName()
	#populateOverallRank()
	#crawl_train()
	cleanup_city()

if __name__ == '__main__':
	main()