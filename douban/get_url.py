# -*- coding:utf-8 -*-

import urllib2, urllib, cookielib
from scrapy import Selector
import pdb
import sys
import time
import datetime
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
    f = opener.open(req)
    html = f.read()
    html_file = open('test.html','w')
    print >> html_file, html
    f.close()
    download = True
    return html

def work(prod):
    search_url = 'https://movie.douban.com/subject_search?search_text=%s&cat=1002' % prod['title']
    print 'search:' + search_url
    hxs = Selector(text=get_html_by_data(search_url))
    import pdb;pdb.set_trace()
    prod['url'] = hxs.xpath('//div[@class="pl2"]/a/@href')[0].extract()

with open('err.csv', 'r') as movie_file, open('movie_url.csv', 'a') as url_file:
    lines = movie_file.readlines()
    total_cnt = len(lines)
    cur = 0
    for line in lines:
        cur += 1
        res = line.strip().split(';')
        prod = {}
        prod['title'] = res[0].replace(',','')
        prod['year'] = res[1].replace(',','')
        try:
            print str(cur) + '/' + str(total_cnt) + ' ' + prod['title']
            work(prod)
            print 'detail:' + prod['url']
            resline = '%s,%s,%s' % (prod['title'], prod['year'], prod['url'])
            print >> url_file, resline.encode('utf-8')
        except:
            with open('err2.csv', 'a') as err_file:
                print >> err_file, line.strip().encode('utf-8')
