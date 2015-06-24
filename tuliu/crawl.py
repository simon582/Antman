#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import hashlib
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

def add(key, prod):
    if prod.has_key(key):
        return prod[key].replace('\r','').replace('\n','').replace(',',' ') + ','
    return ','

def save_csv(prod):
    file = open('result_tuliu.csv','a')
    resline = ""
    resline += add('title', prod)
    resline += add('region', prod)
    resline += add('url', prod)
    resline += add('type', prod)
    resline += add('attr', prod)
    resline += add('release_time', prod)
    resline += add('update_time', prod)
    resline += add('area', prod)
    resline += add('year_limit', prod)
    resline += add('price', prod)
    resline += add('pay_type', prod)
    print >> file, resline.encode('gbk')

def crawl_details(prod):
    hxs = Selector(text=get_html_by_data(prod['url'], fake_ip=True))
    li_list = hxs.xpath('//div[@class="con_bg"]/ul/li')
    for li in li_list:
        try:
            text = li.xpath('./text()')[0].extract().strip().replace(' ','').replace('\n','').replace('\r','')
            key = text.split('：')[0]
            val = text.split('：')[1]
            print key + ': ' + val
        except:
            continue
        if key == "土地类型":
            prod['type'] = val  
        if key == "流转性质":
            prod['attr'] = val
        if key == "发布时间":
            prod['release_time'] = val
        if key == "更新时间":
            prod['update_time'] = val
        if key == "土地面积":
            prod['area'] = val
        if key == "使用权年限":
            prod['year_limit'] = val
        if key == "价格" or key == "一口价":
            prod['price'] = val
        if key == "付款方式":
            prod['pay_type'] = val

def work(page):
    url = 'http://www.tuliu.com/list-pg' + str(page) + '.html#sub_list_b'
    print 'Current page: ' + str(page) + ' list url:' + url
    hxs = Selector(text=get_html_by_data(url, fake_ip=True))
    dl_list = hxs.xpath("//div[@class='list_list']/dl")
    print "len: " + str(len(dl_list))
    for dl in dl_list:
        try:
            print '--------------------------------------------------------'
            prod = {}
            prod['title'] = dl.xpath('.//h2/a/text()')[0].extract().strip()
            print 'title: ' + prod['title']
            prod['url'] = dl.xpath('.//h2/a/@href')[0].extract().strip()
            print 'detail url: ' + prod['url']
            prod['region'] = dl.xpath('.//p[@class="gre"]/text()')[0].extract().strip()
            print 'region: ' + prod['region']
            crawl_details(prod)
            save_csv(prod)
            #import pdb;pdb.set_trace()
        except Exception as e:
            print e
            continue

if __name__ == "__main__":
    '''
    if len(sys.argv) != 3:
        print 'cmd: python crawl.py start_page end_page'
        exit(-1)
    try:
        start_page = int(sys.argv[1])
        end_page = int(sys.argv[2])
    except Exception as e:
        print e
        print 'parameters error'
        exit(-1)
    '''
    start_page = 1
    end_page = 2
    for page in range(start_page, end_page+1):
        try:
            work(page)
        except Exception as e:
            print 'Cannot crawl page: ' + str(page)
            break
    print 'Crawl finished from page %s to %s.'%(str(start_page), str(end_page))
