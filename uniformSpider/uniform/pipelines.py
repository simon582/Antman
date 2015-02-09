# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
#coding=utf-8
import pymongo
from scrapy import log
import time
import sys
sys.path.append('../comm_lib')
import os
import utils
MONGODB_SAFE = False
MONGODB_ITEM_ID_FIELD = "_id"
class UniformPipeline(object):
    def __init__(self, mongodb_server, mongodb_port, mongodb_db, mongodb_collection, mongodb_temp_collection, mongodb_uniq_key,
                 mongodb_item_id_field, mongodb_safe):
        connection = pymongo.Connection(mongodb_server, mongodb_port)
        self.mongodb_db = mongodb_db
        self.db = connection[mongodb_db]
        self.mongodb_collection = mongodb_collection
        self.collection = self.db[mongodb_collection]
        self.temp_collection = self.db[mongodb_temp_collection]
        self.uniq_key = mongodb_uniq_key
        self.itemid = mongodb_item_id_field
        self.safe = mongodb_safe
        self.result_dict = {}
        self.processed_item = {}
        self.count = 0

    def open_spider(self,spider):
        cursor = self.collection.find({},{'id':1})
        for item in cursor:
            self.processed_item[item['id']] = 1
        log.msg('get result num[%d] from db'%len(self.processed_item),level=log.WARNING)

    def process_item(self, item, spider):
        if item['id'] not in self.processed_item:
            self.count += 1
            self.temp_collection.update({'id':item['id']},{'$set': dict(item)},upsert=True, safe=True)
        else:
            log.msg('skip update item because has existed. '+item['id'], level=log.WARNING)
        return item

    @classmethod
    def get_temp_table_name(cls, crawler):
        settings = crawler.settings
        if os.path.exists('temp_table'):
            return open('temp_table').read().strip()
        else:
            return settings.get('MONGODB_TEMP_COLLECTION', None)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.get('MONGODB_SERVER', 'localhost'), settings.get('MONGODB_PORT', 27037),
            settings.get('MONGODB_DB', 'scrapy'), settings.get('MONGODB_COLLECTION', None), cls.get_temp_table_name(crawler), 
            settings.get('MONGODB_UNIQ_KEY', None), settings.get('MONGODB_ITEM_ID_FIELD', MONGODB_ITEM_ID_FIELD),
            settings.get('MONGODB_SAFE', MONGODB_SAFE))

    def close_spider(self,spider):
        #for (id,item) in self.result_dict.items():
        #    self.collection.update({self.uniq_key: item[self.uniq_key] }, {'$set':dict(item) },upsert=True, safe=self.safe)
        if spider.driver:
            utils.driver_quit(spider.driver)
            spider.log('driver.quit()', level = log.DEBUG)
        pass
