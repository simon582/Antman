#-*- coding:utf-8 -*-
import sys
import urllib, urllib2, cookielib, hashlib
reload(sys)
sys.setdefaultencoding('utf-8')
from scrapy import Selector

baseword = '审批改革'

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

def work():
    with open('region.conf','r') as region_file:
        region_list = region_file.readlines()
    for region in region_list:
        region = region.strip()
        print region
        start_url = 'http://info.search.news.cn/result.jspa?ss=2&t=1&t1=0&rp=10&np=1&n1='+ urllib.quote(baseword) + '+' + urllib.quote(region)
        print 'url: ' + start_url
        hxs = Selector(text=get_html_by_data(start_url))
        cnt = hxs.xpath('//div[@class="newsmenu"]/table/tr/td[3]/text()')[0].extract()
        print cnt        

if __name__ == "__main__":
    work()
