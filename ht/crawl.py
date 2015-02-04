#coding:utf-8
import urllib
import cookielib
import urllib2
import json
import sys
import random
import requests
import time
reload(sys)
sys.setdefaultencoding('utf-8')

USER_AGENTS = [
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.2) ',
    'Gecko/2008092313 Ubuntu/8.04 (hardy) Firefox/3.1',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) ',
    'Gecko/20070118 Firefox/2.0.0.2pre',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.7pre) Gecko/20070815 ',
    'Firefox/2.0.0.6 Navigator/9.0b3',
    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_4_11; en) AppleWebKit/528.5+',
    ' (KHTML, like Gecko) Version/4.0 Safari/528.1',
    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; sv-se) AppleWebKit/419 ',
    '(KHTML, like Gecko) Safari/419.3',
    'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0;)',
    'Mozilla/4.08 (compatible; MSIE 6.0; Windows NT 5.1)',
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
]

def get_kd_dict(province):
    request_url = 'http://www.htky365.com/htwebapi/site/query'
    headers = {
        'Connection':"keep-alive",
        'Host':"www.htky365.com",
        'Referer':"http://www.htky365.com/Site/Query?city=%E6%9D%AD%E5%B7%9E%E5%B8%82",
        'User-agent':USER_AGENTS[random.randint(0,len(USER_AGENTS)-1)],
        }
    with open('cookie') as cookie_file:
        headers['Cookie'] = cookie_file.read().strip()
    payload = {
        "appId":"HTWeb",
        "city":"",
        "country":"",
        "province":province,
        "query":"",
    }
    r = requests.post(request_url, data=payload, headers=headers, timeout=5)
    json_source = r.text
    res_dict = json.loads(json_source)
    return res_dict

def crawl_pro(province):
    res_dict = get_kd_dict(province)
    if not 'data' in res_dict:
        print 'Cannot crawl province: ' + province
        return
    for res in res_dict['data']:
        try:
            prod = {}
            prod['kd'] = "huitong"
            prod['province'] = res['province']
            prod['city'] = res['city']
            prod['zone'] = res['county']
            prod['name'] = res['name']
            prod['deliver'] = res['range']
            prod['linkman'] = res['owner']
            prod['phone1'] = res['phone']
            save_csv(prod)
            print prod['name']
        except Exception as e:
            print e

def add(key, prod):
    if key in prod and prod[key] != None:
        return prod[key].replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def save_csv(prod):
    file = open('result.csv','a')
    resline = ""
    resline += add('kd', prod)
    resline += add('name', prod)
    resline += add('province', prod)
    resline += add('city', prod)
    resline += add('zone', prod)
    resline += add('addr', prod)
    resline += add('linkman', prod)
    resline += add('phone1', prod)
    resline += add('phone2', prod)
    resline += add('deliver', prod)
    resline += add('mobile', prod)
    resline += add('ts_tel', prod)
    print >> file, resline.encode('utf-8')

def work():
    with open("province_list","r") as pro_file:
        pro_list = pro_file.readlines()
    for pro in pro_list:
        crawl_pro(pro.strip())

if __name__ == "__main__":
    work()
