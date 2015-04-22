#-*- coding:utf-8 -*-
import sys
from pymongo import MongoClient
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    client = MongoClient("127.0.0.1",27017)
    shop_table = client["dianping"]["shop"]
except Exception as e:
    print e
    exit(-1)

def add(key, prod):
    if prod.has_key(key):
        return prod[key].replace('\r','').replace('\n','').replace(',',' ') + ','
    return ','

def save_csv(cat, prod):
    file = open(cat+'.csv','a')
    resline = ""
    resline += add('district', prod)
    resline += add('region', prod)
    resline += add('shop_name', prod)
    resline += add('addr', prod)
    resline += add('tel', prod)
    resline += add('url', prod)
    print >> file, resline.encode('utf-8')

def work(cat):
    cursor = shop_table.find({"cat":cat})
    for prod in cursor:
        save_csv(cat, prod)

#work("ms")
#work("xxyl")
#work("lr")
#work("jh")
#work("qz")
work("shfw")
