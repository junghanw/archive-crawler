#!/usr/bin/python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys,os
import unicodecsv
from dahr_crawler.items import Item
from datetime import datetime
from collections import defaultdict


class Pipeline(object):
	def __init__(self):
		date = datetime.now().strftime('%Y-%m-%d')
		path = "../CSV/%s" % date
		#path = "dahr_crawler/CSV/%s" % date
		if not os.path.exists(path):
			os.makedirs(path)
		self.path = path
		self.rows = list()
		# csv header informations
		self.authors_num = 0
		self.personnels_num = 0
		self.takes_num = 0
		self.info_list = list()

	# when spider closes, i.e. crawl finishes
	# build header row with header information
	# save all rows to csv file, located under `CSV` folder
	def close_spider(self, spider):
		print "--------------------NOW SAVING--------------------------"
		# make header for csv file
		header = [
			# From `Browse Discs` pages
			"label_name", "label_format", "label_issue_date",
			# From pages fro Each Disc/Label
			"matrix_number", "matrix_company", "matrix_date", "matrix_take_number", "matrix_description",
			]
		header += ["author_" + str(i+1) for i in xrange(self.authors_num)]
		header += ["composer_source"]
		header += self.info_list
		header += ["personnel_" + str(i+1) for i in xrange(self.personnels_num)]
		header += ["note"]
		for i in xrange(self.takes_num):
			n = str(i+1)
			header += ["Take Date "+n, "Take Place "+n, "Take "+n, "Status "+n, "Label Name "+n, "Format "+n]

		# save rows into csv file
		date = datetime.now().strftime('%H:%M')
		filename = "%s/%s.csv" % (self.path, date)
		csv_file = open(filename, 'wb')
		w = unicodecsv.DictWriter(csv_file,header,restval="",extrasaction="raise", delimiter=',', quotechar='"', encoding='utf-8')
		w.writeheader()
		w.writerows(self.rows)
		csv_file.close()
		return

	# returned item from spider is processed in this function
	# update header information and build csv row dict
	def process_item(self, item, spider):
		# update number parameters
		if len(item['authors']) > self.authors_num:
			self.authors_num = len(item['authors'])
		if len(item['personnel']) > self.personnels_num:
			self.personnels_num = len(item['personnel'])
		if len(item['takes']) > self.takes_num:
			self.takes_num = len(item['takes'])
		for k in item['info'].keys():
			if k not in self.info_list:
				self.info_list.append(k)

		# build individual row with all authors, personnels, descriptions, takes
		row = defaultdict(list)
		for k in item.keys():
			if k == 'authors':
				for i in xrange(len(item['authors'])):
					row["author_"+str(i+1)] = item['authors'][i]
			elif k == 'personnel':
				for i in xrange(len(item['personnel'])):
					row["personnel_"+str(i+1)] = item['personnel'][i]
			elif k == 'info':
				for i_k in item['info'].keys():
					row[i_k] = item['info'][i_k]
			elif k == 'takes':
				for i in xrange(len(item['takes'])):
					n = str(i+1)
					row["Take Date "+n] = item['takes'][i][0]
					row["Take Place "+n] = item['takes'][i][1]
					row["Take "+n] = item['takes'][i][2]
					row["Status "+n] = item['takes'][i][3]
					row["Label Name "+n] = item['takes'][i][4]
					row["Format "+n] = item['takes'][i][5]
			else:
				row[k] = item[k]

		# add row to entire set of rows
		self.rows.append(row)

		return
