#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import re
from scrapy import Selector
reload(sys)
sys.setdefaultencoding('utf-8')
sys.setrecursionlimit(1000000)

p = re.compile(r'\d+')
sid = 0
aid_dict = {}
with open('aid.conf','r') as aid_file:
    aid_list = aid_file.readlines()
for aid in aid_list:
    res = aid.strip().split(' ')
    aid_dict[res[1]] = res[0]

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

def crawl_prod(url,addr):
    hxs = Selector(text=get_html_by_data(url))
    prod = {}
    global sid
    prod['sid'] = sid
    sid += 1
    prod['city_id'] = 9
    prod['catid'] = 12
    prod['description'] = addr
    prod['name'] = hxs.xpath('//h1/text()')[0].extract()
    print 'name: ' + prod['name']
    prod['c_fangjia'] = hxs.xpath('//em[@class="comm-avg-price"]/text()')[0].extract()
    print 'junjia: ' + prod['c_fangjia']
    prod['content'] = hxs.xpath('//div[@class="desc-cont"]/text()')[0].extract()
    print 'content: ' + prod['content']
    dt_list = hxs.xpath('//div[@class="comm-list clearfix"]/dl/dt/text()')
    dd_list = hxs.xpath('//div[@class="comm-list clearfix"]/dl/dd')
    for i in range(min(len(dt_list), len(dd_list))):
        k = dt_list[i].extract().encode('utf-8')
        part = dd_list[i]
        value = None
        if k == "所在版块":
            key = 'aid'
            value = aid_dict[part.xpath('./a/text()')[0].extract().strip().encode('utf-8')]
        elif k == "地址":
            map_url = part.xpath('./a/@href')[0].extract().strip()
            l1 = map_url.split('l1=')[1].split('&')[0]
            l2 = map_url.split('l2=')[1].split('&')[0]
            prod['map_lng'] = l2
            prod['map_lat'] = l1
            print 'map_lng: ' + prod['map_lng']
            print 'map_lat: ' + prod['map_lat']
        elif k == "总建面":
            key = "c_daxiao"
            value = part.xpath('./text()')[0].extract()
            value = p.findall(value)[0]
        elif k == "总户数":       
            key = "c_hushu"
            value = part.xpath('./text()')[0].extract()
            value = p.findall(value)[0]
        elif k == "停车位": 
            key = "c_tingchewei"      
            value = part.xpath('./text()')[0].extract()
            value = p.findall(value)[0]
        elif k == "开发商":    
            key = "c_kfs"   
            value = part.xpath('./text()')[0].extract()
        elif k == "物业公司":
            key = "c_wuyeguanli"       
            value = part.xpath('./text()')[0].extract()
        elif k == "建造年代":  
            key = "c_niandai"     
            value = part.xpath('./text()')[0].extract()
 
        if value != None:
            prod[key] = value
            print key + ': ' + value
    write_csv(prod)

def add(key, prod):
    if key in prod:
        return str(prod[key]).replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def write_csv(prod):
    with open('modoer_subject.conf','r') as conf_file:
        lines = conf_file.readlines()
    
    key_list = lines[0].strip().split(' ')
    file = open('modoer_subject.csv','a')
    resline = ""
    for key in key_list:
        resline += add(key, prod)
    print >> file, resline.encode('utf-8')

    key_list = lines[1].strip().split(' ')
    file = open('modoer_subject_shops.csv','a')
    resline = ""
    for key in key_list:
        resline += add(key, prod)
    print >> file, resline.encode('utf-8')

def work(start_url):
    print 'list page: ' + start_url
    hxs = Selector(text=get_html_by_data(start_url))
    item_list = hxs.xpath('//ul[@class="list"]/li[@class="list_item"]')
    for item in item_list:
        try:
            content_url = item.xpath('./a/@href')[0].extract()
            print 'content_url: ' + content_url
            addr = item.xpath('.//div[@class="details"]/p/text()')[0].extract().split(']')[1]
            print 'addr: ' + addr
            crawl_prod(content_url, addr)
        except Exception as e:
            print 'skip item'
            print e
    
    try:
        next_url = hxs.xpath('//a[@class="aNxt"]/@href')[0].extract()
    except Exception as e:
        print 'Crawl finished'
        return
    work(next_url)

if __name__ == '__main__':
   global sid 
   sid = int(sys.argv[1])
   work('http://shanghai.anjuke.com/community/')
