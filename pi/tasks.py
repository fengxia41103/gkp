# -*- coding: utf-8 -*- 
from __future__ import absolute_import

from celery import shared_task

import lxml.html
import urllib, urllib2
import simplejson as json
import pytz
import socks
import socket
import logging
from stem import Signal
from stem.control import Controller
from random import randint
import time
import hashlib
from urllib3 import PoolManager, Retry, Timeout
from tempfile import NamedTemporaryFile
from django.core.files import File
from pi.models import *

# create logger with 'spam_application'
logger = logging.getLogger('gkp')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('/tmp/gkp.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

retries = Retry(connect=5, read=2, redirect=5)
http_manager = PoolManager(retries=retries, timeout=Timeout(total=15.0))

class PlainUtility():
	def __init__(self, http):
		user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
		self.headers={'User-Agent':user_agent}
		self.ip_url = 'http://icanhazip.com/'
		self.logger = logging.getLogger('gkp')
		self.http = http

	def current_ip(self):
		return self.request(self.ip_url)

	def request(self,url):
		r = self.http.request('GET',url)
		if r.status == 200: return r.data
		else: self.logger.error('status %s'%r.status)

class TorUtility():
	def __init__(self):
		user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
		self.headers={'User-Agent':user_agent}
		self.ip_url = 'http://icanhazip.com/'
		self.logger = logging.getLogger('gkp')

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
	                self.logger.info("Identity renewed")
	            else:
	                self.logger.info("response 2:%s"%resp)

	        else:
	            self.logger.info("response 1:%s"%resp)

	    except Exception as e:
	        self.logger.error("Can't renew identity: %s"%e)

	def renew_connection(self):
		with Controller.from_port(port = 9051) as controller:
	  		controller.authenticate('natalie')
	  		controller.signal(Signal.NEWNYM)

		self.logger.info('*'*50)
		self.logger.info('\t'*6+'Renew TOR IP: %s'%self.request(self.ip_url))
		self.logger.info('*'*50)
	
	def _set_urlproxy(self):
	    proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"})
	    opener = urllib2.build_opener(proxy_support)
	    urllib2.install_opener(opener)

	def request(self, url, retry=3):
		go = 0
		while go < retry:
			try:
				self._set_urlproxy()
				request=urllib2.Request(url, None, self.headers)
				return urllib2.urlopen(request).read()
			except:
				self.logger.error('Retrying #%d' % go)
				go += 1
				self.renew_connection()

	def current_ip(self):
		return self.request(self.ip_url)

class MyBaiduCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('gkp')

	def tieba(self,keyword):
		baidu_url = 'http://tieba.baidu.com/f?kw=%s&ie=utf-8'%urllib.quote(keyword.encode('utf-8'))
		content = self.http_handler.request(baidu_url)
		html = lxml.html.document_fromstring(content)

		threads = []
		for t in html.xpath('//li[contains(@class, "j_thread_list")]'):
			if t.get('data-field') is None: continue

			stats = json.loads(t.get('data-field'))
			if stats['is_top'] or not stats['reply_num']: continue  # sticky posts, always on top, so we skip these

			# basic thread infos
			this_thread = {
				'source':u'百度贴吧',
				'author': stats['author_name'],
				'author_id':stats['id'],
				'url':'http://tieba.baidu.com/p/%d' % stats['id'],
				'reply_num': stats['reply_num'],
				'title': t.xpath('.//a[contains(@class,"j_th_tit")]')[0].text_content().strip(), # post title line
				'abstract': t.xpath('.//div[contains(@class,"threadlist_abs_onlyline")]')[0].text_content().strip(), # post abstracts
				'last_timestamp': t.xpath('.//span[contains(@class,"threadlist_reply_date")]')[0].text_content().strip()			}

			imgs = []
			for i in t.xpath('.//img[contains(@class,"threadlist_pic")]'):
				#imgs.append(i.get('original')) # this is thumbnail
				imgs.append(i.get('bpic')) # this is full size pic, has to save locally first. Link to Baidu won't work.
			this_thread['imgs']=imgs

			# add to list
			threads.append(this_thread)

		return threads

	def consumer(self, params):
		'''
			read 3rd party content		
		'''
		keyword = params['keyword']
		if '(' in keyword: keyword=keyword[:keyword.find('(')]
		try: # school name can be changed outside this request, so we take precaution here!
			school = MySchool.objects.get(name=keyword)
		except: return
		results = self.tieba(keyword)

		# save results to DB
		for t in results:
			# make django's timezone-aware timestamp
			if ':' in t['last_timestamp']:
				tmp = t['last_timestamp'].split(':')
				now = timezone.now()
				post_timestamp = dt(now.year,now.month,now.day,int(tmp[0]),int(tmp[1]))
				post_timestamp = pytz.timezone(timezone.get_default_timezone_name()).localize(post_timestamp)
			elif '-' in t['last_timestamp']: 
				tmp = t['last_timestamp'].split('-')
				now = timezone.now()
				
				# some quirky condition
				tmp_mon = int(tmp[0])
				if tmp_mon > now.month: year = now.year-1
				else: year = now.year

				post_timestamp = dt(year,tmp_mon,int(tmp[1]))
				post_timestamp = pytz.timezone(timezone.get_default_timezone_name()).localize(post_timestamp)
			else: post_timestamp = None

			# create records in DB
			data = MyBaiduStream.objects.filter(
				url_original = t['url'],
				school = school
			)
			if len(data) > 1: 
				for d in data[1:]:
					Attachment.objects.filter(object_id=d.id).delete()
					d.delete()
				data = data[0]
			elif len(data)==1: data = data[0]
			else: data = MyBaiduStream(url_original=t['url'],school=school)

			#except: 
			#	self.logger.error('DB save failed!')
			#	self.logger.error(t)				
			#	continue # DB was not successful
			data.reply_num = t['reply_num']
			data.name = t['title']
			data.description = t['abstract']
			data.author_id = str(t['author_id'])
			data.author = t['author']

			if post_timestamp: 
				data.last_updated=post_timestamp
			data.save()

			# look up its attachments, if any
			for img_url in t['imgs']:
				if len(Attachment.objects.filter(source_url=img_url)): continue # exist

				self.logger.info('retrieving images [%s]' % img_url)

				# get image and store into a tmp file
				img_data = None
				try: img_data = self.http_handler.request(img_url)
				except: self.logger.error('Retrieve img failed: %s' % img_url)
				if img_data:
					tmp_file = NamedTemporaryFile(suffix='.jpg',delete=False)
					tmp_file.write(img_data)
					attchment = Attachment(	
						source_url = img_url,
						content_object=data,
						file=File(tmp_file)
					).save()

					# this will remove the tmp file from filesystem
					tmp_file.close()

@shared_task
def test(param):
    return 'The test task executed with argument "%s" ' % param

@shared_task
def baidu_consumer(param):
	http_agent = PlainUtility(http_manager)
	'The test task executed with argument "%s" ' % json.dumps(param)
	crawler = MyBaiduCrawler(http_agent)
	crawler.consumer(param)