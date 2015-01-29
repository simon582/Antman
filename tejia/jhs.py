#encoding:utf-8
import MySQLdb
from scrapy import Selector
import sys
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

cookie_str = "cna=hQX7DCfN/RYCAXrqMLzkbMDV; miid=5151629387633752399; cainiao_abtest=0; thw=cn; __utma=6906807.988028570.1421561235.1421561235.1421815316.2; __utmz=6906807.1421561235.1.1.utmcsr=taobao.com|utmccn=(referral)|utmcmd=referral|utmcct=/market/caipiao/afc-2015.php; jc=hangzhou; ucn=center; lzstat_uv=2924804164818009635|862081@3492151@1208344@3416547@2341454@1723936@2738597@3443933@3525281@2043323@3045821@3192183@2945527@2948565@2801066@2945730@2798379; lzstat_ss=3754936660_6_1422442742_2043323|3966022142_6_1422442742_3045821|1988132601_1_1422377686_3192183|711923675_1_1422441813_2738597|2350850463_0_1422442602_2945527|119119529_6_1422442742_2948565|3691024572_3_1422442740_2801066|3061905166_1_1422442742_2945730|35137919_1_1422442742_2798379; ali_ab=220.191.87.156.1417080661532.0; _tb_token_=f3354fb347e47; cainiao_abtest[9/1]=1; v=0; uc3=nk2=EFed8r5gJsy%2F&id2=VASr1cFqhwie&vt3=F8dATkOKa7P%2Fmi8yCYI%3D&lg2=UIHiLt3xD8xYTw%3D%3D; existShop=MTQyMjUwMjk1OA%3D%3D; unt=simon0571%26center; lgc=simon0571; tracknick=simon0571; mt=np=&ci=22_1&cyk=0_0; _cc_=Vq8l%2BKCLiw%3D%3D; tg=0; cookie2=1c2b05cb445a2d9bcee3fab944e1334e; t=1b46d230211b1b3231588e059e17eca8; uc1=cookie14=UoW1FqnRqr%2F8fg%3D%3D; isg=49A91BFAFE92E6D13504A2B8034FF43B; bid=3"

url_dict = {}
with open('jhs.conf','r') as conf_file:
    lines = conf_file.readlines()
    for line in lines:
        res = line.split(',')
        if len(res) == 2 and res[1] != "":
            print res[0]
            print res[1].strip()
            url_dict[res[0]] = res[1].strip()

try:
    conn = MySQLdb.connect(host="localhost",user="root",passwd="123456",db="tejia",charset="utf8")
    cursor = conn.cursor()
except Exception as e:
    print e
    print 'Cannot connect MySQL!'
    exit(-1)

def get_html_by_data(url, use_cookie=False):
    headers = {
        "Connection":"keep-alive",
        "Host":"ju.taobao.com",
        "Referer":"http://ju.taobao.com/jusp/nvzhuangpindao/tp.htm",
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
    sql = "insert into jhs(id,title,act_price,ori_price,remind,item_url,left_time,pic_url,now_time,cat,sold) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    params = (id,prod['title'],prod['act_price'],prod['ori_price'],prod['remind'],prod['item_url'],prod['left_time'],prod['pic_url'],prod['now_time'],prod['cat'],prod['sold'])
    n = cursor.execute(sql, params)
    print 'mysql insert result: ' + str(n)

def work(cat, pinyin, floor_index):
    print cat + ' ' + pinyin + ' index:' + str(floor_index)
    json_str = get_html_by_data('http://ju.taobao.com/json/jusp/ajaxGetTpFloor.json?_ksTS=1422516597946_562&callback=jsonpfloor&urlKey='+pinyin+'&pc=true&floorIndex='+str(floor_index))
    if json_str.find('IndexOutOfBoundsException') != -1:
        print 'floor_index out of bounds.' + cat + ' crawl finished'
        return
    json_str = json_str.split('jsonpfloor(')[1]
    json_str = json_str[0:len(json_str)-1]
    total_dict = json.loads(json_str)
    if 'itemList' in total_dict:
        for item in total_dict['itemList']:
            try:
                prod = {}
                prod['cat'] = cat
                prod['title'] = item["name"]["title"]
                prod['act_price'] = item["price"]["actPrice"]
                prod['ori_price'] = item["price"]["origPrice"]
                prod['remind'] = str(item["remind"]["remindNum"])
                prod['sold'] = str(item["remind"]["soldCount"])
                prod['item_url'] = item["baseinfo"]["itemUrl"]
                prod['left_time'] = item["baseinfo"]["leftTime"]
                prod['pic_url'] = item["baseinfo"]["picUrl"]
                prod['now_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
                save_prod(prod)
            except Exception as e:
                print e
                continue
    work(cat, pinyin, floor_index + 1)

if __name__ == "__main__":
    for cat, pinyin in url_dict.items():
        work(cat, pinyin, 1)
    conn.commit()
