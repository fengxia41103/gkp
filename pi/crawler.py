#!/usr/bin/python  
# -*- coding: utf-8 -*-  
from django.conf import settings

import socks
import socket
import re,sys,time,codecs,shutil,tempfile,os.path
import urllib2, lxml.html
from itertools import izip_longest
from stem import Signal
from stem.control import Controller
from random import shuffle
from multiprocessing import Process
from utility import MyUtility
# import models
from pi.models import *

class TorUtility():
	def __init__(self):
		user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
		self.headers={'User-Agent':user_agent}

	def renewTorIdentity(self,passAuth):
	    try:
	        s = socket.socket()
	        s.connect(('localhost', 9051))
	        s.send('AUTHENTICATE "{0}"\r\n'.format(passAuth))
	        resp = s.recv(1024)

	        if resp.startswith('250'):
	            s.send("signal NEWNYM\r\n")
	            resp = s.recv(1024)

	            if resp.startswith('250'):
	                print "Identity renewed"
	            else:
	                print "response 2:", resp

	        else:
	            print "response 1:", resp

	    except Exception as e:
	        print "Can't renew identity: ", e

	def renew_connection(self):
		with Controller.from_port(port = 9051) as controller:
	  		controller.authenticate('natalie')
	  		controller.signal(Signal.NEWNYM)

	def request(self, url):
	    def _set_urlproxy():
	        proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"})
	        opener = urllib2.build_opener(proxy_support)
	        urllib2.install_opener(opener)
	    _set_urlproxy()
	    request=urllib2.Request(url, None, self.headers)
	    return urllib2.urlopen(request).read()

class MyCrawler():
	def __init__(self):
		self.logs = {
			'school':{
				'log':os.path.join(settings.MEDIA_ROOT,'school.log'),
				'counter':os.path.join(settings.MEDIA_ROOT,'school_counter.log')
			},
			'major':{
				'log':os.path.join(settings.MEDIA_ROOT,'major.log'),
				'counter':os.path.join(settings.MEDIA_ROOT,'major_counter.log')
			}
		}
		self.school_log = self.logs['school']['log']
		self.major_log = self.logs['major']['log']
		self.ip_url = 'http://icanhazip.com/'
		self.tor_util = TorUtility()
		self.util = MyUtility()

	def get_total_page_no (self, url):
		content = self.tor_util.request(url)
		html = lxml.html.document_fromstring(content)
		info = html.xpath('//span[@class="pageInfo"]')
		ii = info[0].text_content()
		pat=re.compile('[^/]*/(?P<page_no>\d+)\s')
		return pat.search(ii).group('page_no')

	def admission_by_school_crawler(self, index, url): 
		content = self.tor_util.request(url)
		html = lxml.html.document_fromstring(content)
		tds = html.xpath('//table[@class="markTable"]//td')
		records = self.util.grouper([t.text_content() for t in tds],9,'')
		print url, len(records)

		f = open(self.school_log,'a')
		f.write('\n'.join(['\t'.join([r.strip().encode('UTF-8') for r in rs]) for rs in records])+'\n')
		f.close()
		
		# if we persist into DB
		#self.admission_by_school_persist (records)

	def admission_by_school_persist (self,records):
		# if we choose to write to DB directly
		for r in records:
			school,created = MySchool.objects.get_or_create(name=r[0].strip())
			province,created = MyAddress.objects.get_or_create(province=r[1].strip())
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
			admission.save()
			del admission
			del school
			del province

	def admission_by_major_crawler(self, index, url): 
		content = self.tor_util.request(url)
		html = lxml.html.document_fromstring(content)
		tds = html.xpath('//table[@class="markTable"]//td')
		records = self.grouper([t.text_content() for t in tds[1:]],8,'')
		print url, len(records)

		f = open(self.major_log,'a')
		f.write('\n'.join(['\t'.join([r.strip().encode('UTF-8') for r in rs]) for rs in records])+'\n')
		f.close()

		# if we persist into DB
		#self.admission_by_major_persist (records)

	def admission_by_major_persist (self,records):
		# if choose to write to DB directly
		for r in records:
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
			admission.save()

	def fenshu_table_worker(self, base_url, source):
		# get total page so we know the range
		total_page_no = int(self.get_total_page_no ('%s.html' % base_url))+1
		print 'total page no:', total_page_no
		page_index = range(1,total_page_no)

		# how much have we done?
		counters = open(self.logs[source]['log'],'r').read().split('\n')
		counters = [int(c) for c in filter(lambda x: len(x)>0, counters)]
		work_load = list(set(page_index)-set(counters))

		start = time.time()
		next_switch = 0
		f_counter = open(self.logs[source]['log'],'a')
		print 'Total of %d pages left. Go!' % len(work_load)
		shuffle(work_load)
		
		renew_threshold = 60.0
		where = 0
		for i in work_load:
			if source == 'school': self.admission_by_school_crawler (i,'%s-p-%d.html' % (base_url,i))
			elif source == 'major': self.admission_by_major_crawler (i,'%s-%d.html' % (base_url,i))

			# save counter
			f_counter.write('%d\n' % i)
			f_counter.flush()
			where += 1

			end = time.time()
			# switch TOR which may assign a new IP
			if (end-next_switch) > renew_threshold:
				self.tor_util.renew_connection()
				print '*'*50
				print '\t'*6+'Renew TOR IP: ', self.tor_util.request(ip_url)			
				print '*'*50
				next_switch = end+10.0

			print '%d/%d --- elapsed: ' % (where, len(work_load)), time.time() - start
		f_counter.close()
		return 'done'

	def thread_fenshu_crawler (self, base_url, source):
		# dump school's
		base_url = 'http://www.gaokaopai.com/fenshuxian'
		base_url = 'http://www.gaokaopai.com/fenshuxian-sct-2-p'
	
		while 1:
			try:
				counters = len(open(self.logs[source]['log'],'r').read().split('\n'))
				total_page_no = int(self.get_total_page_no ('%s.html' % base_url))+1
				print 'total page no:', total_page_no
				if counters >= total_page_no: break
				elif self.fenshu_table_worker(base_url, source) == 'done': break
			except:
				print '*'*50+'\n'+'\t'*6+'ERROR! SLEEPING\n'+'*'*50+'\n' 
				time.sleep(3)
			finally: 
				sys.stdout.flush()

	def school_crawler(self, index, url):
		content = self.tor_util.request(url)
		html = lxml.html.document_fromstring(content)
		tds = html.xpath('//table[@class="markTable"]//td')
		
		# school name
		name = html.xpath('//div[@class="schoolName"]/strong')[0].text_content().strip()
		if name is '': return
		try: en_name = html.xpath('//div[@class="enName"]')[0].text_content().strip()
		except: en_name = None

		intro = html.xpath('//div[@class="intro"]')[0].text_content().strip()

		tt = [a.text_content() for a in html.xpath('//ul[@class="baseInfo_left"]//div[@class="c"]')]
		try: yr = int(tt[0][:-1])
		except: yr = None

		if u'人' in tt[2] and u'~' not in tt[2]:
			try: no_student = int(tt[2][:-1])
			except: no_student = None
		elif u'人' in tt[2] and u'~' in tt[2]:
			try: no_student = int(tt[2].split(u'~')[1][:-1])
			except: no_student = None
		else:
			try: no_student = int(tt[2])
			except: no_student = None

		if u'人' in tt[3]:
			try: no_fellow = int(tt[3][:-1])
			except: no_fellow = None
		else:
			try: no_fellow = int(tt[3][:-1])
			except: no_fellow = None			

		tt = [a.text_content() for a in html.xpath('//ul[@class="baseInfo_right"]//div[@class="c"]')]
		try: key_major = int(tt[0][:-1])
		except: key_major = None
		try: no_phd_program = int(tt[2][:-1])
		except: no_phd_program = None
		try: no_master_program = int(tt[3][:-1])
		except: no_master_program = None

		school, created = MySchool.objects.get_or_create (name = name.strip())
		school.description = intro
		school.raw_page = content
		school.founded = yr
		school.no_student = no_student
		school.no_fellow = no_fellow
		school.key_major = key_major
		school.school_type = tt[1].strip()
		school.no_phd_program = no_phd_program
		school.no_master_program = no_master_program
		school.save()

	def school_worker(self, base_url, start_index, total_page_no):
		# get total page so we know the range
		print 'total page no:', total_page_no

		existing = MySchool.objects.filter(raw_page__isnull=True)
		work_load = [e.id for e in existing]
		work_load = range(1, 3301)
		shuffle(work_load)

		start = time.time()
		ip_url = 'http://icanhazip.com/'
		next_switch = 0
		print 'Total of %d pages left. Go!' % len(work_load)
		
		renew_threshold = 60.0
		where = 0
		for i in work_load:
			self.school_crawler(i, '%s-%d.html' % (base_url,i))
			where += 1

			end = time.time()
			# switch TOR which may assign a new IP
			if (end-next_switch) > renew_threshold:
				self.tor_util.renew_connection()
				print '*'*50
				print '\t'*6+'Renew TOR IP: ', self.tor_util.request(ip_url)			
				print '*'*50
				next_switch = end+10.0

			print '%d/%d --- elapsed: ' % (where, len(work_load)), time.time() - start
		return 'done'

	def thread_school_crawler (self, base_url):
		# dump school's
		existing = MySchool.objects.filter(raw_page__isnull=True)
		total_page_no = 3301

		while 1:
			try:
				print 'total page no:', total_page_no
				if len(existing) >= total_page_no: break
				elif self.school_worker(base_url, 1, total_page_no) == 'done': break
				#elif self.school_worker(base_url, len(existing), total_page_no) == 'done': break

			except:
				print '*'*50+'\n'+'\t'*6+'ERROR! SLEEPING\n'+'*'*50+'\n' 
				time.sleep(3)
			finally: 
				sys.stdout.flush()				

	def major_crawler (self, major, url):
		print major.code, major.name, url
		content = self.tor_util.request(url)
		html = lxml.html.document_fromstring(content)

		degree = None
		h3 = html.xpath('//div[@class="majorBase"]/h3')
		if len(h3) == 3:
			degree = h3[1].text_content().strip()
			degree = degree[degree.find(u'：'):].strip()
			how_long = h3[2].text_content().strip()
			how_long = how_long[how_long.find(u'：')+1:].strip()
		elif len(h3) == 2:
			how_long = h3[1].text_content().strip()
			how_long = how_long[how_long.find(u'：')+1:].strip()

		try: course = html.xpath('//div[@class="majorBase"]/div[@class="course"]/p')[0].text_content().strip()
		except: course = None
		description = html.xpath('//div[@class="majorCon"]')[0].text_content().strip()
		if degree and major.degree is None: major.degree = degree
		major.how_long = how_long
		major.course = course
		major.description = description
		major.save()

		related = html.xpath('//div[@class="majorBase"]/div[@class="course"]/a')
		for r in related:
			m,created = MyMajor.objects.get_or_create(name=r.text_content().strip())
			major.related_majors.add(m)

	def thread_major_crawler(self):
		while 1:
			#try:
			work_load = MyMajor.objects.filter(description__isnull = True, code__isnull=False).exclude(code__exact='')
			print 'Total of %d pages left. Go!' % len(work_load)

			start = time.time()
			next_switch = 0
			renew_threshold = 60
			where = 0
			for w in work_load:
				url = 'http://www.gaokaopai.com/zhuanye-jianjie-%s.html'%w.code
				self.major_crawler(w,url)

				end = time.time()
				where += 1
				# switch TOR which may assign a new IP
				if (end-next_switch) > renew_threshold:
					self.tor_util.renew_connection()
					print '*'*50
					print '\t'*6+'Renew TOR IP: ', self.tor_util.request(self.ip_url)			
					print '*'*50
					next_switch = end+10.0

				print '%d/%d --- elapsed: ' % (where, len(work_load)), time.time() - start
			break

			#except:
			#	print '*'*50+'\n'+'\t'*6+'ERROR! SLEEPING\n'+'*'*50+'\n' 
			#	time.sleep(3)
			#finally: 
			sys.stdout.flush()				

def main():
	# dump school's
	school_base_url = 'http://www.gaokaopai.com/fenshuxian'
	major_base_url = 'http://www.gaokaopai.com/fenshuxian-sct-2-p'
	crawler = MyCrawler()
	crawler.thread_fenshu_crawler(school_base_url,'school')
	
if __name__ == '__main__':
	main()
