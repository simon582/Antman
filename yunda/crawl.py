#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import json
import hashlib
import Image
import re
import pymongo
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
    f = opener.open(req, timeout=5)
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
    print >> file, resline.encode('utf-8')

def crawl_details(start_url):
    print start_url
    html = get_html_by_data(start_url, use_cookie=False)
    prod = {}
    prod['kd'] = "yunda"
    json_str = html.split('yd_shi=')[1].split('</script>')[0]
    if json_str == "{}":
        return
    json_str = json_str.replace('&gt;','').replace('&lt;','').replace('&quot;','').replace('&nbsp;','').replace('&amp;','').replace('\'','')
    #print json_str
    ori = json.loads(json_str)
    if 'psfw' in ori:
        ori['psfw'] = re.sub(r"[a-zA-Z_]+|[/\<>:;,.-=+`~!@#$%^&*()_+{}|:\"?']+", '',ori['psfw'])
        ori['psfw'] = re.sub(r" +", " ", ori['psfw'])
        ori['psfw'] = ori['psfw'].replace('\n','').replace('\r','').replace('\t','').replace('　','').replace(' ','').replace(u'【更新时间：--】','')
        prod['deliver'] = ori['psfw']

    if 'mc' in ori:
        prod['name'] = ori['mc']
    if 'city' in ori:
        prod['region'] = ori['city']
    if 'dz' in ori:
        prod['addr'] = ori['dz']
    if 'fzr' in ori:
        prod['linkman'] = ori['fzr']
    if 'xddh' in ori:
        prod['phone1'] = ori['xddh']
    if 'cxdh' in ori:
        prod['phone2'] = ori['cxdh']
    if 'tsdh' in ori:
        prod['ts_tel'] = ori['tsdh']
    
    if "region" in prod:
        res = prod['region'].split(',')
        if len(res) >= 2:
            prod['province'] = prod['city'] = res[0]
            if res[0].find('省') != -1 or res[1].find('市') != -1:
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
    save_csv(prod)

if __name__ == '__main__':
    part = int(sys.argv[1])
    sid = int(sys.argv[2]) + 1
    for id in range(sid, (part+1) * 100000):
        start_url = "http://www.yundaex.com/fuwuwangdian_data.php?id=" + str(id)
        try:
            crawl_details(start_url)
        except Exception as e:
            print e
            print 'skip: ' + start_url
            continue
    print 'Crawl Finished!'
