#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import hashlib
import Image
import os
import re
import pymongo
from scrapy import Selector
reload(sys)
sys.setdefaultencoding('utf-8')

# initialize mongodb connection
try:
    con = pymongo.Connection('127.0.0.1', 27017)
    kd_db = con.kd
    table = kd_db.info
except Exception as e:
    print 'Cannot connect mongodb!'
    print e
    exit(-1)

cursor = table.find()

kd_dict = {"sto":"shentong", "yt":"yuantong", "yd":"yunda", "ht":"huitong", "tt":"tiantian", "gt":"guotong", "yt":"yuantong"}

for key, value in kd_dict.items():
    path = 'result/' + value
    if not os.path.isdir(path):
        os.makedirs(path)

for item in cursor:
    filepath = kd_dict[item['kd']]
    filename = item['province'] + '.csv'
    file = open('result/' + filepath + '/' + filename, 'a')
    outline = ""
    outline += kd_dict[item['kd']] + ','
    outline += item['province'] + ','
    res = item['region'].split('-')
    if len(res) == 3:
        outline += res[1] + ',' + res[2] + ','
    if len(res) == 2:
        outline += res[0] + ',' + res[1] + ','
    if len(res) == 1:
        outline += res[0] + ',' + res[0] + ','
    outline += item['addr'].replace(',','') + ','
    m = re.search(r"\d{3,4}-\d{7,8}", item['phone'])
    if m:
        outline += m.group(0) + ','
    else:
        m = re.search(r"\d{11}", item['phone'])
        if m:
            outline += m.group(0) + ','
        else:
            outline += item['phone']
    try:
        print >> file, outline.encode('gbk')
    except:
        continue
