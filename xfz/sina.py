#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import hashlib
import Image
import HTMLParser
import os
import zlib
import time
from BeautifulSoup import BeautifulSoup
from scrapy import Selector
reload(sys)
sys.setdefaultencoding('utf-8')
import pymongo

try:
    conn = pymongo.Connection('localhost',27017)
    info_table = conn.content_db.info
    print 'Create mongodb connection successfully.'
except Exception as e:
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
    f = opener.open(req, timeout=20)
    html = unicode(f.read(),'gbk')
    html_file = open('test.html','w')
    print >> html_file, html
    f.close()
    return html

def get_html_by_gzip(url):
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    opener = urllib2.build_opener()
    response = opener.open(request, timeout=20)
    html = response.read()
    gzipped = response.headers.get('Content-Encoding')
    if gzipped:
        html = zlib.decompress(html, 16+zlib.MAX_WBITS)
    else:
        html = ''
    html = html.decode('gbk', 'ignore')
    html_file = open('test.html','w')
    print >>html_file, html
    response.close()
    return html

def crawl_prod(url, prod):
    try:
        html = get_html_by_gzip(url)
        hxs = Selector(text=html)
        p_list = hxs.xpath('//div[@id="articleContent"]/p|//div[@id="artibody"]/p|//div[@class="moduleParagraph"]/p')
        prod['text'] = ""
        for p in p_list:
            text_list = p.xpath('.//text()')
            for text in text_list:
                prod['text'] += text.extract().strip()
        save_db(prod) 
    except Exception as e:
        print e

def crawl_list(url, baseword):
    print 'crawl_list: ' + url
    html = get_html_by_data(url)
    hxs = Selector(text=html)
    item_list = hxs.xpath('//div[@class="box-result clearfix"]')
    if not item_list:
        html = get_html_by_data(url)
        hxs = Selector(text=html)
        item_list = hxs.xpath('//div[@class="box-result clearfix"]')
  
    for item in item_list:
        try:
            prod = {}
            prod['baseword'] = baseword
            content_url = item.xpath('.//h2/a/@href')[0].extract()
            prod['content_url'] = content_url
            print 'url:' + content_url
            title_list = item.xpath('.//h2/a/text()|.//h2/a/span/text()')
            prod['title'] = ""
            for title in title_list:
                prod['title'] += title.extract().strip()
            print 'title: ' + prod['title']
            date = item.xpath('.//span[@class="fgray_time"]/text()')[0].extract()
            prod['ori_date'] = date.strip().split(' ', 1)[1]
            print 'date: ' + prod['ori_date']
            handle_date(prod)
            crawl_prod(content_url, prod)
        except Exception as e:
            print e
            continue        

def handle_date(prod):
    ori_date = prod['ori_date'].strip().encode('utf-8')
    if ori_date.find('月') != -1:
        prod['timestamp'] = time.mktime(time.strptime('2014-'+ori_date, "%Y-%m月%d日 %H:%M"))
    else:
        prod['timestamp'] = time.mktime(time.strptime(ori_date, "%Y-%m-%d %H:%M:%S"))
    prod['date'] = time.strftime("%Y-%m-%d %H:%M", time.localtime(prod['timestamp']))
    print 'date: ' + prod['date']

def add(key, prod):
    if prod.has_key(key):
        return prod[key].replace('\n','').replace('\r','').replace(',',' ').strip() + ','
    else:
        print 'Cannot find key: ' + key
        return ','

def save_db(prod):
    prod['id'] = hashlib.md5(prod['title']).hexdigest().upper()
    info_table.save(prod)

def save_txt(prod):
    file = open('result.csv','a')
    resline = ""
    resline += add('baseword', prod)
    resline += add('date', prod)
    resline += add('title', prod) 
    resline += add('text', prod)
    print >> file, resline.encode('utf-8')

def get_max_page(url):
    try:
        html = get_html_by_data(url)
        hxs = Selector(text=html)
        text = hxs.xpath('//div[@class="result"]/div[@class="l_v2"]/text()')[0].extract() 
        number = text.split('新闻')[1].split('篇')[0]
        max_page = int(number.replace(',','')) / 20 + 2
        return max_page
    except Exception as e:
        print 'get_max_page:' + url
        print e
        return 0

if __name__ == '__main__':
    customer_types = ['消费者','顾客','客户']
    conflicts = ['投诉','索赔','投诉','状告','告上法庭','不满','恶劣','损害','误导','欺骗','欺诈','违法','曝光','危机','丑闻','质量问题','安全问题','道歉','召回','下架','处罚','罚款']
    company_types = ['跨国企业','跨国公司']
    company_names = ['3M','ABB','雅培','苹果公司','巴斯夫','拜耳','宝马','普利司通','佳能','家乐福','可口可乐','戴姆勒','达能','戴尔','杜邦','艾默生','福特','富士通','通用电气','通用汽车','日立','本田','现代汽车','英特尔','强生','卡夫','爱立信','LG','马自达','麦德龙','米其林','三菱','NEC','雀巢','尼桑','诺基亚','诺华','松下','百事','标致','辉瑞','宝洁','理光','罗氏','飞利浦','三星','夏普','索尼','铃木','乐购','东芝','丰田','联合利华','大众汽车','沃尔玛','施乐']
    for customer_type in customer_types:
        for conflict in conflicts:
            baseword = customer_type + '+' + conflict
            #max_page = get_max_page('http://search.sina.com.cn/?ac=product&from=digi_index&source=&range=all&f_name=&col=&ie=utf-8&c=news&q=' + baseword + '&country=&size=&time=&a=&page=' + str(1) + '&pf=2131425517&ps=2132737668&dpc=1')
            for page in range(1, 100):
                print 'query: ' + baseword + ' current: ' + str(page) 
                start_url='http://search.sina.com.cn/?ac=product&from=digi_index&source=&range=all&f_name=&col=&ie=utf-8&c=news&q=' + baseword + '&country=&size=&time=&a=&page=' + str(page) + '&pf=2131425517&ps=2132737668&dpc=1'
                try:
                    crawl_list(start_url, baseword)
                except Exception as e:
                    print 'Error crawl_list:' + start_url
                    print e
                    continue
    print 'Crawl Finished!'
