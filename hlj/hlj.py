#-*- coding:utf-8 -*-
import sys
import hashlib
import requests
import urllib2
import random
from scrapy import Selector
import json
from random import randint
import traceback
reload(sys)
sys.setdefaultencoding('utf-8')

type_dict = {
    "2":"婚礼策划",
    "6":"婚纱摄影",
    "7":"摄影师",
    "8":"摄像师",
    "9":"化妆师",
    "11":"主持人",
}
def get_html_by_data(url, use_cookie=False, fake_ip=False):
    headers = {
        'Host': 'www.hunliji.com',
        'Referer': 'http://www.hunliji.com/exhibit?cid=78&page=1&property=9&sort=default',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
    }
    if fake_ip:
        ip = "%s.%s.%s.%s" % (str(randint(0,255)), str(randint(0,255)), str(randint(0,255)), str(randint(0,255)))
        #headers["X-Forwarded-For"] = ip
    r = requests.get(url, headers=headers)
    html = r.text
    with open('test.html','w') as test_file:
        print >> test_file, html
    return html

def crawl_prod(prod):
    hxs = Selector(text=get_html_by_data(prod['detail_url'],use_cookie=True,fake_ip=True))
    try:
        tc_text = hxs.xpath('//div[@class="tabs-left"]/a[1]/text()')[0].extract()
        print 'tc_text: ' + tc_text
        prod['tc_cnt'] = tc_text.split(' ')[1]
        al_text = hxs.xpath('//div[@class="tabs-left"]/a[2]/text()')[0].extract() 
        print 'al_text: ' + al_text
        prod['al_cnt'] = al_text.split(' ')[1]
        contact_text_list = hxs.xpath('//div[@class="shop-contact"]/p/text()')
        prod['contact'] = ""
        for text in contact_text_list:
            prod['contact'] += text.extract().strip().replace(',','|')
        print 'contact: ' + prod['contact']
    except Exception as e:
        print e

def work(city_id, type_id, type_name, page):
    print 'city_id: ' + city_id
    print 'type_id: ' + type_id
    print 'type_name: ' + type_name
    print 'page: ' + page
    url = "http://www.hunliji.com/exhibit?cid="+city_id+"&page="+page+"&property="+type_id+"&sort=default"
    print 'list_url: ' + url
    hxs = Selector(text=get_html_by_data(url, use_cookie=True, fake_ip=True))
    item_list = hxs.xpath('//ul[@class="merc-list"]/li[@class="merc-row"]')
    if len(item_list) == 0:
        return False
    city_name = hxs.xpath('//span[@class="city"]/text()')[0].extract()

    for item in item_list:
        try:
            prod = {}
            prod['city'] = city_name
            print 'city: ' + city_name
            prod['type'] = type_name
            print 'type: ' + type_name
            detail_url = 'http://www.hunliji.com' + item.xpath('.//h3/a/@href')[0].extract()
            print 'detail_url: ' + detail_url
            prod['detail_url'] = detail_url
            title = item.xpath('.//h3/a/text()')[0].extract()
            print 'title: ' + title
            prod['title'] = title
            crawl_prod(prod)
            save(prod)
            #import pdb;pdb.set_trace()
        except Exception as e:
            print e
            print 'skip item'
    return True

def add(key, prod):
    if key in prod:
        return prod[key].replace('&nbsp','').replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def save(prod):
    file = open('data/'+prod['city']+'.csv','a')
    resline = ""
    resline += add('type',prod)
    resline += add('title',prod)
    resline += add('detail_url',prod)
    resline += add('tc_cnt',prod)
    resline += add('al_cnt',prod)
    resline += add('contact',prod)
    print >> file, resline.encode('utf-8')

if __name__ == '__main__':
    city_id = sys.argv[1]
    for type_id, type_name in type_dict.items():
        page = 1
        while work(city_id, type_id, type_name, str(page)):
            page += 1
    print 'Crawl finished!'
