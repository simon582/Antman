#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import requests
import random
from scrapy import Selector
import pymongo
import traceback
reload(sys)
sys.setdefaultencoding('utf-8')

curr_ip_pos = 0
ip_list = []
def reset():
    global curr_ip_pos
    global ip_list
    response = requests.get('http://121.41.122.106:8080/ip/')
    ip_list = response.text.split(' ')
    for i in range(len(ip_list)):
        ip_list[i] = ip_list[i].strip()
    curr_ip_pos = 0

def get_html_by_data(url, use_cookie=False):
    global curr_ip_pos
    while True:
        try:
            proxy = {'http':ip_list[curr_ip_pos]}
            response = requests.get(url, proxies=proxy, timeout=3)
            if response.status_code != requests.codes.ok:
                curr_ip_pos += 1
                print 'Get Error! Try Again! curr_ip_pos: ' + str(curr_ip_pos) 
                if curr_ip_pos >= len(ip_list) - 1:
                    reset()
                continue
            html = response.text
            html_file = open('test.html','w')
            print >> html_file, html
            return html
        except:
            curr_ip_pos += 1
            print 'Get Error! Try Again! curr_ip_pos: ' + str(curr_ip_pos) 
            if curr_ip_pos >= len(ip_list) - 1:
                reset()

def add(key, prod):
    if key in prod:
        return prod[key].replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def write_csv(prod):
    file = open('result.csv','a')
    resline = ""
    resline += add('title',prod)
    resline += add('name',prod)
    resline += add('addr',prod)
    resline += add('star',prod)
    resline += add('open_year',prod)
    resline += add('room_cnt',prod)
    resline += add('tel',prod)
    print >> file, resline.encode('utf-8')

def crawl_prod(url, prod):
    hxs = Selector(text=get_html_by_data(url))
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
    hxs = Selector(text=get_html_by_data(list_url))
    item_list = hxs.xpath('//div[@id="hotel_list"]/div[@class="searchresult_list"]')
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
            hxs = Selector(text=get_html_by_data(start_url))
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
    reset()
    start_page = int(sys.argv[1])
    first = True
    for id in range(24, 2001):
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
