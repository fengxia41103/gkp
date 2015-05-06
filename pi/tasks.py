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
import codecs
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import re
from datetime import timedelta
from itertools import izip_longest

from gaokao.tor_handler import *
from pi.models import *
from lx.models import *

# create logger with 'spam_application'
logger = logging.getLogger('gkp')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
# fh = logging.FileHandler('/tmp/gkp.log')
# fh.setLevel(logging.DEBUG)

# # create console handler with a higher log level
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)

# # create formatter and add it to the handlers
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# ch.setFormatter(formatter)
# # add the handlers to the logger
# logger.addHandler(fh)
# logger.addHandler(ch)

def grouper(iterable, n, padvalue=None):
	# grouper('abcdefg', 3, 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')
	return list(izip_longest(*[iter(iterable)]*n, fillvalue=padvalue))

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


@shared_task
def baidu_consumer(param):
	#http_agent = PlainUtility(http_manager)
	http_agent = TorUtility()
	'The test task executed with argument "%s" ' % json.dumps(param)
	crawler = MyBaiduCrawler(http_agent)
	crawler.parser(param)


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
		html = lxml.html.document_fromstring(clean_html(content))
		wiki = html.xpath('//table[contains(@class, "infobox")]')
		if wiki:
			# remove all relative links that are linking back to wiki source
			for element, attribute, link, pos in wiki[0].iterlinks():
				if attribute == "href": element.set('href', 'http://zh.wikipedia.org'+element.get('href'))

			# reset img width
			for img in wiki[0].iter('img'):
				img.set('width','100%')

			html = lxml.html.tostring(wiki[0])
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

@shared_task
def job_consumer(major):
	http_agent = SeleniumUtility()
	crawler = MyJobCrawler(http_agent)
	crawler.parser(major)
	del crawler

class MySogouCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.retriever = PlainUtility()
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
		# url = "http://weixin.sogou.com/weixin?type=1&query=%s&fr=sgsearch&ie=utf8" % urllib.quote(school.name.encode('utf-8'))
		url = 'http://weixin.sogou.com/weixin?type=1&query=%s&fr=sgsearch&ie=utf8&_ast=1430486528&_asf=null&w=01029901&cid=null'% urllib.quote(school.name.encode('utf-8'))

		# uncomment .decode('utf-8') if using TorUtility		
		content = self.http_handler.request(url)
		#content = self.http_handler.request(url).decode('utf-8')

		html = lxml.html.document_fromstring(clean_html(content))
		no_result = html.xpath('//div[@id="noresult_part1_container"]')
		if len(no_result): 
			print school.name, 'no result'
			return # no result

		total_page = html.xpath('//div[@id="pagebar_container"]/a')
		total_page = len(total_page)
		if not total_page: total_page = 2 # we are counting from 1

		for page in range(1,total_page):
			url = "http://weixin.sogou.com/weixin?type=1&query=%s&fr=sgsearch&ie=utf8&page=%d" % (urllib.quote(school.name.encode('utf-8')),page)

			content = self.http_handler.request(url)
			#content = self.http_handler.request(url).decode('utf-8')
			html = lxml.html.document_fromstring(clean_html(content))

			for result in html.xpath('//div[contains(@class,"results")]/div'):
				name = result.xpath('.//h3')[0].text_content().strip()
				self.logger.info('Found %s'%name)

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
				if created:	self.logger.info('%s added'%name)
				else: self.logger.info('%s updated'%name)

				# we already have the barcode
				if len(wx.attachments.all()): continue

				# images
				icon_url = result.xpath('.//div[contains(@class,"img-box")]/img')[0].get('src')
				img_data = None
				try: img_data = self.retriever.request(icon_url)
				except: self.logger.error('retrieve img failed: %s' % icon_url)
				if img_data:
					print 'writing icon image data'
					tmp_file = NamedTemporaryFile(suffix='.jpg',delete=False)
					tmp_file.write(img_data)
					wx.icon = File(tmp_file)
					wx.save()
					tmp_file.close()

				barcode_url = 'http://www.vchale.com/uploads/ewm/%s.jpg'%account_id
				# barcode_url = result.xpath('.//div[contains(@class,"pos-box")]/img')[0].get('src')
				img_data = None
				try: img_data = self.retriever.request(barcode_url)
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
	http_agent = SeleniumUtility(use_tor=False)
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
		# url = 'http://www.baike.com/wiki/%s'%school.name

		content = self.http_handler.request(url)
		try: html = lxml.html.document_fromstring(content)
		except: 
			self.logger.info(school.name)
			return

		wiki = html.xpath('//div[@id="content"]')
		if wiki:
			for img in wiki[0].xpath('.//img'):
				img.attrib['src'] = img.get('data-original')
			school.hudong = lxml.html.tostring(wiki[0])
			school.hudong_raw_html = content
		else: self.logger.info('Found nothing: '+school.name)
		
		summary_table = html.xpath('.//div[@id="datamodule"]//table')
		if summary_table: school.hudong_summary_table = lxml.html.tostring(summary_table[0])
		toc = html.xpath('.//fieldset[@id="catalog"]')
		if toc: school.hudong_toc = lxml.html.tostring(toc[0])
		school.save()
		self.logger.info(school.name+ ' saved')

@shared_task
def hudong_wiki_consumer(school_id):
	http_agent = TorUtility()
	crawler = MyHudongWikiCrawler(http_agent)
	crawler.parser(school_id)

class MySEVISCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('gkp')

	def parser(self,id):
		# cleaner = Cleaner(style=True, links=True, add_nofollow=True,page_structure=False, safe_attrs_only=False)
		url = 'http://studyinthestates.dhs.gov/certified-school/%d'%id
		self.logger.info(url)

		try: content = self.http_handler.request(url)
		except:
			self.logger.error(url)
			return

		html = lxml.html.document_fromstring(content)

		try: school_name = html.xpath('//h1[@id="page-title"]')[0].text_content().strip()
		except: return # we don't have a school name, could be "page not found"

		zip_pat = re.compile('\d+')

		for info in html.xpath('//div[@id="school-info"]'):
			campus = html.xpath('.//p[contains(@class,"lead")]')
			if campus: campus = campus[0].text_content().strip()
			else: campus = ''

			# address
			mailing = physical = ''
			mailing_zip = physical_zip = None
			sevis_mailing = sevis_physical = None
			for p in html.xpath('.//p')[-3:-1]:
				tmp = filter(lambda x: x.strip(), p.text_content().split('\n'))

				if 'Mailing' in tmp[0]:
					mailing = ','.join([a.strip() for a in tmp[1:-1]])
					mailing_zip = tmp[-1]
					# self.logger.info(mailing_zip)

					if zip_pat.search(mailing_zip):
						mailing_zip = zip_pat.search(mailing_zip).group(0)
						try: mailing_zip = MyZip.objects.get(zipcode = mailing_zip)
						except:
							mailing_zip = None
							self.logger.error('Invalid mailing_zip!')
							sevis_mailing = tmp[-1]
					else:
						mailing_zip = None
						sevis_mailing = tmp[-1]

				elif 'Physical' in tmp[0]:
					physical = ','.join([a.strip() for a in tmp[1:-1]])
					physical_zip = tmp[-1]
					# self.logger.info(physical_zip)

					if zip_pat.search(physical_zip):
						physical_zip = zip_pat.search(physical_zip).group(0)
						try: physical_zip = MyZip.objects.get(zipcode = physical_zip)
						except:
							physical_zip = None
							self.logger.error('Invalid physical_zip!')
							sevis_physical = tmp[-1]
					else:
						physical_zip = None
						sevis_physical = tmp[-1]

			# visa type
			for school_type in html.xpath('.//div[@id="school-type"]'):
				if html.xpath('.//span[contains(@class,"f-1")]'): f_1 = True
				else: f_1 = False

				if html.xpath('.//span[contains(@class,"m-1")]'): m_1 = True
				else: m_1 = False

			if len(MySEVISSchool.objects.filter(campus_id = int(id))) < 1:
				MySEVISSchool(
					raw_html = content, # let's try not to crawl that site again!
					name = school_name,
					campus = campus,
					campus_id = int(id),
					f_1 = f_1,
					m_1 = m_1,
					mailing_address = mailing,
					physical_address = physical,
					mailing_zip = mailing_zip,
					physical_zip = physical_zip,
					sevis_mailing = sevis_mailing,
					sevis_physical = sevis_physical
				).save()
			elif school:
				school.name = school_name
				school.campus = campus
				school.raw_html = content,
				school.f_1 = f_1
				school.m_1 = m_1
				school.mailing_address = mailing
				school.physical_address = physical
				school.mailing_zip = mailing_zip
				school.physical_zip = physical_zip
				school.sevis_mailing = sevis_mailing
				school.sevis_physical = sevis_physical
				school.save()
			self.logger.info(school_name + ' done')
		# print school_name, campus, f_1, m_1

@shared_task
def sevis_consumer(id):
	http_agent = SeleniumUtility()
	crawler = MySEVISCrawler(http_agent)
	crawler.parser(id)

class MyBaiduImageCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('gkp')

	def parser(self,keyword,save_to,min_width=800):
		url = 'http://image.baidu.com/i?tn=baiduimagejson&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1430450474499_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=800&height=&face=0&istype=2&ie=utf-8&rn=20&word=%s'%keyword.encode('utf-8')
		self.logger.info(url)

		result = self.http_handler.request(url)
		data = json.loads(result,'latin-1')['data']
		total_items = len(data)
		blacklist = ['gkcx']
		for d in data:
			if 'width' in d and d['width'] < min_width: continue
			link = d['objURL']

			# black list these sites
			if filter(lambda x: x in link, blacklist): continue

			# download image
			try: 
				img = self.http_handler.request(link)
				with open('%s%s.jpg'%(save_to,keyword),'w') as f:
					f.write(img)
				print keyword, 'done'
				break
			except: continue

@shared_task
def baidu_image_consumer(keyword,save_to):
	http_agent = PlainUtility()
	crawler = MyBaiduImageCrawler(http_agent)
	crawler.parser(keyword,save_to)

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from random import shuffle
class MyGKPPlanCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.agent = handler.agent
		self.logger = logging.getLogger('gkp')

	def wait_for_presence(self,by_what,val, wait_length=15):
		WebDriverWait(self.agent,wait_length).until(EC.presence_of_element_located((by_what,val)))

	def wait_for_invisible(self,by_what,val, wait_length=15):
		WebDriverWait(self.agent,wait_length).until(EC.invisibility_of_element_located((by_what,val)))

	def parser(self,id):
		url = 'http://www.gaokaopai.com/daxue-zhaosheng-%d.html'%id
		self.logger.debug(url)
		content = self.http_handler.request(url)

		states = [11,12,13,14,15,21,22,23,31,32,33,34,35,36,37,41,42,43,44,45,46,50,51,52,53,54,61,62,63,64,65]
		shuffle(states)

		# for cat in self.agent.find_elements_by_xpath("//*[@data-id='1']"):
		for cat in [1,2]:			
			self.agent.execute_script("$.setVar('claimSubType', %d);"%cat)

			# for state in self.agent.find_elements_by_xpath("//*[@data-id='2']"):
			for state in states:
				self.agent.execute_script("$(arguments[0]).click();", state)

				search_btn = self.agent.find_element_by_xpath('//*[contains(@class,"mlSearch")]')
				search_btn.click()
				self.logger.debug('activating search')

				self.wait_for_presence(By.XPATH,"//*[contains(text(),'loading')]")
				self.logger.debug('loading')

				self.wait_for_invisible(By.XPATH,"//*[contains(text(),'loading')]")
				self.logger.debug('loading complete')
				
				self.logger.debug('selecting cat: %d'%cat)
				self.logger.debug('selecting state: %d'%state)				
				tds = self.agent.find_elements_by_xpath('//*[@class="claimContent"]/descendant::td')
				self.logger.debug(len(tds))

				for tr in grouper([t.text for t in tds],6,''):
					self.logger.debug('-'.join(tr))
					break

@shared_task
def gkp_plan_consumer(id):
	http_agent = SeleniumUtility(use_tor=True) # has to use Selenium for this one
	crawler = MyGKPPlanCrawler(http_agent)
	crawler.parser(id)	