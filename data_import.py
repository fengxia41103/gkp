#!/usr/bin/python  
# -*- coding: utf-8 -*- 
import sys,time,os,gc,csv

import django

sys.path.append(os.path.join(os.path.dirname(__file__), 'gaokao'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gaokao.settings")
from django.conf import settings

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

@profile
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

import numpy as np
def detect_me(filename='data/major.csv'):
	with open(filename,'r') as fp:
		idx = 1
		for line in fp:
			if len(line.split('\t'))!=8: print idx
			idx += 1

def main():
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

if __name__ == '__main__':
	main()