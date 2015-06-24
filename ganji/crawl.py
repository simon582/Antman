#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import json
import hashlib
import re
import time
import random
from random import randint
from scrapy import Selector
reload(sys)
sys.setdefaultencoding('utf-8')

proxy_ip_list = []
with open('/root/proxy/proxy_list.txt','r') as proxy_file:
    for line in proxy_file.readlines():
        proxy_ip_list.append(line.strip())

def get_html_by_data_new(url, use_cookie=False):
    while True:
        session = requests.Session()
        proxy = random.choice(proxy_ip_list)
        proxies = {
                'http': 'http://'+proxy,
                'https': 'http://'+proxy,
        }
        headers = {
            'Host': 'gz.ganji.com',
            'Referer': 'http://gz.ganji.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
        }
        r = session.get(prod['apk_url'], headers=headers, proxies=proxies)
        if r.content.find('机器人确认') != -1:
            continue
        else:
            f = file('test.html', 'w')
            f.write(r.content)
            f.close()
            return r.content

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
    req.add_header("Referer","http://anshan.ganji.com/")
    f = opener.open(req, timeout=5)
    html = f.read()
    html_file = open('test.html','w')
    print >> html_file, html
    f.close()
    if html.find('机器人确认') != -1:
        print 'Spider is detected by robot.'
        exit(-1)
    return html

def filter(title):
    if title.find('同学') != -1 or title.find('大学生') != -1:
        return True
    return False

def work_zypx(city, cat, url, page):
    print city + ' ' + cat + ' ' + url + ' ' + str(page)
    url += '/o' + str(page)
    print url 
    hxs = Selector(text=get_html_by_data(url, use_cookie=True, fake_ip=True))
    li_list = hxs.xpath("//li[@class='list-img clearfix']|//li[@class='list-noimg clearfix']")
    print 'len: ' + str(len(li_list))
    titles = ""
    for li in li_list:
        try:
            prod = {}
            prod['city'] = city
            prod['cat'] = cat
            prod['title'] = ""
            title_list = li.xpath('.//a[@class="list-info-title"]/text()|.//a[@class="list-info-title"]/span/text()')
            for title in title_list:
                prod['title'] += title.extract().replace(' ','').strip()
            print 'title: ' + prod['title']
            titles += prod['title']
            if filter(prod['title']):
                continue
            prod['url'] = li.xpath('.//a[@class="list-info-title"]/@href')[0].extract()
            if prod['url'].find('http://') == -1:
                prod['url'] = 'http://' + url.split('/')[2] + prod['url']
            print 'url: ' + prod['url']
            crawl_prod(prod)
            time.sleep(1.5)
        except Exception as e:
            print e
            continue
    return hashlib.md5(titles).hexdigest()

def work_others(city, cat, url, page):
    print city + ' ' + cat + ' ' + url + str(page)
    url += '/o' + str(page)
    print url
    hxs = Selector(text=get_html_by_data(url, use_cookie=True, fake_ip=True))
    li_list = hxs.xpath("//li[@class='list-img clearfix']|//li[@class='list-noimg clearfix']")
    print 'len: ' + str(len(li_list))
    titles = ""
    for li in li_list:
        try:
            prod = {}
            prod['city'] = city
            prod['cat'] = cat
            prod['title'] = ""
            title_list = li.xpath('.//a[@class="f14"]/text()|.//a[@class="f14 log_count"]/text()')
            for title in title_list:
                prod['title'] += title.extract().replace(' ','').strip()
            print 'title: ' + prod['title']
            titles += prod['title']
            if filter(prod['title']):
                continue
            prod['url'] = li.xpath('.//a[@class="f14"]/@href|.//a[@class="f14 log_count"]/@href')[0].extract()
            if prod['url'].find('http://') == -1:
                prod['url'] = 'http://' + url.split('/')[2] + prod['url']
            print 'url: ' + prod['url']
            crawl_prod(prod)
            time.sleep(1.5)
        except Exception as e:
            print e
            continue
    return hashlib.md5(titles).hexdigest()

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

def handle_img(prod):
    url = prod['img_url']
    file_path = './img/'
    file_name = hashlib.md5(url.encode('utf8')).hexdigest().upper() + '.png'
    data = urllib2.urlopen(url).read()
    prod['tel'] = file_name
    print 'tel: ' + prod['tel']
    f = file(file_path + file_name, 'wb')
    f.write(data)
    f.close()

def crawl_prod(prod):
    hxs = Selector(text=get_html_by_data(prod['url'], use_cookie=True, fake_ip=True))
    # date
    prod['date'] = hxs.xpath('//i[@class="f10 pr-5"]/text()|//p[@class="p1"]/span[@class="mr35"][1]/text()')[0].extract()
    prod['date'] = prod['date'].strip().replace('发布时间：','')
    print 'date: ' + prod['date']
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
        li_list = hxs.xpath('//div[@class="info"][1]/ul/li')
        if len(li_list) == 0:
            return
        for li in li_list:
            try:
                key = li.xpath('./span/text()')[0].extract().replace('：','').strip()
                value = li.xpath('./p/text()')[0].extract().replace('（','').strip()
                #print key + value
                handle_details(prod, key, value)
                if key == '联系电话':
                    prod['img_url'] = 'http://anshan.ganji.com/' + li.xpath('./p/span/img/@src')[0].extract()
                    print 'img_url: ' + prod['img_url']
                    handle_img(prod)
            except:
                continue
    print prod
    save_csv(prod) 

def add(key, prod):
    if prod.has_key(key):
        return prod[key].replace('\n','').replace('\r','').replace(',',' ').strip() + ','
    else:
        print 'Cannot find key: ' + key
        return ','

def save_csv(prod):
    file = open('csv/' + prod['city'] + '.csv','a')
    resline = ""
    resline += add('city', prod)
    resline += add('cat', prod)
    resline += add('title', prod)
    resline += add('contact', prod)
    resline += add('qq', prod)
    resline += add('tel', prod)
    resline += add('date', prod)
    print >> file, resline.encode('utf-8')

def work(city, cat, url):
    hash_code = ''
    page = 1
    while True:
        if cat == '职业培训':
            new_code = work_zypx(city, cat, url, page)
        else:
            new_code = work_others(city, cat, url, page)
        if hash_code == new_code:
            break
        hash_code = new_code
        page += 1

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
                    work(city_name, cat_name, url + cat)
                except Exception as e:
                    print e
                    print 'Do not find: ' + city_name + ' ' + cat_name
                    continue
