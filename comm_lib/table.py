#!/usr/bin/python
#encoding=utf8
__author__ = 'luoyan@maimiaotech.com'
import sys 
import os 
import logging 
import logging.config
logger = logging.getLogger(__name__)
from Searcher.conf.settings import mongoConn
import traceback
import pymongo
if pymongo.version.startswith("2.5"):
    import bson.objectid
    import bson.json_util
    pymongo.objectid = bson.objectid
    pymongo.json_util = bson.json_util
    sys.modules['pymongo.objectid'] = bson.objectid
    sys.modules['pymongo.json_util'] = bson.json_util
from pymongo import Connection
from pymongo.errors import AutoReconnect
def get_conn(host_url, replica_set_name):
    try:
        mongoConn = pymongo.MongoReplicaSetClient(host=host_url, replicaSet=replica_set_name, read_preference=pymongo.ReadPreference.PRIMARY_PREFERRED)
    except AutoReconnect,e:
        print "init mongo connection failed.... "
        mongoConn = None
    return mongoConn

class Table(object):
    """
    class to operate cold_query  
    """
    _conn = mongoConn
    def __init__(self, db, coll, uniq_key = 'id', host_url = None, replica_set_name=None):
        if host_url:
            self._conn = get_conn(host_url, replica_set_name)
        self._db = db
        self._coll = coll
        self._coll_new = coll + '_new'
        self.uniq_key = uniq_key
        self.coll = self._conn[self._db][self._coll]
        self.coll_new = self._conn[self._db][self._coll_new]

    def scan(cls, batch_size=30, is_new=False, condition={}):
        try:
            if is_new:
                cursor = cls.coll_new.find(condition).batch_size(batch_size)
            else:
                cursor = cls.coll.find(condition).batch_size(batch_size)
        except:
            exstr = traceback.format_exc()
            logger.error('scan error : ' + exstr)
            return None
        return cursor

    def query(cls, id):
        try:
            cursor = cls.coll.find_one({cls.uniq_key: id})
        except:
            exstr = traceback.format_exc()
            logger.error('query error : ' + exstr)
            return None
        return cursor

    def save(cls, item, is_new=False):
        try:
            if not is_new:
                cls.coll.update({cls.uniq_key:item[cls.uniq_key]}, item, True)
            else:
                cls.coll_new.update({cls.uniq_key:item[cls.uniq_key]}, item, True)
        except:
            exstr = traceback.format_exc()
            logger.error('save error : ' + exstr)

    def remove(cls, item):
        try:
            cursor = cls.coll.remove({cls.uniq_key:item[cls.uniq_key]})
        except:
            exstr = traceback.format_exc()
            logger.error('remove error : ' + exstr)

    def dump(cls):
        try:
            cursor = cls.coll.find()
            for item in cursor:
                info = 'id ' + item['id'] + ' go_link ' + item['go_link'] + ' title ' + item['title'].strip()
                print info.encode('utf8')
        except:
            exstr = traceback.format_exc()
            logger.error('dump error : ' + exstr)
            return None
        return cursor

if __name__ == '__main__':
    t = Table('scrapy', 'test')
    t.dump()
