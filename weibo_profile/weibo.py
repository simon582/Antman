# -*- coding: utf-8 -*-
import time
import urllib2
import urllib
import cookielib
import sys
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
    html_file = open('debug.html','w')
    print >> html_file, html
    f.close()
    return html

def add(key, prod):
    if prod.has_key(key):
        return prod[key].replace('\r','').replace('\n','').replace(',',' ') + ','
    return ','

def save_csv(prod):
    file = open('result.csv','a')
    resline = ""
    resline += add('id', prod)
    resline += add('wb_name', prod)
    resline += add('date', prod)
    resline += add('quote_reason', prod)
    resline += add('content', prod)
    #resline += add('img', prod)
    resline += add('quote', prod)
    resline += add('comment', prod)
    resline += add('like', prod)
    print >> file, resline.encode('utf-8')

def work(wb_name, id, page):
    list_url = 'http://weibo.cn/' + id + '/profile?&page=' + str(page)
    print list_url
    hxs = Selector(text=get_html_by_data(list_url, use_cookie=True))
    wb_list = hxs.xpath('//div[@class="c"]')
    if len(wb_list) <= 3:
        return False
    print 'Find ' + str(len(wb_list)) + ' weibo elements'
    for wb in wb_list:
        try:
            prod = {}
            prod['id'] = id
            prod['wb_name'] = wb_name
            prod['content'] = ""
            content_list = wb.xpath('.//span[@class="ctt"]/a/text()|.//span[@class="ctt"]/text()|.//span[@class="ctt"]/span/text()')
            for elem in content_list:
                prod['content'] += elem.extract()
            print prod['content']
            prod['quote_reason'] = ''
            quote_div = wb.xpath('./div[3]')
            if quote_div:
                quote_list = quote_div.xpath('.//text()')
                for quote in quote_list:
                    if quote.extract().find('赞[') != -1:
                        break
                    prod['quote_reason'] += quote.extract().strip()
            print 'quote_reason: ' + prod['quote_reason']
            date = wb.xpath('.//span[@class="ct"]/text()')[0].extract()
            prod['date'] = date.split(' ')[0]
            if prod['date'].find('今天') != -1 or prod['date'].find('前') != -1:
                prod['date'] = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            elif prod['date'].find('月') != -1:
                prod['date'] = '2015-' + prod['date'].replace('月','-').replace('日','')
            print prod['date']
            if prod['date'].find('2012') != -1 or prod['date'].find('2013-5') != -1 or prod['date'].find('2013-6') != -1:
                print 'out of date'
                return False

            '''
            img_list = wb.xpath('.//img[@class="ib"]')
            if len(img_list) > 0:
                prod['img'] = '1'
            else:
                prod['img'] = '0'
            print 'has img: ' + prod['img']
            '''

            text_list = wb.xpath('.//a/text()')
            for text in text_list:
                text = text.extract()
                if text.find('转发') != -1:
                    eq1 = text.find('[')
                    eq2 = text.find(']')
                    prod['quote'] = text[eq1+1:eq2]
                    print 'quote: ' + prod['quote']
                if text.find('评论') != -1:
                    eq1 = text.find('[')
                    eq2 = text.find(']')
                    prod['comment'] = text[eq1+1:eq2]
                    print 'comment: ' + prod['comment']
                if text.find('赞') != -1:
                    eq1 = text.find('[')
                    eq2 = text.find(']')
                    prod['like'] = text[eq1+1:eq2]
                    print 'like: ' + prod['like']
            save_csv(prod)
        except Exception as e:
            print e
            continue
    return True

if __name__ == '__main__':
    id_list = []
    with open('id.conf') as id_file:
        id_list = id_file.readlines()
    for line in id_list:
        try:
            id = line.strip().split(' ')[1]
            wb_name = line.strip().split(' ')[0]
            page = 1
            while True:
                if work(wb_name, id, page):
                    page += 1
                else:
                    break
        except Exception as e:
            print e
            continue
