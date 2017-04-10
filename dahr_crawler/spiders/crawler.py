#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from math import ceil
from scrapy.spider import Spider
from scrapy.http import Request
from scrapy.log import start
from dahr_crawler.items import Item
from datetime import datetime

class DAHRSpider(Spider):
	def __init__(self):
		LOG_FILE = "../LOG/" + datetime.now().strftime('%Y-%m-%d') + ".txt"
		#LOG_FILE = "dahr_crawler/LOG/" + datetime.now().strftime('%Y-%m-%d') + ".txt"
		start(logfile=LOG_FILE, loglevel='DEBUG', logstdout=False)

	name = "DAHR" # name for crawler, run as "scrapy crawl DAHR"
	base_url = "http://adp.library.ucsb.edu"
	allowed_domains = []
	start_urls = [
		"http://adp.library.ucsb.edu/index.php/objects/index",           # url of Browse/Discs page
	]

	# pre-compiled regex list
	remove_table = re.compile(ur'\n|\t|\r|</?tr[^>]*>|<td([^>]*)>|\xa0') # remove html table tags
	get_link = re.compile(r'a href="([^>]*)">([^<]*)')                   # parse url link in <a> tag
	remove_tag = re.compile(r'<[^>]*>')									 # remove all html tags

	# parse pagination
	def parse(self, response):
		# calculate the number of pages
		total_label = re.findall(r'Results .* of (\d+)', response.xpath('//html').extract()[0])[0]
		pagination = int(ceil(int(total_label)/50.0))					# 50 entries per page
		# loop through pagination
		for i in xrange(pagination):
			next_link = self.base_url + ("/index.php/objects/index?Objects_page=%s" % str(i+1))
			yield Request(url=next_link, callback=self.parse_disc)
		return

	# Browse Discs level parser
	def parse_disc(self, response):
		discs = response.xpath('//tbody/tr').extract()
		# loop through all label entries
		for disc in discs:
			# collect info for each disc entry
			disc = self.remove_table.sub('',disc).split('</td>')[:3]
			disc_link, disc_name = self.get_link.findall(disc[0])[0]
			if disc_name == '': continue

			# build request for Label/Matrix page
			request = Request(url=self.base_url + disc_link, callback=self.parse_label)
			request.meta['label_name'] = disc_name
			request.meta['label_format'] = disc[1]
			request.meta['label_issue_date'] = disc[2]
			yield request
		return

	# Label/Matrix level parser
	def parse_label(self, response):
		matrices = response.xpath('//table[position()=1]/tr').extract()[1:]
		# loop through all matrix entries
		for matrix in matrices:
			# collect info for each matrix entry
			matrix = self.remove_table.sub('', matrix).split('</td>')
			matrix_link, matrix_number = self.get_link.findall(matrix[1])[0]

			# build request for details page
			request = Request(url=self.base_url + matrix_link, callback=self.parse_matrix, dont_filter=True)
			request.meta.update(response.request.meta)
			request.meta['matrix_company'] = matrix[0].strip()
			request.meta['matrix_number'] = matrix_number
			request.meta['matrix_take_number'] = matrix[2].strip()
			request.meta['matrix_date'] = matrix[3].strip()
			request.meta['matrix_description'] = matrix[4].strip()
			yield request
		return

	# Matrix level parser
	def parse_matrix(self, response):
		# parse necessary info from tables
		# upper left table
		authors = response.xpath('//div[@id="info-left"]/table/tr[not(contains(@class,"personnel"))]/td/a').extract()
		authors = [self.remove_tag.sub('',a) for a in authors]
		try:
			composer_source = response.xpath('//div[@id="info-left"]/table/tr/td[@class="composer-statement"]/text()').extract()[0]
			composer_source = composer_source.replace("Composer information source:", '').strip().strip('.')
		except IndexError:
			# page did not provide Composer information source
			composer_source = ''
		personnel = response.xpath('//div[@id="info-left"]/table/tr[contains(@class,"personnel")]/td/a').extract()
		personnel = [self.remove_tag.sub('', p) for p in personnel]

		# upper right table
		info = dict()
		additional_info = response.xpath('//div[@id="info-right"]/ul/li').extract()
		additional_info = [self.remove_tag.sub('', i) for i in additional_info]
		for i in additional_info:
			key, val = tuple(i.split(':', 1))
			info[key.strip()] = val.strip()
		notes = ' '.join(response.xpath('//div[@id="info-right"]/table/tr/td/text()').extract())

		# takes table
		takes_info = response.xpath('//tr[contains(@class,"takes")]').extract()
		takes_info = [self.remove_table.sub('', t).split('</td>') for t in takes_info]
		takes = []
		for t in takes_info:
			t = [re.sub(r'<(?!/)[^>]*>','', i).strip() for i in t]
			front = [i.strip() for i in t[0].split('</a>')] if '</a>' in t[0] else ['', t[0].strip()] # date and location
			t = front + [self.remove_tag.sub('', i) for i in t[1:5]]
			takes.append(t)
		# order of list t : `take date, take place, take, status, label name, format` accordingly

		# build processed item
		item = Item()
		# disc info
		item['label_name'] = response.request.meta['label_name']
		item['label_format'] = response.request.meta['label_format']
		item['label_issue_date'] = response.request.meta['label_issue_date']
		# matrix info
		item['matrix_company'] = response.request.meta['matrix_company']
		item['matrix_number'] = response.request.meta['matrix_number']
		item['matrix_take_number'] = response.request.meta['matrix_take_number']
		item['matrix_date'] = response.request.meta['matrix_date']
		item['matrix_description'] = response.request.meta['matrix_description']
		# matrix detail
		item['authors'] = authors
		item['composer_source'] = composer_source
		item['personnel'] = personnel
		item['note'] = notes
		item['info'] = info
		item['takes'] = takes

		return item
