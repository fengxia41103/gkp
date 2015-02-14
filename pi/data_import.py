#!/usr/bin/python  
# -*- coding: utf-8 -*- 

import sys
from crawler import MyCrawler

def import_admission_by_school(filename):
	content = open(filename).read().split('\n')
	MyCrawler().admission_by_school_persist([[a.decode('UTF-8') for a in c.split('\t')] for c in content])

def import_admission_by_major(filename):
	content = open(filename).read().split('\n')
	MyCrawler().admission_by_major_persist([[a.decode('UTF-8') for a in c.split('\t')] for c in content])

def import_school_major_relation(filename):
	content = open(filename).read().split('\n')
	for index, r in enumerate([[a.decode('UTF-8') for a in c.split('\t')] for c in content], start=1):
		major = MyMajor.objects.get(name = r[0].strip())
		school = MySchool.objects.get(name = r[1].strip())
		major.schools.add(school)

if __name__ == '__main__':
	main()