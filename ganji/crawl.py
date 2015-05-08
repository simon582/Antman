#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import json
import hashlib
import re
from random import randint
from scrapy import Selector
reload(sys)
sys.setdefaultencoding('utf-8')

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
    if fake_ip:
        ip = "%s.%s.%s.%s" % (str(randint(0,255)), str(randint(0,255)), str(randint(0,255)), str(randint(0,255)))
        req.add_header("X-Forwarded-For", ip)
    req.add_header("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36")
    f = opener.open(req)
    html = f.read()
    html_file = open('test.html','w')
    print >> html_file, html
    f.close()
    return html

def filter(title):
    if title.find('同学') != -1 or title.find('大学生') != -1:
        return True
    return False

def work_zypx(city, cat, url, page):
    print city + ' ' + cat + ' ' + url + ' ' + str(page)
    url += '/o' + str(page)
    print url    
    hxs = Selector(text=get_html_by_data(url, fake_ip=True))
    li_list = hxs.xpath("//li[@class='list-img clearfix']|//li[@class='list-noimg clearfix']")
    print 'len: ' + str(len(li_list))
    for li in li_list:
        try:
            prod = {}
            prod['title'] = ""
            title_list = li.xpath('.//a[@class="list-info-title"]/text()|.//a[@class="list-info-title"]/span/text()')
            for title in title_list:
                prod['title'] += title.extract().replace(' ','').strip()
            print 'title: ' + prod['title']
            if filter(prod['title']):
                continue
            prod['url'] = li.xpath('.//a[@class="list-info-title"]/@href')[0].extract()
            print 'url: ' + prod['url']
            crawl_prod(prod)
        except Exception as e:
            print e
            continue

def work_others(city, cat, url):
    print city + ' ' + cat + ' ' + url + str(page)
    url += '/o' + str(page)
    print url    
    hxs = Selector(text=get_html_by_data(url, fake_ip=True))
    li_list = hxs.xpath("//li[@class='list-img clearfix']|//li[@class='list-noimg clearfix']")
    print 'len: ' + str(len(li_list))
    for li in li_list:
        try:
            prod = {}
            prod['title'] = ""
            title_list = li.xpath('.//a[@class="f14"]/text()|.//a[@class="f14 log_count"]/text()')
            for title in title_list:
                prod['title'] += title.extract().replace(' ','').strip()
            print 'title: ' + prod['title']
            if filter(prod['title']):
                continue
            prod['url'] = li.xpath('.//a[@class="f14"]/@href|.//a[@class="f14 log_count"]/@href')[0].extract()
            print 'url: ' + prod['url']
            crawl_prod(prod)
        except Exception as e:
            print e
            continue

def handle_details(prod, key, value):
    if key == "联系人":
        prod['contact'] = value
        print 'contact: ' + prod['contact']
        if prod['contact'].find('老师') == -1 and prod['contact'].find('校长') == -1:
            print 'Filter by contact'
            return
    if key == "联系电话":
        prod['tel'] = value
        print 'tel: ' + prod['tel']
        if prod['tel'][:3] == "400":
            print 'Filter by 400 tel'
            return
    if key == "联系QQ":
        prod['qq'] = value
        print 'qq: ' + prod['qq']
    if key == "线上联系" and (value.find('QQ') != -1 or value.find('qq') != -1):
        prod['qq'] = value.replace('QQ','').replace('：','').replace(':','').strip()
        print 'qq: ' + prod['qq'] 

def crawl_prod(prod):
    prod['url'] = 'http://anshan.ganji.com/jixujiaoyurenzheng/1559316326x.htm'
    hxs = Selector(text=get_html_by_data(prod['url'], fake_ip=True))
    li_list = hxs.xpath('//ul[@class="cont-info clearfix"]/li')
    if len(li_list) > 0:
        for li in li_list:
            value = key = ""
            ks = li.xpath('./span/text()')
            for k in ks:
                key += k.extract().strip().replace('：','')
            vs = li.xpath('./i/text()|./text()')
            for v in vs:
                value += v.extract().strip()
            #print key + value
            handle_details(prod, key, value)
    else:
        li_list = hxs.xpath('//div[@class="info"]/ul/li')
        if len(li_list) == 0:
            return
        for li in li_list:
            try:
                key = li.xpath('./span/text()')[0].extract().replace('：','').strip()
                value = li.xpath('./p/text()')[0].extract().replace('（','').strip()
                #print key + value
                handle_details(prod, key, value)
                if key == '联系电话':
                    img_url = 'http://anshan.ganji.com/' + li.xpath('./p/span/img/@src')[0].extract()
                    print 'img_url: ' + img_url 
            except:
                continue
    import pdb;pdb.set_trace()
    #save_csv(prod) 

def work(city, cat, url, page):
    if cat == '职业培训':
        return work_zypx(city, cat, url, page)
    else:
        return work_others(city, cat, url, page) 

if __name__ == "__main__":
    with open('cat_list') as cat_file, open('city_list') as city_file:
        cat_list = cat_file.readlines()
        city_list = city_file.readlines()
        for ct_line in city_list:
            city_name = ct_line.split(' ')[0]
            url = ct_line.split(' ')[1].strip()
            for cat_line in cat_list:
                cat_name = cat_line.split(',')[0]
                cat = cat_line.split(',')[1].strip()
                try:
                    page = 1
                    while work(city_name, cat_name, url + cat, page):
                        page += 1
                except Exception as e:
                    print e
                    print 'Do not find: ' + city_name + ' ' + cat_name
                    continue
