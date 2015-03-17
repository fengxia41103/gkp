#!/usr/bin/python  
# -*- coding: utf-8 -*- 
import sys,time,os,gc,csv
import lxml.html
import urllib, urllib2
import simplejson as json
import pytz
import socks
import socket
from stem import Signal
from stem.control import Controller

# setup Django
import django
sys.path.append(os.path.join(os.path.dirname(__file__), 'gaokao'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gaokao.settings")
from django.conf import settings

from django.utils import timezone
# import models
from pi.models import *
from pi.crawler import MyBaiduCrawler

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

class MyBaiduCrawler():
	def __init__(self):
		self.tor_util = TorUtility()

	def tieba(self,keyword):
		baidu_url = 'http://tieba.baidu.com/f?kw=%s&ie=utf-8'%urllib.quote(keyword.encode('utf-8'))		
		content = self.tor_util.request(baidu_url)
		html = lxml.html.document_fromstring(content)

		threads = []
		for t in html.xpath('//li[contains(@class, "j_thread_list")]'):
			stats = json.loads(t.get('data-field'))
			if stats['is_top'] or not stats['reply_num']: continue  # sticky posts, always on top, so we skip these

			# basic thread infos
			this_thread = {
				'source':'百度贴吧',
				'author': stats['author_name'],
				'author_id':stats['id'],
				'url':'http://tieba.baidu.com/p/%d' % stats['id'],
				'reply_num': stats['reply_num'],
				'title': t.xpath('.//a[contains(@class,"j_th_tit")]')[0].text_content().strip(), # post title line
				'abstract': t.xpath('.//div[contains(@class,"threadlist_abs_onlyline")]')[0].text_content().strip(), # post abstracts
				'last_timestamp': t.xpath('.//span[contains(@class,"threadlist_reply_date")]')[0].text_content().strip()
			}

			imgs = []
			for i in t.xpath('.//img[contains(@class,"threadlist_pic")]'):
				imgs.append(i.get('original'))
				#imgs.append(i.get('bpic')) # this is full size pic, has to save locally first. Link to Baidu won't work.
			this_thread['imgs']=imgs

			# add to list
			threads.append(this_thread)

		return threads

def baidu_crawler():
	print 'Queue size', MyCrawlerRequest.objects.count()

	reqs = MyCrawlerRequest.objects.all().order_by('-created').values('source','params')[:10]
	targets = list(set([(t['source'],t['params']) for t in reqs]))

	for req in targets:
		if req[0] == 1: # baidu tieba
			params = json.loads(req[1])
			school = MySchool.objects.get(name=params['keyword'])
			results = MyBaiduCrawler().tieba(params['keyword'])
			for t in results:
				# make django's timezone-aware timestamp
				if ':' in t['last_timestamp']:
					tmp = t['last_timestamp'].split(':')
					now = timezone.now()
					post_timestamp = dt(now.year,now.month,now.day,int(tmp[0]),int(tmp[1]))
					post_timestamp = pytz.timezone(timezone.get_default_timezone_name()).localize(post_timestamp)
				else: post_timestamp = None

				# create records in DB
				data,created = MyBaiduStream.objects.get_or_create(
					school = school,
					author = t['author'],
					url_original = t['url'],
					reply_num = t['reply_num'],
					name = t['title'][:64],
					description = t['abstract'],
				)
				if post_timestamp: 
					data.last_updated=post_timestamp
					data.save()

			# clear queue for all other requests since data have been updated
			for m in MyCrawlerRequest.objects.filter(source=req[0],params=req[1]):
				m.delete()

def main():
	django.setup()
	baidu_crawler()
	
if __name__=='__main__':
	main()