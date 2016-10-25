#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import hashlib
import time
from pymongo import MongoClient
from scrapy import Selector
from random import randint
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    client = MongoClient("127.0.0.1",27017)
    shop_table = client["dianping"]["hotel"]
except Exception as e:
    print e
    exit(-1)

def get_html_by_data(url, use_cookie=False, fake_ip=False):
    data = {}
    post_data = urllib.urlencode(data)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    req = urllib2.Request(url)
    if use_cookie:
        cookie_file = open('cookie')
        cookie = cookie_file.read().strip()
        req.add_header("Cookie", cookie)
    req.add_header("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36")
    req.add_header("Referer", "http://www.dianping.com/search/category/5/80/r1682")
    req.add_header("Host", "www.dianping.com")
    req.add_header("Upgrade-Insecure-Requests", "1")
    while 1:
        if fake_ip:
            ip_addr = '%s.%s.%s.%s'%(str(randint(1,255)), str(randint(1,255)), str(randint(1,255)), str(randint(1,255)))
            req.add_header("X-Forwarded-For", ip_addr)
        f = opener.open(req)
        if f.code != 200:
            print 'Error request, code:' + str(f.code)
            time.sleep(1)
            continue
        html = f.read()
        html_file = open('test.html','w')
        print >> html_file, html
        f.close()
        return html

def get_html_by_data2(url, use_cookie=False, fake_ip=False):
    data = {}
    post_data = urllib.urlencode(data)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    req = urllib2.Request(url)
    if use_cookie:
        cookie_file = open('cookie2')
        cookie = cookie_file.read().strip()
        req.add_header("Cookie", cookie)
    req.add_header("User-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36")
    if fake_ip:
        ip_addr = '%s.%s.%s.%s'%(str(randint(1,255)), str(randint(1,255)), str(randint(1,255)), str(randint(1,255)))
        req.add_header("X-Forwarded-For", ip_addr)
    req.add_header("Host", "m.dianping.com")
    req.add_header("Upgrade-Insecure-Requests", 1)
    while 1:
        if fake_ip:
            ip_addr = '%s.%s.%s.%s'%(str(randint(1,255)), str(randint(1,255)), str(randint(1,255)), str(randint(1,255)))
            req.add_header("X-Forwarded-For", ip_addr)
        f = opener.open(req)
        if f.code != 200:
            print 'Error request, code:' + str(f.code)
            time.sleep(1)
            continue
        html = f.read()
        html_file = open('test2.html','w')
        print >> html_file, html
        f.close()
        return html

def write_db(prod):
    prod['id'] = hashlib.md5(prod['shop_name']+prod['addr']+prod['tel']).hexdigest().upper()
    shop_table.save(prod)
    print 'write successfully.'

def crawl_details(prod):
    try:
        detail_url = prod['url'].replace('shop', 'shopping/shopexpandinfo')
        hxs = Selector(text=get_html_by_data2(detail_url, use_cookie=True, fake_ip=True))
        prod['tel'] = ''
        tel_list = hxs.xpath('//span[@class="title-item tel"]/text()')
        for tel in tel_list:
            prod['tel'] += tel.extract().strip()
    except:
        prod['tel'] = ''

def crawl_prod(prod):
    prod['url'] = 'http://m.dianping.com/shop/2297227'
    hxs = Selector(text=get_html_by_data2(prod['url'], use_cookie=True, fake_ip=True))
    prod['shop_name'] = hxs.xpath('//span[@class="shop-name"]/text()|//figcaption[@class="shopname"]/text()')[0].extract().strip()
    print 'shop_name: ' + prod['shop_name']
    prod['addr'] = ''
    addr_list = hxs.xpath('//div[@class="info-list link-list"]/a/text()|//article[@class="add bottom-border"]/text()')
    for addr in addr_list:
        prod['addr'] += addr.extract().strip()
    print 'addr: ' + prod['addr']
    
    prod['tel'] = ''
    #import pdb;pdb.set_trace()
    try:
        tel_list = hxs.xpath('//div[@class="info-list link-list"]/div/a/text()|//div[@class="aboutPhoneNum"]/a/text()')
        for tel in tel_list:
            prod['tel'] += tel.extract().strip() + ' '
    except:
        pass

    prod['dp_cnt'] = '0'
    try:
        txt = hxs.xpath('//div[@class="modebox shop-comment"]/a/span/text()')[0].extract().strip()
        prod['dp_cnt'] = txt.split('(')[1].split(')')[0]
    except:
        pass
    print 'dp_cnt:' + prod['dp_cnt']
    
    if prod['addr'].find('电话、交通、营业时间等信息') != -1:
        crawl_details(prod)
    print 'tel: ' + prod['tel']
    write_db(prod) 

def work(city, url, page):
    print city + ' ' + url + 'p' + str(page)
    hxs = Selector(text=get_html_by_data(url+'p'+str(page), use_cookie=True, fake_ip=True))
    li_list = hxs.xpath('//ul[@class="hotelshop-list"]/li')
    if len(li_list) == 0:
        return False
    for li in li_list:
        content_url = 'http://www.dianping.com' + li.xpath('.//h2[@class="hotel-name"]/a/@href')[0].extract()
        print content_url
        prod = {}
        prod['city'] = city
        prod['url'] = 'http://m.dianping.com/shop/' + content_url.split('/')[4]
        crawl_prod(prod)
    return True

if __name__ == "__main__":
    with open("city_list_utf8.csv",'r') as region_file:
        for line in region_file.readlines():
            res = line.split(';')
            city = res[0].strip()
            url = res[1].strip().split('#')[0]
            for page in xrange(1, 51):
                try:
                    if not work(city, url, page):
                        break
                except Exception as e:
                    print e
                    continue
