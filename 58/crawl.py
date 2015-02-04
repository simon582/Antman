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

def crawl_prod(url, city_name, keyword):
    hxs = Selector(text=get_html_by_data(url))
    prod = {}
    prod['city_name'] = city_name
    prod['keyword'] = keyword
    try:
        item_list = hxs.xpath('//div[@class="col_sub"]/ul[@class="suUl"]/li')
        for item in item_list:
            key = item.xpath('.//div[@class="su_tit"]/text()')[0].extract()
            if key.find('联系人') != -1:
                prod['contact'] = item.xpath('.//div[@class="su_con"]/a/text()')[0].extract()
                print 'contact: ' + prod['contact']
        prod['tel'] = hxs.xpath('//span[@class="l_phone"]/text()|//span[@id="t_phone"]/text()')[0].extract()
        print 'tel: ' + prod['tel']
        item_list = hxs.xpath('//div[@class="newinfo"]/ul/li')
        for item in item_list:
            try:
                key = item.xpath('.//i[@class="z"]/nobr/text()')[0].extract()
            except:
                continue
            if key.find('详细地址') != -1:
                key = 'address'
            elif key.find('类别') != -1:
                key = 'cat'
            elif key.find('服务区域') != -1:
                key = 'region'
            elif key.find('小类') != -1:
                key = 'detail'
            else:
                continue
            content = ""
            content_list = item.xpath('./text()|./a/text()')
            for c in content_list:
                content += c.extract().strip()
            print key + ': ' + content
            prod[key] = content
        desc = ""
        desc_list = hxs.xpath('//div[@class="descriptionBox"]/article/text()|//div[@class="descriptionBox"]/p/text()')
        for d in desc_list:
            desc += d.extract().strip()
        print 'desc: ' + desc
        prod['desc'] = desc
        #import pdb;pdb.set_trace()
        write_csv(prod)
    except Exception as e:
        print e

def add(key, prod):
    if key in prod:
        return prod[key].replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def write_csv(prod):
    file = open('result.csv','a')
    resline = ""
    resline += add('city_name',prod)
    resline += add('keyword',prod)
    resline += add('contact',prod)
    resline += add('tel',prod)
    resline += add('address',prod)
    resline += add('cat',prod)
    resline += add('region',prod)
    resline += add('detail',prod)
    resline += add('desc',prod)
    print >> file, resline.encode('utf-8')

def work(base_url, city_name, keyword):
    print 'Current: ' + city_name + ' ' + keyword
    url = base_url + urllib.quote(keyword)
    print url
    hxs = Selector(text=get_html_by_data(url))
    a_list = hxs.xpath('//table[@class="tblist"]/tr/td[@class="t"]/a[@class="t"]/@href')
    for a in a_list:
        print a.extract()
        prod_url = a.extract()
        crawl_prod(prod_url, city_name, keyword)

if __name__ == '__main__':
    with open('city_list','r') as city_file, open('keyword_list','r') as word_file:
        city_list = city_file.readlines()
        word_list = word_file.readlines()
    for i in range(0, len(city_list)):
        city = city_list[i]
        res = city.strip().split(' ')
        url = res[0]
        city_name = res[1]
        for word in word_list:
            try:
                work(url + 'sou/?key=', city_name, word.strip())
                work(url + 'sou/pn2/?key=', city_name, word.strip())
            except Exception as e:
                print e
                continue
        print 'Crawl Finished! ' + city_name
        print 'Complete process: ' + str(i*100.0/len(city_list)) + '%'
