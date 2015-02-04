#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import hashlib
import Image
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

def crawl_author(url, prod):
    html = get_html_by_data(url)
    hxs = Selector(text=html)
    prod['author'] = hxs.xpath('//div[@class="worksInfo"]/table/tr[1]/td[1]/text()')[0].extract().strip()
    if prod['author'] == "":
        author = hxs.xpath('//div[@class="worksInfo"]/table/tr[1]/td[1]/a[1]/text()')
        if author:
            prod['author'] = author[0].extract().strip()

def crawl_prods(url):
    html = get_html_by_data(url, use_cookie=True)
    hxs = Selector(text=html)
    item_list = hxs.xpath('//ul[@class="imgList specWorks clearfix"]/li')
    for item in item_list:
        try:
            prod = {}
            prod['name'] = item.xpath('.//h3/a/@title')[0].extract()
            prod['gj'] = item.xpath('.//ul[@class="dataItem"]/li[2]/span/text()')[0].extract().replace(',','')
            prod['cjj'] = item.xpath('.//ul[@class="dataItem"]/li[3]/span/text()')[0].extract().replace(',','') 
            prod['date'] = item.xpath('.//ul[@class="dataItem"]/li[5]/text()')[0].extract()
            content_url = 'http://auction.artron.net' + item.xpath('.//h3/a/@href')[0].extract()
            crawl_author(content_url, prod)
            print 'name: ' + prod['name']
            print 'author: ' + prod['author']
            print 'gj: ' + prod['gj']
            print 'cjj: ' + prod['cjj']
            print 'date: ' + prod['date']
            save_csv(prod) 
        except Exception as e:
            print e
    next_url = 'http://auction.artron.net' + hxs.xpath('//a[@class="page-next"]/@href')[0].extract()
    if next_url != url:
        crawl_prods(next_url)

def crawl_list(url):
    html = get_html_by_data(url)
    hxs = Selector(text=html)
    item_list = hxs.xpath('//ul[@class="dataList"]/li')
    for item in item_list:
        try:
            cj_cnt = item.xpath('.//ul/li[@class="sum"]/text()')[0].extract()
            print 'cj_cnt: ' + cj_cnt
            if cj_cnt.find('--') != -1:
                continue
            content_urls = item.xpath('.//ul[@class="auctList"]/li/a/@href')
            for content_url in content_urls:
                content_url = 'http://auction.artron.net' + content_url.extract()
                print content_url
                crawl_prods(content_url)
        except Exception as e:
            print e
            continue        
    
def add(key, prod):
    if prod.has_key(key):
        return prod[key].replace(',',' ').strip() + ','
    return ','

def save_csv(prod):
    file = open('result.csv','a')
    resline = ""
    resline += add('name', prod)
    resline += add('author', prod)
    resline += add('date', prod)
    resline += add('gj', prod)
    resline += add('cjj', prod)
    print >> file, resline.encode('utf-8')

if __name__ == '__main__':
    part = int(sys.argv[1])
    start = 8 + part * 20
    end = 8 + (part + 1) * 20
    for page in range(start, end):
        print 'current page: ' + str(page)
        start_url='http://auction.artron.net/result/pmh-0-0-2-0-' + str(page) + '/'
        crawl_list(start_url)
    print 'Crawl Finished!'
