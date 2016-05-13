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
    #if len(ip_list) == 0:
    #    print 'no available proxy ip'
    #    exit(0)
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
            print e
            print 'Get Error! Try Again! ip: ' + cur_ip
            #ip_list.remove(cur_ip)
            traceback.print_exc()

def get_html_by_data_2(url, use_cookie=False, fake_ip=False):
    headers = {
        'Host': 'hotels.ctrip.com',
        'Referer': 'http://hotels.ctrip.com/hotel/beijing1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
    }
    if fake_ip:
        ip = "%s.%s.%s.%s" % (str(randint(0,255)), str(randint(0,255)), str(randint(0,255)), str(randint(0,255)))
        headers["X-Forwarded-For"] = ip
    r = requests.get(url, headers=headers)
    html = r.text
    with open('test.html','w') as test_file:
        print >> test_file, html
    return html

def add(key, prod):
    if key in prod:
        return prod[key].replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def write_csv(prod):
    with open('result.csv', 'a') as csv_file:
        resline = ""
        resline += add('title', prod) 
        resline += add('name', prod) 
        resline += add('addr', prod) 
        resline += add('star', prod) 
        resline += add('open_year', prod) 
        resline += add('room_cnt', prod) 
        resline += add('tel', prod) 
        resline += add('url', prod)
        print >> csv_file, resline.encode('utf-8')

def crawl_prod(url, prod):
    hxs = Selector(text=get_html_by_data(url, fake_ip=True))
    prod['url'] = url
    try:
        prod['star'] = hxs.xpath('//div[@class="grade"]/span/@title')[0].extract()
        print 'star: ' + prod['star']
        info_text = hxs.xpath('//div[@class="htl_room_txt text_3l "]/p/text()')[0].extract().strip()
        if info_text.find('开业') != -1:
            prod['open_year'] = info_text.split('开业')[0]
            print 'open_year: ' + prod['open_year']
        if info_text.find('间房') != -1:
            prod['room_cnt'] = info_text.split('房')[0].split(u'\xa0')[-1]
            print 'room_cnt: ' + prod['room_cnt']
        prod['tel'] = hxs.xpath('//div[@class="htl_room_txt text_3l "]/p/span[@id="J_realContact"]/@data-real')[0].extract().strip().split(u'\xa0')[0].strip()
        print 'tel: ' + prod['tel']
    except Exception as e:
        print e

def crawl_list(title, list_url):
    print 'crawl list:' + list_url
    hxs = Selector(text=get_html_by_data(list_url, fake_ip=True))
    item_list = hxs.xpath('//div[@id="hotel_list"]/div[@class="searchresult_list "]')
    for item in item_list:
        try:
            url = item.xpath('.//h2[@class="searchresult_name"]/a/@href')[0].extract()
            print 'content_url: ' + url
            prod = {}
            prod['title'] = title
            prod['name'] = item.xpath('.//h2[@class="searchresult_name"]/a/@title')[0].extract()
            print 'name: ' + prod['name']
            addr_list = item.xpath('.//p[@class="searchresult_htladdress"]/text()|.//p[@class="searchresult_htladdress"]/a/text()')
            prod['addr'] = ""
            for addr in addr_list:
                prod['addr'] += addr.extract().strip()
            print 'addr: ' + prod['addr']
            crawl_prod('http://hotels.ctrip.com' + url, prod)
            write_csv(prod)
        except Exception as e:
            print e
            print 'skip item'

def work(start_url, start_page):
    retry_times = 0
    while retry_times < 3:
        try:
            hxs = Selector(text=get_html_by_data(start_url, fake_ip=True))
            max_page = hxs.xpath('//div[@class="c_page_list layoutfix"]/a[@rel="nofollow"]/text()')[0].extract().strip()
            title = hxs.xpath('//h1/text()')[0].extract().strip()
            break
        except:
            retry_times += 1
    if retry_times == 3:
        print 'Retry 3 times! No max_page or title info.'
        return False
    print title + ' ' + max_page + ' pages'
    for page in range(start_page, int(max_page) + 1):
        try:
            crawl_list(title, start_url + '/p' + str(page))
        except Exception as e:
            print e
            print traceback.format_exc()
            print 'skip page ' + start_url + '/p' + str(page)
    return True

if __name__ == '__main__':
    read_ip()
    start_city = int(sys.argv[1])
    start_page = int(sys.argv[2])
    first = True
    for id in range(start_city, 2001):
        try:
            print 'current id: ' + str(id)
            if first:
                res = work("http://hotels.ctrip.com/hotel/qingdao" + str(id), start_page)
                first = False
            else:
                res = work("http://hotels.ctrip.com/hotel/qingdao" + str(id), 1)
            if not res:
                print 'skip city id ' + str(id)
        except Exception as e:
            print e
            print 'skip city id ' + str(id)
