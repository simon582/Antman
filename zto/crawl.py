#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import hashlib
import Image
import pymongo
from scrapy import Selector
reload(sys)
sys.setdefaultencoding('utf-8')

province_list = []
with open('province_list','r') as pro_file:
    lines = pro_file.readlines()
    for line in lines:
        province_list.append(line.strip())

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

def add(key, prod):
    if key in prod:
        return prod[key].replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def save_csv(prod):
    file = open('result.csv','a')
    resline = ""
    resline += add('kd', prod)
    resline += add('name', prod)
    resline += add('province', prod)
    resline += add('city', prod)
    resline += add('zone', prod)
    resline += add('addr', prod)
    resline += add('linkman', prod)
    resline += add('phone1', prod)
    resline += add('phone2', prod)
    resline += add('deliver', prod)
    resline += add('mobile', prod)
    resline += add('ts_tel', prod)
    #resline += add('sub_tel', prod)
    print >> file, resline.encode('utf-8')

def crawl_details(prod):
    print prod['url']
    html = get_html_by_data(prod['url'], use_cookie=False)
    hxs = Selector(text=html)
    tr_list = hxs.xpath('//div[@class="fl w360 brief"]/ul/li')
    for tr in tr_list:
        try:
            key = tr.xpath('./span/text()')[0].extract().replace('：','').strip()
            value = tr.xpath('./text()')[0].extract().strip()
            ikey = "null"
            if key == "网点名称":
                ikey = "name"
            elif key == "所在地区":
                ikey = "region"
            elif key == "经理姓名":
                ikey = "linkman"
            elif key == "经理手机":
                ikey = "mobile"
            elif key == "查询电话":
                ikey = "phone1"
            elif key == "业务电话":
                ikey = "phone2"
            elif key == "公司地址":
                ikey = "addr"
            if ikey != "null":
                prod[ikey] = value.replace(u'\xa0','')
        except:
            continue
    tr_list = hxs.xpath('//div[@class="websitebd"]/div[@class="part1"][2]/table/tbody/tr')
    prod['deliver'] = ""
    for tr in tr_list:
        try:
            key = tr.xpath('./th/text()')[0].extract()
            value_list = tr.xpath('./td/text()')
            if key == "派送范围":
                for value in value_list:
                    prod['deliver'] += value.extract()
                break 
        except:
            continue   
 
    if "region" in prod:
        res = prod['region'].split(' - ')
        if len(res) >= 2:
            prod['province'] = prod['city'] = res[0]
            if res[0].find('省') != -1 or res[0].find('自治区') != -1 or res[1].find('市') != -1:
                prod['city'] = res[1]
            if res[1].find('区') != -1 or res[1].find('县') != -1:
                prod['zone'] = res[1]
    if (not "zone" in prod) and ('addr' in prod):
        if prod['addr'].find('县') != -1:
            prod['zone'] = prod['addr'].split('县')[0] + '县'
            if prod['zone'].find('市') != -1:
                prod['zone'] = prod['zone'].split('市')[1]
        elif prod['addr'].find('区') != -1:
            prod['zone'] = prod['addr'].split('区')[0] + '区'
            if prod['zone'].find('市') != -1:
                prod['zone'] = prod['zone'].split('市')[1]
    
    for key,value in prod.items():
        print key + ": " + value 

def crawl_prods(base_url, province, page):
    url = base_url + 'page=' + str(page) + '&Place=' + province
    print url
    html = get_html_by_data(url, use_cookie=False)
    hxs = Selector(text=html)
    a_list = hxs.xpath('//div[@class="part1"]/table/tbody/tr/td[1]/a')
    if len(a_list) == 0:
        return
    for a in a_list:
        try:
            prod = {}
            prod['kd'] = 'zhongtong'
            prod['name'] = a.xpath('./text()')[0].extract().strip()
            prod['url'] = "http://www.zto.cn" + a.xpath('./@href')[0].extract()
            crawl_details(prod)
            save_csv(prod) 
        except Exception as e:
            print e
    crawl_prods(base_url, province, page+1)    

if __name__ == '__main__':
    part = int(sys.argv[1])
    for i in range(part * 5, (part+1) * 5):
        if i >= len(province_list):
            break
        print 'process: ' + str(i)
        start_url = 'http://www.zto.cn/GuestService/SiteQuery?'
        crawl_prods(start_url, province_list[i], 1)
    print 'Crawl Finished!'
