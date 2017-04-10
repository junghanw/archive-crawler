# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class Item(Item):
	# from 'browse discs' page
	label_name = Field()
	label_format = Field()
	label_issue_date = Field()

	# from pages for each disc/label
	matrix_company = Field()
	matrix_number = Field()
	matrix_take_number = Field()
	matrix_date = Field()
	matrix_description = Field()

	# from detail pages
	authors = Field()
	composer_source = Field()
	personnel = Field()
	info = Field()
	note = Field()
	takes = Field()



