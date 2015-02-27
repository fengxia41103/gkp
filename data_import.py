#!/usr/bin/python  
# -*- coding: utf-8 -*- 
import sys,time,os,gc,csv
import lxml.html

# setup Django
import django
sys.path.append(os.path.join(os.path.dirname(__file__), 'gaokao'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gaokao.settings")
from django.conf import settings

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

import googlemaps
def main():
	django.setup()
	#add_school_address()
	#google_geocoding()
	baidu_geocoding()

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
	ak = '15a027206f52227322d641d63057dde8';
	url = 'http://api.map.baidu.com/geocoder/v2/';

	for idx, s in enumerate(MySchool.objects.all()):
		#if s.baidu_geocode: continue

		retry = 3
		result = None

		print idx, ':', s.name
		
		# compose url
		#if len(s.address): val=s.address
		#else: val = s.name
		val = s.name
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
			except:
				print 'json loading failed'
				print result.read()

def google_geocoding():
	# https://code.google.com/apis/console/?noredirect&pli=1#project:871463256694:access
	gmaps = googlemaps.Client(key='AIzaSyBs9Lh9SBeGg8azzB5h50y8DDjxFO4SLwA')
	for s in MySchool.objects.all():
		if u'民办' in s.name: s.name = s.name.replace(u'民办','')
		#if s.google_geocode and len(s.google_geocode): continue

		print 'Working on ', s.name
		if len(s.address):s.google_geocode = gmaps.geocode(address=s.address,components={'country':'CN'})
		else: continue 
			#s.google_geocode = gmaps.geocode(address=s.name,components={'country':'CN'})
		
		if len(s.google_geocode) == 1:
			s.formatted_address_en = s.google_geocode[0][u'formatted_address']
			s.en_name = s.google_geocode[0][u'address_components'][0][u'long_name']
		elif len(s.google_geocode) < 1:
			print 'No geocode info: ', s.name
		elif len(s.google_geocode) > 1:
			print '>1 geocode info', s.name
		s.save()

if __name__ == '__main__':
	main()