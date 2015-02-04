#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import hashlib
import Image
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

def get_html_by_data(url, use_cookie=False):
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
    f = opener.open(req)
    html = f.read()
    html_file = open('test.html','w')
    print >> html_file, html
    f.close()
    return html

def crawl_prods(url, kd_name):
    print kd_name + ' ' + url
    html = get_html_by_data(url, use_cookie=False)
    hxs = Selector(text=html)
    item_list = hxs.xpath('//div[@class="express-message-wrap clearfix"]/div')
    for item in item_list:
        try:
            prod = {}
            prod['kd'] = kd_name
            prod['name'] = item.xpath('.//dl/dt[1]/a/text()')[0].extract()
            prod['region'] = item.xpath('.//dl/dd[2]/strong/text()')[0].extract().strip().replace('\t','').replace(' ','')
            prod['province'] = prod['region'].split('-')[0]
            prod['addr'] = item.xpath('.//dl/dd[3]/strong/text()')[0].extract().strip()
            prod['phone'] = item.xpath('.//dl/dd[4]/strong/text()')[0].extract().strip()
            print prod['name']
            print prod['region']
            print prod['province']
            print prod['addr']
            print prod['phone']
            table.save(prod) 
        except Exception as e:
            print e
    try:
        next_url = 'http://www.kuaidihelp.com/' + hxs.xpath('//li[@class="next-page"]/a/@href')[0].extract()
        if next_url != url:
            crawl_prods(next_url, kd_name)
    except:
        return

if __name__ == '__main__':
    part = int(sys.argv[1])
    with open('kd.conf','r') as kd_file:
        kd_list = kd_file.readlines()
    for i in range(part * 1000, (part+1) * 1000):
        print 'process: ' + str(i)
        for kd_name in kd_list:
            start_url = 'http://www.kuaidihelp.com/wangdian-' + str(i) + '-' + kd_name.strip() + '-xq-cy--/'
            crawl_prods(start_url, kd_name.strip())
    print 'Crawl Finished!'
