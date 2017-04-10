# -*- coding: utf-8 -*-

# Scrapy settings for dahr project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'dahr_crawler'

SPIDER_MODULES = ['dahr_crawler.spiders']
NEWSPIDER_MODULE = 'dahr_crawler.spiders'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36'
ITEM_PIPELINES = {
	'dahr_crawler.pipelines.Pipeline': 0,
}

DEFAULT_ITEM_CLASS = 'scrapy.item.Item'
DEFAULT_REQUEST_HEADERS = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

# log setting
LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
LOG_LEVEL = 'INFO'
LOG_STDOUT = False

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'dahr (+http://www.yourdomain.com)'
