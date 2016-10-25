#-*- coding:utf-8 -*-
import sys
from pymongo import MongoClient
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    client = MongoClient("127.0.0.1",27017)
    shop_table = client["dianping"]["hotel"]
except Exception as e:
    print e
    exit(-1)

def add(key, prod):
    if prod.has_key(key):
        return prod[key].replace('\r','').replace('\n','').replace(',',' ') + ','
    return ','

def save_csv(prod):
    file = open('result.csv','a')
    resline = ""
    resline += add('city', prod)
    #resline += add('district', prod)
    #resline += add('region', prod)
    resline += add('shop_name', prod)
    resline += add('dp_cnt', prod)
    resline += add('addr', prod)
    resline += add('tel', prod)
    resline += add('url', prod)
    print >> file, resline.encode('utf-8')

def work():
    cursor = shop_table.find()
    for prod in cursor:
        save_csv(prod)

work()
