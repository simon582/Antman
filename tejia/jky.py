#encoding:utf-8
import MySQLdb
from scrapy import Selector
import sys
sys.path.append('/usr/lib/python2.6/site-packages')
import re
import urllib
import urllib2
import cookielib
import hashlib
import os
import time
import requests
import json
import random
reload(sys)
sys.setdefaultencoding('utf-8')

USER_AGENTS = [
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.2) ',
    'Gecko/2008092313 Ubuntu/8.04 (hardy) Firefox/3.1',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) ',
    'Gecko/20070118 Firefox/2.0.0.2pre',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.7pre) Gecko/20070815 ',
    'Firefox/2.0.0.6 Navigator/9.0b3',
    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_4_11; en) AppleWebKit/528.5+',
    ' (KHTML, like Gecko) Version/4.0 Safari/528.1',
    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; sv-se) AppleWebKit/419 ',
    '(KHTML, like Gecko) Safari/419.3',
    'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0;)',
    'Mozilla/4.08 (compatible; MSIE 6.0; Windows NT 5.1)',
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
]

cookie_str = "_Qt=1421909225685; _ga=GA1.2.1829769921.1421909222; activity_tips=close; _QM=1; sid=lbtvndrmsq6524t8pp5stm6p77; newPerson=1; server_time=1422610101; _pk_id.1.da7f=ddcf6747f1dee525.1421909222.5.1422610100.1422602224.; _pk_ses.1.da7f=*; Hm_lvt_1261e11de2864ee1cb9c180175bfa028=1421909222,1422350466; Hm_lpvt_1261e11de2864ee1cb9c180175bfa028=1422610100"

url_dict = {}
with open('jky.conf','r') as conf_file:
    lines = conf_file.readlines()
    for line in lines:
        res = line.split(',')
        if len(res) == 2 and res[1] != "":
            url_dict[res[0]] = res[1].strip()

try:
    conn = MySQLdb.connect(host="localhost",user="root",passwd="fzjy1201",db="tejia",charset="utf8")
    cursor = conn.cursor()
except Exception as e:
    print e
    print 'Cannot connect MySQL!'
    exit(-1)

def get_html_by_data(url, use_cookie=False):
    headers = {
        "Connection":"keep-alive",
        "Host":"www.jiukuaiyou.com",
        "Referer":"http://www.jiukuaiyou.com/",
        "User-agent":random.choice(USER_AGENTS),
        "Cookie":cookie_str,
    }
    res = requests.get(url, headers=headers)
    html = res.text
    return html

def save_prod(prod):
    for key, value in prod.items():
        print key + ": " + value
    if (not 'item_url' in prod) or prod['item_url'] == "":
        return
    id = hashlib.md5(prod['item_url']).hexdigest().upper()
    sql = "insert into jky(id,title,act_price,ori_price,item_url,left_time,pic_url,now_time,cat,sold) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    params = (id,prod['title'],prod['act_price'],prod['ori_price'],prod['item_url'],prod['left_time'],prod['pic_url'],prod['now_time'],prod['cat'],prod['sold'])
    n = cursor.execute(sql, params)
    print 'mysql insert result: ' + str(n)

def crawl_detail(prod):
    html = get_html_by_data(prod['item_url'])
    ts = html.split('timestamp=')[1].split('-')[0]
    delta = int(ts) - time.time()
    day = int(delta / (24*60*60))
    delta = delta - day * (24*60*60)
    hour = int(delta / (60*60))
    delta = delta - hour * (60*60)
    minute = int(delta / 60)
    if day > 0:
        prod['left_time'] = str(day) + "天" + str(hour) + "小时" + str(minute) + "分钟"
    elif hour > 0:
        prod['left_time'] = str(hour) + "小时" + str(minute) + "分钟"
    elif minute > 0:
        prod['left_time'] = str(minute) + "分钟"

def crawl_shop_name(prod):
    try:
        html = get_html_by_data(prod['go_link'])
        flag = '<iframe frameborder="0" scrolling="no" src="'
        if html.find(flag) != -1:
            tb_url = html.split(flag)[1].split('"')[0]
        elif html.find('url=') != -1:
            tb_url = html.split('url=\'')[1].split('\'')[0]
        print tb_url
        import pdb;pdb.set_trace()
    except Exception as e:
        print e
        import pdb;pdb.set_trace()

def work(cat, start_url, page):
    print cat + ' ' + start_url + ' page:' + str(page)
    url = start_url + str(page)
    hxs = Selector(text=get_html_by_data(url))
    item_list = hxs.xpath('//div[@class="main pr mt25 clear"]/ul/li')
    if len(item_list) == 0:
        print cat + ' crawl finished'
        return
    for item in item_list:
        try:
            prod = {}
            prod['cat'] = cat
            prod['title'] = item.xpath('.//a[@class="title"]/text()')[0].extract().strip()
            prod['act_price'] = item.xpath('.//span[@class="price-current"]/text()')[0].extract().strip()
            prod['ori_price'] = item.xpath('.//span[@class="price-old"]/text()')[0].extract().strip()
            prod['sold'] = item.xpath('.//span[@class="sold"]/em/text()')[0].extract().strip()
            if prod['sold'].find('w') != -1:
                prod['sold'] = str(int(float(prod['sold'].replace('w','')) * 10000))
            prod['item_url'] = item.xpath('.//div[@class="pic-img"]/a/@href')[0].extract().strip()
            #prod['go_link'] = item.xpath('.//div[@class="btn  buy m-buy"]/a/@href')[0].extract()
            pic_url = item.xpath('.//div[@class="pic-img"]/a/img/@data-original')
            if len(pic_url) == 0:
                pic_url = item.xpath('.//div[@class="pic-img"]/a/img/@src')
            prod['pic_url'] = pic_url[0].extract().strip()
            prod['now_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            crawl_detail(prod)
            #crawl_shop_name(prod)
            save_prod(prod)
        except Exception as e:
            print e
            continue
    work(cat, start_url, page + 1)

if __name__ == "__main__":
    for cat, url in url_dict.items():
        work(cat, url, 1)
    conn.commit()
