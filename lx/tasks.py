# -*- coding: utf-8 -*- 
from __future__ import absolute_import

from celery import shared_task

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
import lxml.html 
from lxml.html.clean import clean_html, Cleaner

from gaokao.tor_handler import TorUtility, SeleniumUtility, PlainUtility
from lx.models import *

# create logger with 'spam_application'
logger = logging.getLogger('lx')
logger.setLevel(logging.DEBUG)

class MySEVISCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('lx')

	def parser(self,id):
		# cleaner = Cleaner(style=True, links=True, add_nofollow=True,page_structure=False, safe_attrs_only=False)
		school = MySEVISSchool.objects.get(campus_id = id)
		url = 'http://studyinthestates.dhs.gov/certified-school/%d'%id
		self.logger.info(url)
		self.logger.info(school.name)

		if not school.raw_html:
			self.logger('Grabbing raw')
			try: content = self.http_handler.request(url)
			except:
				self.logger.error(url)
				return

			html = lxml.html.document_fromstring(content)
		else: 
			self.logger.info('We have raw')
			html = lxml.html.document_fromstring(school.raw_html)

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

class MySchoolWikiCrawler():
	def __init__(self,handler):
		self.http_handler = handler
		self.logger = logging.getLogger('lx')

	def parser(self,id):
		# cleaner = Cleaner(style=True, links=True, add_nofollow=True,page_structure=False, safe_attrs_only=False)
		school = MySEVISSchool.objects.get(id = id)
		url = 'http://en.wikipedia.org/wiki/%s'%urllib.quote(school.name)
		self.logger.info('%d, %d: %s' %(school.id, school.campus_id, school.name))

		content = self.http_handler.request(url)
		html = lxml.html.document_fromstring(content)

		wiki = html.xpath('//div[@id="mw-content-text"]')
		if wiki:
			for quick in wiki[0].xpath('.//table[contains(@class,"infobox")]'):
				school.wiki_quick_facts = lxml.html.tostring(quick[0],pretty_print=True)
				quick.getparent().remove(quick)
				break # we only want the 1st one!!

			# remove all "metadata" which usually goes like 
			for meta in wiki[0].xpath('.//*[contains(@class,"metadata")]'):
				meta.getparent().remove(meta)

			# remove all [edit] link
			for edit in wiki[0].xpath('.//*[contains(@class,"mw-editsection")]'):
				edit.getparent().remove(edit)

			# remove TOC toggle
			for toc_toggle in wiki[0].xpath('.//*[contains(@class,"toctoggle")]'):
				toc_toggle.getparent().remove(toc_toggle)

			# remove references section
			for ref in wiki[0].xpath('.//*[@id="References"]'):
				ref.getparent().remove(ref)
			for ref in wiki[0].xpath('.//*[contains(@class,"reflist")]'):
				ref.getparent().remove(ref)

			# remove navbox
			for navbox in wiki[0].xpath('.//*[contains(@class,"navbox")]'):
				navbox.getparent().remove(navbox)

			# remove coordinates
			for coordinate in wiki[0].xpath('.//*[@id="coordinates"]'):
				coordinate.getparent().remove(coordinate)

			# remove toc. We'll generate this later.
			for toc in wiki[0].xpath('.//*[@id="toc"]'):
				toc.getparent().remove(toc)

			# remove jump to top link
			for toc_top in wiki[0].xpath('.//*[contains(@class,"toc-top-link")]'):
				toc_top.getparent().remove(toc_top)
				self.logger.info('Removing toc_top')

			# strip tags
			# lxml.etree.strip_tags(wiki[0],'noscript')

			# remove sistersite
			for sister in wiki[0].xpath('.//*[contains(@class,"sistersitebox")]'):
				if sister.getparent(): sister.getparent().remove(sister)

			# clean up table class
			for tag in html.xpath('//table'):
			    tag.attrib['class'] = 'table'		
			
			# clean up empty tags

			school.wiki = lxml.html.tostring(wiki[0],pretty_print=True)
		school.save()

@shared_task
def school_wiki_consumer(id):
	http_agent = SeleniumUtility(use_tor = False)
	crawler = MySchoolWikiCrawler(http_agent)
	crawler.parser(id)	