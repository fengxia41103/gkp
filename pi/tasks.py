# -*- coding: utf-8 -*- 
from __future__ import absolute_import

from celery import shared_task

import lxml.html
import simplejson as json
import pytz
import logging
from random import randint
import time
import hashlib
import urllib, urllib2
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

class MyBaiduCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('gkp')

	def parse_tieba(self,keyword):
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

	def parser(self, params):
		'''
			read 3rd party content		
		'''
		keyword = params['keyword']
		if '(' in keyword: keyword=keyword[:keyword.find('(')]
		try: # school name can be changed outside this request, so we take precaution here!
			school = MySchool.objects.get(name=keyword)
		except: return

		# parse retrieved html
		results = self.parse_tieba(keyword)

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
					if Attachment.objects.filter(source_url=img_url).exists(): continue
					else:
						attchment = Attachment(	
							source_url = img_url,
							content_object=data,
							file=File(tmp_file)
						).save()

					# this will remove the tmp file from filesystem
					tmp_file.close()


from gaokao.tor_handler import TorUtility
@shared_task
def baidu_consumer(param):
	#http_agent = PlainUtility(http_manager)
	http_agent = TorUtility()
	'The test task executed with argument "%s" ' % json.dumps(param)
	crawler = MyBaiduCrawler(http_agent)
	crawler.parser(param)

from itertools import izip_longest
def grouper(iterable, n, padvalue=None):
	# grouper('abcdefg', 3, 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')
	return list(izip_longest(*[iter(iterable)]*n, fillvalue=padvalue))

from datetime import timedelta
import re
class MyTrainCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('gkp')

	def parse_time (self,time_string):
		time_string = time_string.strip()
		if time_string in [u'始发站',u'终点站']: return None
		elif u'第' in time_string:
			day_delta = int(time_string[:4].strip()[1])
			timestamp = time_string[-5:].strip()
			hour,minute = tuple(timestamp.split(':'))
			timestamp = dt(2015,1,int(day_delta),int(hour),int(minute))
		else:
			hour,minute = tuple(time_string.split(':'))
			timestamp = dt(2015,1,1,int(hour),int(minute))
		return pytz.timezone(timezone.get_default_timezone_name()).localize(timestamp)		

	def parser(self,train_id):
		url = 'http://trains.ctrip.com/TrainSchedule/%s/'%train_id.upper()
		content = self.http_handler.request(url)
		html = lxml.html.document_fromstring(content)

		if not html.xpath('//div[@class="s_hd"]/span'): return

		ids = html.xpath('//div[@class="s_hd"]/span')[0].text_content().strip()
		ids = ids.split('/')
		#summary = html.xpath('//div[@class="s_bd"]/table')[0]
		#summary = grouper([td.text_content().strip() for td in summary.xpath('.//td')],7)[0]
		
		#start = self.parse_time(summary[3])
		#end = self.parse_time(summary[4])
		for t_id in ids:
			if not t_id: continue

			pat = re.compile(u'(?P<hour>\d+)小时(?P<minute>\d+)分钟')
			details = html.xpath('//div[@class="s_bd"]/table')[1]
			for stop in grouper([td.text_content().strip() for td in details.xpath('.//td')],7):
				tmp = pat.search(stop[5])
				if tmp:
					hour = int(tmp.group('hour'))
					minute = int(tmp.group('minute'))
					total_seconds = hour*3600+minute*60
				else: total_seconds=0

				if u'公里' in stop[6]: miles = int(stop[6][:-2])
				else: miles=0
				stop,created = MyTrainStop.objects.get_or_create(
					train_id = t_id,
					category = t_id[0],
					stop_index = int(stop[1]),
					stop_name = stop[2].strip(),
					arrival = self.parse_time(stop[3]),
					departure = self.parse_time(stop[4]),
					seconds_since_initial = total_seconds
				)
@shared_task
def train_consumer(train_id):
	http_agent = TorUtility()
	crawler = MyTrainCrawler(http_agent)
	crawler.parser(train_id)

from lxml.html.clean import clean_html
class MyCityWikiCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('gkp')

	def parser(self,city, province_id):
		# cleaner = Cleaner(style=True, links=True, add_nofollow=True,page_structure=False, safe_attrs_only=False)
		url = 'http://zh.wikipedia.org/wiki/%s'%city.encode('utf-8')
		content = self.http_handler.request(url)
		html = lxml.html.document_fromstring(content)
		wiki = html.xpath('//table[contains(@class, "infobox")]')
		if wiki:
			# remove all relative links that are linking back to wiki source
			for element, attribute, link, pos in wiki[0].iterlinks():
				if attribute == "href": element.set('href', 'http://zh.wikipedia.org'+element.get('href'))

			# reset img width
			for img in wiki[0].iter('img'):
				img.set('width','100%')

			html = clean_html(lxml.html.tostring(wiki[0]))
			city_obj = MyCity.objects.get(city = city, province = province_id)
			city_obj.wiki_intro = html
			city_obj.save()
			self.logger.info(city_obj.city+ ' saved')
		else: self.logger.info('Found nothing: '+city)

@shared_task
def city_wiki_consumer(city, province_id):
	http_agent = TorUtility()
	crawler = MyCityWikiCrawler(http_agent)
	crawler.parser(city, province_id)

class MyJobCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('gkp')

	def __del__(self):
		del self.http_handler
		
	def parser(self,keyword):
		major = MyMajor.objects.get(id = keyword)

		url = 'http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea=000000,00&funtype=0000&industrytype=00&keyword=%s&keywordtype=2&lang=c&stype=1&postchannel=0000&fromType=3' % urllib.quote(major.name.encode('utf-8'))
		content = self.http_handler.request(url)			
		html = lxml.html.document_fromstring(clean_html(content))
		summary = html.xpath('//table[contains(@class, "resultNav")]')
		total_count = 0
		if summary:
			summary = summary[0]
			for td in summary.xpath('.//td'):
				text = td.text_content()
				if '/' in text and '-' in text: 
					total_count = int(text.split('/')[1])
					major.job_stat = total_count
					major.save()					
					break
		self.logger.info(total_count)


		result_list = html.xpath('//table[contains(@class,"resultList")]')
		jobs = []
		for result in result_list:
			for job_name in html.xpath('.//a[contains(@class,"jobname")]'):
				# the comma is significant since we are defining a tuple!
				jobs.append((job_name.text_content().strip(),job_name.get('href')))
			for index, co_name in enumerate(html.xpath('.//a[contains(@class,"coname")]')):
				jobs[index] += (co_name.text_content().strip(),)
			for index, location in enumerate(html.xpath('.//tr[contains(@class,"tr0")]/td[contains(@class,"td3")]')):
				tmp = location.text_content().strip()
				if '-' in tmp: tmp=tmp[:tmp.find('-')]
				jobs[index] += (tmp,)
			for index, attributes in enumerate(html.xpath('.//tr[contains(@class,"tr1")]/td[contains(@class,"td1234")]')):
				req_degree = req_experience = co_type = co_size = ''
				for tmp in [t.strip() for t in attributes.text_content().strip().split('|')]:
					if tmp.startswith(u'学历要求'): req_degree = tmp[5:].strip()
					elif tmp.startswith(u'工作经验'): req_experience = tmp[5:].strip()
					elif tmp.startswith(u'公司性质'): co_type = tmp[5:].strip()
					elif tmp.startswith(u'公司规模'): co_size = tmp[4:].strip()
				jobs[index] += (req_degree,req_experience,co_type,co_size)

		for jobname, job_url, coname, location,req_degree,req_experience,co_type,co_size in jobs:
			job, created = MyJob.objects.get_or_create(source_url = job_url)
			if created:
				job.co_name = coname
				job.co_type = co_type
				job.co_size = co_size
				job.title = jobname
				job.location = location
				job.req_degree = req_degree
				job.req_experience = req_experience
				job.save()
			job.majors.add(major)

			#self.logger.info(','.join([jobname,coname]))
			#self.logger.info(job_url)
			#self.logger.info(','.join([coname,location,req_degree,req_experience,co_type,co_size]))

from gaokao.tor_handler import SeleniumUtility
@shared_task
def job_consumer(major):
	http_agent = SeleniumUtility()
	crawler = MyJobCrawler(http_agent)
	crawler.parser(major)
	del crawler

import codecs
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class MySogouCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('gkp')
		
	def parser(self,id):
		'''
			type=1: webchat account search
			type=2: webchat article search

			tsn=1: in 1 day
			tsn=2: in 1 week
			tsn=3: in 1 month
			tsn=4: in 1 year
		'''
		school = MySchool.objects.get(id=id)

		# STEP 1: get weixin account
		url = "http://weixin.sogou.com/weixin?type=1&query=%s&fr=sgsearch&ie=utf8" % urllib.quote(school.name.encode('utf-8'))
		#content = self.http_handler.request(url)
		content = self.http_handler.request(url).decode('utf-8')
		html = lxml.html.document_fromstring(clean_html(content))

		total_page = html.xpath('//div[@id="pagebar_container"]/a')
		total_page = len(total_page)
		print total_page

		for page in range(1,total_page):
			url = "http://weixin.sogou.com/weixin?type=1&query=%s&fr=sgsearch&ie=utf8&page=%d" % (urllib.quote(school.name.encode('utf-8')),page)
			#content = self.http_handler.request(url)
			content = self.http_handler.request(url).decode('utf-8')
			html = lxml.html.document_fromstring(clean_html(content))

			for result in html.xpath('//div[contains(@class,"results")]/div'):
				name = result.xpath('.//h3')[0].text_content().strip()
				
				# we only save ones that have full school name in it
				if school.name not in name: continue

				source_url = result.get('href')
				account_id = result.xpath('.//h4')[0].text_content().strip().split(u'：')[1]
				description = result.xpath('.//span[contains(@class,"sp-txt")]')[0].text_content().strip()
				wx, created = MyWeixinAccount.objects.get_or_create(account = account_id,name=name)
				wx.school = school
				wx.description = description
				wx.sg_url = 'http://weixin.sogou.com%s'%source_url
				wx.save()

				# images
				icon_url = result.xpath('.//div[contains(@class,"img-box")]/img')[0].get('src')
				img_data = None
				try: img_data = self.http_handler.request(icon_url)
				except: self.logger.error('retrieve img failed: %s' % icon_url)
				if img_data:
					print 'writing icon image data'
					tmp_file = NamedTemporaryFile(suffix='.jpg',delete=False)
					tmp_file.write(img_data)
					wx.icon = File(tmp_file)
					wx.save()
					tmp_file.close()

				barcode_url = 'http://www.vchale.com/uploads/ewm/%s.jpg'%account_id
				img_data = None
				try: img_data = self.http_handler.request(barcode_url)
				except: self.logger.error('retrieve img failed: %s' % icon_url)
				if img_data:
					print 'writing barcode image data'				
					tmp_file = NamedTemporaryFile(suffix='.jpg',delete=False)
					tmp_file.write(img_data)
					wx.barcode = File(tmp_file)
					wx.save()
					tmp_file.close()

				print wx.name, 'done'
		return

		# STEP 2: get articles
		url = "http://weixin.sogou.com/weixin?type=2&query=%s&fr=sgsearch&ie=utf8&tsn=2&interation=" % urllib.quote(school.name.encode('utf-8'))
		# WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.&interation=1ID,'searchinput')))

		# WARNING: if using TorUtility, must decode here!
		content = self.http_handler.request(url).decode('utf-8')
		#content = self.http_handler.request(url)

		#self.logger.info('Ready to parse')
		html = lxml.html.document_fromstring(clean_html(content))
		for result in html.xpath('//div[@class="results"]/div'):
			tweet_title = ''
			tweet_url = ''
			title = result.xpath('.//h4/a')
			if title:
				tweet_title = title[0].text_content()
				tweet_url = title[0].get('href')

			tweet_summary = result.xpath('.//p')
			if tweet_summary: tweet_summary = tweet_summary[0].text_content()

			img_url = ''
			img = result.xpath('.//div[@class="img_box2"]//img')
			if img: img_url = 'http://'+img[0].get('src').split('http://')[-1]

			author_id = ''
			author = result.xpath('.//a[@id="weixin_account"]')
			if author: 
				author_id = author[0].get('title')

			timestamp = ''
			t = result.xpath('.//div[contains(@class,"s-p")]')
			if t: 
				timestamp = t[0].text_content().strip()
				timestamp = timestamp[len(author_id):]


@shared_task
def sogou_consumer(keyword):
	http_agent = TorUtility()
	crawler = MySogouCrawler(http_agent)
	crawler.parser(keyword)

class MyHudongWikiCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('gkp')

	def parser(self,school_id):
		school = MySchool.objects.get(id = school_id)
		# cleaner = Cleaner(style=True, links=True, add_nofollow=True,page_structure=False, safe_attrs_only=False)
		url = 'http://www.baike.com/wiki/%s'%school.name.encode('utf-8')
		content = self.http_handler.request(url)
		html = lxml.html.document_fromstring(content)
		wiki = html.xpath('//div[@id="content"]')
		if wiki:
			school.hudong = clean_html(lxml.html.tostring(wiki[0]))
			school.save()
			self.logger.info(school.name+ ' saved')
		else: self.logger.info('Found nothing: '+city)

@shared_task
def hudong_wiki_consumer(school_id):
	http_agent = TorUtility()
	crawler = MyHudongWikiCrawler(http_agent)
	crawler.parser(school_id)