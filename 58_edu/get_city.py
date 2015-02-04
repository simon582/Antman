#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
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
    f = opener.open(req)
    html = f.read()
    html_file = open('test.html','w')
    print >> html_file, html
    f.close()
    return html

def work(url):
    hxs = Selector(text=get_html_by_data(url))
    a_list = hxs.xpath('//dl[@id="clist"]/dd/a')
    for a in a_list:
        href = a.xpath('.//@href')[0].extract()
        city = a.xpath('.//text()')[0].extract()
        print href + ' ' + city

if __name__ == '__main__':
    work('http://www.58.com/changecity.aspx')
