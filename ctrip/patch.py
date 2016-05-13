#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import requests
import random
from scrapy import Selector
import pymongo
from random import randint
import random
import traceback
reload(sys)
sys.setdefaultencoding('utf-8')

curr_ip_pos = 0
ip_list = []

def read_ip():
    global ip_list
    with open('ip.conf') as cnf_file:
        text = cnf_file.read()
        ip_list = text.strip().split('\n')

def get_html_by_data(url, use_cookie=False, fake_ip=False):
    global ip_list
    while True:
        try:
            print 'available ip count:' + str(len(ip_list))
            cur_ip = random.choice(ip_list)
            proxy = {'http':'http://'+cur_ip}
            response = requests.get(url, proxies=proxy, timeout=3)
            if response.status_code != requests.codes.ok:
                print 'Get Error! Try Again! ip: ' + cur_ip
                continue
            html = response.text
            html_file = open('test.html','w')
            print >> html_file, html
            return html
        except Exception as e:
            #print e
            print 'Get Error! Try Again! ip: ' + cur_ip
            #traceback.print_exc()

def add(key, prod):
    if key in prod:
        return prod[key].replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def write_line(prod):
    resline = ""
    resline += add('title', prod) 
    resline += add('name', prod) 
    resline += add('addr', prod) 
    resline += add('star', prod) 
    resline += add('open_year', prod) 
    resline += add('room_cnt', prod) 
    resline += add('tel', prod) 
    resline += add('url', prod)
    return resline

def crawl_prod(url, prod):
    hxs = Selector(text=get_html_by_data(url, fake_ip=True))
    prod['url'] = url
    try:
        prod['star'] = hxs.xpath('//div[@class="grade"]/span/@title')[0].extract()
        print 'star: ' + prod['star']
    except Exception as e:
        print 'no star'
    try:
        info_text = hxs.xpath('//div[@class="htl_room_txt text_3l "]/p/text()')[0].extract().strip()
        if info_text.find('开业') != -1:
            prod['open_year'] = info_text.split('开业')[0]
            print 'open_year: ' + prod['open_year']
        if info_text.find('间房') != -1:
            prod['room_cnt'] = info_text.split('房')[0].split(u'\xa0')[-1]
            print 'room_cnt: ' + prod['room_cnt']
    except Exception as e:
        print 'no details'
    try:
        prod['tel'] = hxs.xpath('//div[@class="htl_room_txt text_3l "]/p/span[@id="J_realContact"]/@data-real')[0].extract().strip().split(u'\xa0')[0].strip()
        print 'tel: ' + prod['tel']
    except Exception as e:
        print 'no tel'

def handle_prod(prod):
    print 'name: ' + prod['name']
    crawl_prod(prod['url'], prod)
    return write_line(prod)

if __name__ == '__main__':
    read_ip()
    patch_cnt = 0
    part = int(sys.argv[1])
    with open('empty.csv', 'r') as res_file, open('res_new.csv', 'a') as out_file:
        for line in res_file.readlines():
            patch_cnt += 1
            if patch_cnt % 40 != part:
                continue
            prod = {}
            res = line.split(',')
            prod['title'] = res[0]
            prod['name'] = res[1]
            prod['addr'] = res[2]
            prod['url'] = res[7]
            line = handle_prod(prod)    
            print >> out_file, line.strip().encode('utf-8')
    print 'patch_cnt:' + str(patch_cnt)
