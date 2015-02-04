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
    html = unicode(f.read(),'gbk')
    html_file = open('test.html','w')
    print >> html_file, html
    f.close()
    return html

def add(key, prod):
    if key in prod:
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
    resline += add('sub_tel', prod)
    print >> file, resline.encode('utf-8')

def crawl_details(prod):
    html = get_html_by_data(prod['url'], use_cookie=False)
    hxs = Selector(text=html)
    prod['name'] = hxs.xpath('//div[@class="cordiva"]/font/text()')[0].extract()
    tr_list = hxs.xpath('//table[@id="cordivdetail"]/tr')
    for tr in tr_list:
        try:
            key = tr.xpath('./td[@class="td_l"]/text()')[0].extract()
            value = tr.xpath('./td[@class="td_r"]/text()')[0].extract()
            ikey = "null"
            if key == "所在地区":
                ikey = "region"
            if key == "查询电话":
                ikey = "phone1"
            if key == "业务电话":
                ikey = "phone2"
            if key == "公司地址":
                ikey = "addr"
            if key == "派送范围":
                ikey = "deliver"
            if key == "分部联络方式":
                ikey = "sub_tel"
                vlist = tr.xpath('./td[@class="td_r"]/text()')
                value = ""
                for v in vlist:
                    value += v.extract()
            if ikey != "null":
                prod[ikey] = value.replace(u'\xa0','')
        except:
            continue
    if "region" in prod:
        res = prod['region'].split(' ')
        if len(res) >= 2:
            prod['province'] = prod['city'] = res[0]
            if res[0].find('省') != -1 or res[1].find('市') != -1:
                prod['city'] = res[1]
            if res[1].find('区') != -1 or res[1].find('县') != -1:
                prod['zone'] = res[1]
    if (not "zone" in prod) and ('addr' in prod):
        if prod['addr'].find('县') != -1:
            prod['zone'] = prod['addr'].split('县')[0] + '县'
            if prod['zone'].find('市') != -1:
                prod['zone'] = prod['zone'].split('市')[1]
        elif prod['addr'].find('区') != -1:
            prod['zone'] = prod['addr'].split('区')[0] + '区'
            if prod['zone'].find('市') != -1:
                prod['zone'] = prod['zone'].split('市')[1]
    
    for key,value in prod.items():
        print key + ": " + value 
    #import pdb;pdb.set_trace()

def crawl_prods(url):
    print url
    html = get_html_by_data(url, use_cookie=False)
    hxs = Selector(text=html)
    item_list = hxs.xpath('//b[@class="corinfo"]/a')
    for item in item_list:
        try:
            prod = {}
            prod['kd'] = 'tiantian'
            #prod['name'] = item.xpath('./text()')[0].extract()
            prod['url'] = 'http://www.ttkdex.com/webdistributed/' + item.xpath('./@href')[0].extract()
            crawl_details(prod)
            save_csv(prod) 
        except Exception as e:
            print e

if __name__ == '__main__':
    part = int(sys.argv[1])
    for i in range(part * 5 + 1, (part+1) * 5 + 1):
        print 'process: ' + str(i)
        start_url = 'http://www.ttkdex.com/webdistributed/' + str(i) + '.html'
        crawl_prods(start_url)
    print 'Crawl Finished!'
