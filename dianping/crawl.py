#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import hashlib
from pymongo import MongoClient
from scrapy import Selector
from random import randint
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    client = MongoClient("127.0.0.1",27017)
    shop_table = client["dianping"]["shop"]
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
        cookie = cookie_file.read()
        req.add_header("Cookie", cookie)
    req.add_header("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36")
    if fake_ip:
        ip_addr = '%s.%s.%s.%s'%(str(randint(1,255)), str(randint(1,255)), str(randint(1,255)), str(randint(1,255)))
        req.add_header("X-Forwarded-For", ip_addr)
    req.add_header("Referer", "http://www.dianping.com/search/category/5/80/r1682")
    req.add_header("Host", "www.dianping.com")
    f = opener.open(req)
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
        cookie = cookie_file.read()
        req.add_header("Cookie", cookie)
    req.add_header("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36")
    if fake_ip:
        ip_addr = '%s.%s.%s.%s'%(str(randint(1,255)), str(randint(1,255)), str(randint(1,255)), str(randint(1,255)))
        req.add_header("X-Forwarded-For", ip_addr)
    req.add_header("Host", "m.dianping.com")
    f = opener.open(req)
    html = f.read()
    html_file = open('test2.html','w')
    print >> html_file, html
    f.close()
    return html

def write_db(prod):
    prod['id'] = hashlib.md5(prod['shop_name']+prod['addr']+prod['tel']).hexdigest().upper()
    shop_table.save(prod)
    print 'write successfully.'

def crawl_prod(prod):
    hxs = Selector(text=get_html_by_data2(prod['url'], use_cookie=True, fake_ip=True))
    prod['shop_name'] = hxs.xpath('//span[@class="shop-name"]/text()|//figcaption[@class="shopname"]/text()')[0].extract().strip()
    print 'shop_name: ' + prod['shop_name']
    prod['addr'] = ''
    addr_list = hxs.xpath('//div[@class="info-list link-list"]/a/text()|//article[@class="add bottom-border"]/text()')
    for addr in addr_list:
        prod['addr'] += addr.extract().strip()
    print 'addr: ' + prod['addr']
    try:
        prod['tel'] = ''
        tel_list = hxs.xpath('//div[@class="info-list link-list"]/div/a/text()|//article[@class="tel bottom-border"]/a/text()')
        for tel in tel_list:
            prod['tel'] += tel.extract().strip()
    except:
        prod['tel'] = ''
    print 'tel: ' + prod['tel']
    '''
    prod['shop_name'] = hxs.xpath('//h1[@class="shop-name"]/text()')[0].extract().strip()
    print 'shop_name: ' + prod['shop_name']
    prod['addr'] = hxs.xpath('//span[@itemprop="street-address"]/text()')[0].extract().strip()
    print 'addr: ' + prod['addr'] 
    prod['tel'] = ""
    tel_list = hxs.xpath('//span[@itemprop="tel"]/text()')
    for tel in tel_list:
        prod['tel'] += tel.extract() + ' '
    print 'tel: ' + prod['tel']
    '''
    write_db(prod) 

def work(cat, district, region, url, page):
    print district + ' ' + region + ' ' + url + 'p' + str(page)
    hxs = Selector(text=get_html_by_data(url+'p'+str(page), use_cookie=True, fake_ip=True))
    li_list = hxs.xpath('//div[@id="shop-all-list"]/ul/li|//ul[@class="shop-list"]/li')
    for li in li_list:
        content_url = 'http://www.dianping.com' + li.xpath('.//a[1]/@href')[0].extract()
        print content_url
        prod = {}
        prod['cat'] = cat
        prod['district'] = district
        prod['region'] = region
        prod['url'] = 'http://m.dianping.com/shop/' + content_url.split('/')[4]
        crawl_prod(prod)

if __name__ == "__main__":
    cat = sys.argv[1]
    with open(cat + ".conf",'r') as region_file:
        for line in region_file.readlines():
            res = line.split(';')
            district = res[0].strip()
            region = res[1].strip()
            url = res[2].strip().split('#')[0]
            for page in xrange(1, 50):
                try:
                    work(cat, district, region, url, page)
                except Exception as e:
                    print e
                    continue
