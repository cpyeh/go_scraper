# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs

class GoScraperPipeline(object):

    def process_item(self, item, spider):
        item = json.dumps(dict(item), ensure_ascii=False) + "\n"
        return item
