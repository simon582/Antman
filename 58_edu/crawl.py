#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import pymongo
import requests
from scrapy import Selector
reload(sys)
sys.setdefaultencoding('utf-8')
curr_ip_pos = 0
ip_list = []
def reset():
    print 'Reset IP list......'
    global curr_ip_pos
    global ip_list
    response = requests.get('http://121.41.122.106:8080/ip/')
    ip_list = response.text.split(' ')
    for i in range(len(ip_list)):
        ip_list[i] = ip_list[i].strip()
    curr_ip_pos = 0
    if len(ip_list) > 0:
        print 'Reset IP successfully!'
    else:
        print 'Reset IP failed!'
        exit(-1)

def get_html_by_data(url, use_cookie=False):
    global curr_ip_pos
    while True:
        try:
            proxy = {'http':ip_list[curr_ip_pos]}
            response = requests.get(url, proxies=proxy, timeout=3)
            if response.status_code != requests.codes.ok:
                curr_ip_pos += 1
                print 'Get Error! Try Again! curr_ip_pos: ' + str(curr_ip_pos)
                if curr_ip_pos >= len(ip_list) - 1:
                    reset()
                continue
            html = response.text
            html_file = open('test.html','w')
            print >> html_file, html
            if html.find('redirect failed') != -1 or html.find('Authorization Required') != -1 or html.find('Page Not found') != -1 or html.find('请输入验证码') != -1 or html.find('请求过于频繁') != -1:
                curr_ip_pos += 1
                print 'Get Error! IP is blocked! curr_ip_pos: ' + str(curr_ip_pos)
                if curr_ip_pos >= len(ip_list) - 1:
                    reset()
            return html
        except Exception as e:
            curr_ip_pos += 1
            print 'Get Error! Try Again! curr_ip_pos: ' + str(curr_ip_pos)
            if curr_ip_pos >= len(ip_list) - 1:
                reset()

def get_html_by_data2(url, use_cookie=False):
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
    f = opener.open(req, timeout=5)
    html = f.read()
    html_file = open('test.html','w')
    print >> html_file, html
    f.close()
    return html

def crawl_prod_profile(url, city_name, keyword, tel):
    hxs = Selector(text=get_html_by_data(url))
    prod = {}
    prod['city_name'] = city_name
    prod['keyword'] = keyword
    prod['tel'] = tel
    print 'tel: ' + tel
    try:
        prod['region'] = ""
        region_list = hxs.xpath('//div[@class="nav"]/span/a/text()')
        for region in region_list:
            prod['region'] += region.extract().strip() + ' '
        print 'region: ' + prod['region']
        prod['title'] = hxs.xpath('//h1/text()')[0].extract().strip()
        print 'title: ' + prod['title']
        prod['publish_time'] = hxs.xpath('//div[@class="details_time"]/text()')[0].extract().split('：')[1]
        print 'publish_time: ' + prod['publish_time']
        prod['address'] = hxs.xpath('//div[@class="right_add"]/p/text()')[0].extract().strip()
        print 'address: ' + prod['address']
        write_csv(prod)
    except Exception as e:
        print e

def crawl_prod(url, city_name, keyword):
    hxs = Selector(text=get_html_by_data(url))
    prod = {}
    prod['city_name'] = city_name
    prod['keyword'] = keyword
    try:
        prod['region'] = ""
        region_list = hxs.xpath('//div[@class="nav"]/span/a/text()')
        for region in region_list:
            prod['region'] += region.extract().strip() + ' '
        print 'region: ' + prod['region']
        prod['title'] = hxs.xpath('//h1/text()')[0].extract().strip()
        print 'title: ' + prod['title']
        prod['publish_time'] = hxs.xpath('//li[@class="time"]/text()')[0].extract()
        print 'publish_time: ' + prod['publish_time']
        prod['company'] = hxs.xpath('//div[@class="userinfo"]/h2/text()')
        if len(prod['company']) > 0:
            prod['company'] = prod['company'][0].extract().strip()
            print 'company: ' + prod['company']
        else:
            prod['company'] = "" 

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
            elif key.find('授课形式') != -1:
                key = 'class_type'
            else:
                continue
            content = ""
            content_list = item.xpath('./text()|./a/text()')
            for c in content_list:
                content += c.extract().strip()
            prod[key] = content
            print key + ': ' + content
        #import pdb;pdb.set_trace()
        write_csv(prod)
    except Exception as e:
        print e

def add(key, prod):
    if key in prod:
        return prod[key].replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def write_csv(prod):
    file = open('result/' + prod['city_name'] + '.csv','a')
    resline = ""
    resline += add('keyword',prod)
    resline += add('region',prod)
    resline += add('title',prod)
    resline += add('publish_time',prod)
    resline += add('company',prod)
    resline += add('contact',prod)
    resline += add('tel',prod)
    resline += add('address',prod)
    resline += add('cat',prod)
    resline += add('class_type',prod)
    print >> file, resline.encode('utf-8')

def work(base_url, city_name, keyword, page):
    #import pdb;pdb.set_trace()
    print 'Current: ' + city_name + ' ' + keyword
    url = base_url + 'pn' + str(page) + '/'
    print url
    hxs = Selector(text=get_html_by_data(url))
    term_list = hxs.xpath('//div[@id="infolist"]/table/tr')
    if len(term_list) == 0:
        return
    for term in term_list:
        try:
            a = term.xpath('./td/div/a/@href')[0]
            print a.extract()
            prod_url = a.extract()
            if keyword == "家教个人":
                tel = term.xpath('.//b[@class="tele"]/text()')
                if len(tel) > 0:
                    crawl_prod_profile(prod_url, city_name, keyword, tel[0].extract())
            else:
                crawl_prod(prod_url, city_name, keyword)
        except Exception as e:
            print e
            continue
    work(base_url, city_name, keyword, page + 1)

if __name__ == '__main__':
    part = int(sys.argv[1])
    
    with open('city_list','r') as city_file, open('cat_list','r') as cat_file:
        city_list = city_file.readlines()
        cat_list = cat_file.readlines()
    
    l = len(city_list) / 10 + 1
    for i in range(part * l, (part+1) * l):
        if i >= len(city_list):
            break
        city = city_list[i]
        res = city.strip().split(' ')
        url = res[0]
        city_name = res[1]
        for cat in cat_list:
            try:
                res = cat.strip().split(' ')
                work(url + res[0].strip() + '/', city_name, res[1], 1)
            except Exception as e:
                print e
                continue
        print 'Crawl Finished! ' + city_name
