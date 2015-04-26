#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import json
import hashlib
import re
from scrapy import Selector
reload(sys)
sys.setdefaultencoding('utf-8')

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
    f = opener.open(req, timeout=5)
    html = f.read()
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
    resline += add('user', prod)
    resline += add('name', prod)
    resline += add('age', prod)
    resline += add('gender', prod)
    resline += add('region', prod)
    resline += add('position', prod)
    resline += add('capital', prod)
    resline += add('in_credit', prod)
    resline += add('out_credit', prod)
    resline += add('cur_amt', prod)
    resline += add('cur_rate', prod)
    resline += add('periods', prod)
    resline += add('interest', prod)
    print >> file, resline.encode('utf-8')

def crawl_black(prod):
    url = 'http://www.ppdai.com/blacklistdetail/' + prod['user']
    hxs = Selector(text=get_html_by_data(url))
    textline = hxs.xpath('//div[@class="info_tit"]/span/text()')[0].extract()
    res = textline.split('_')
    prod['name'] = res[0]
    print 'name: ' + prod['name']
    prod['region'] = res[1]
    print 'region: ' + prod['region']
    prod['gender'] = res[2]
    print 'gender: ' + prod['gender']
    prod['periods'] = hxs.xpath('//div[@class="table_nav"]/table/tr[2]/td[2]/text()')[0].extract()
    print 'periods: ' + prod['periods']
    prod['interest'] = hxs.xpath('//div[@class="table_nav"]/table/tr[2]/td[5]/text()')[0].extract().replace(',','')
    print 'interest: ' + prod['interest']

def crawl_detail(prod):
    url = 'http://www.ppdai.com/user/' + prod['user']
    hxs = Selector(text=get_html_by_data(url))
    prod['in_credit'] = hxs.xpath('//span[@class="cf7971a"]/text()')[0].extract()
    print 'in_credit: ' + prod['in_credit']
    prod['out_credit'] = hxs.xpath('//span[@class="cf7971a"]/text()')[1].extract()
    print 'out_credit: ' + prod['out_credit']
    prod['age'] = hxs.xpath('//li[@class="user_li"]/p/span[2]/text()')[0].extract().strip()
    print 'age: ' + prod['age']
    prod['position'] = hxs.xpath('//li[@class="user_li"]/p[2]/text()')[0].extract().split('：')[1].strip()
    print 'position: ' + prod['position']
    prod['cur_amt'] = hxs.xpath('//div[@class="borrow_list"]/table/tbody/tr/td[1]/span/text()')[0].extract().replace(',','')
    print 'cur_amt: ' + prod['cur_amt']
    prod['cur_rate'] = hxs.xpath('//div[@class="borrow_list"]/table/tbody/tr/td[2]/text()')[0].extract().split('：')[1].strip()
    print 'cur_rate: ' + prod['cur_rate']

def work(year, page):
    url = 'http://www.ppdai.com/blacklist/%s_m0_p%s'%(year, page) 
    print url
    hxs = Selector(text=get_html_by_data(url))
    tr_list = hxs.xpath('//table[@class="black_table"]/tr')
    print 'len(tr_list): ' + str(len(tr_list))
    if len(tr_list) == 0:
        return False
    for tr in tr_list:
        try:
            prod = {}
            prod['user'] = tr.xpath('./td[1]/a/text()')[0].extract()
            print 'user: ' + prod['user']
            prod['capital'] = tr.xpath('./td[3]/p[1]/text()')[0].extract()
            prod['capital'] = prod['capital'].split(':')[1].strip().replace(',','')
            print 'capital: ' + prod['capital']
            crawl_black(prod)
            crawl_detail(prod)
            print prod
            #import pdb;pdb.set_trace()
            save_csv(prod)
        except Exception as e:
            print e
            continue
    return True

if __name__ == '__main__':
    year = sys.argv[1]
    page = 1
    while work(year, page):
        page += 1
    print 'Crawl ' + year + ' finished.'
    print 'Last page: ' + str(page)
