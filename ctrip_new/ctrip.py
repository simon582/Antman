#-*- coding:utf-8 -*-
import sys
import hashlib
import requests
import urllib2
import random
from scrapy import Selector
import pymongo
import json
from random import randint
import traceback
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    client = pymongo.MongoClient()
    hotel_table = client['ctrip']['hotel']
except Exception as e:
    print e
    print '[ERROR]Cannot connect MongoDB!'
    exit(-1)

def save(prod):
    hotel_table.save(prod)

def get_html_by_data(url, use_cookie=False, fake_ip=False):
    headers = {
        'Host': 'hotels.ctrip.com',
        'Referer': 'http://hotels.ctrip.com/hotel/beijing1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
    }
    if fake_ip:
        ip = "%s.%s.%s.%s" % (str(randint(0,255)), str(randint(0,255)), str(randint(0,255)), str(randint(0,255)))
        headers["X-Forwarded-For"] = ip
    r = requests.get(url, headers=headers)
    html = r.text
    with open('test.html','w') as test_file:
        print >> test_file, html
    return html

def print_list(name, l):
    print name + ' ',
    for elem in l:
        print elem + ' ',
    print ''

def download_pic(pic_name, pic_url):
    img_path = '/data/ctrip/img/'
    data = urllib2.urlopen(pic_url).read()
    f = file(img_path + pic_name, 'wb')
    f.write(data)
    f.close()

def crawl_pic(prod, hxs):
    pic_url_list = hxs.xpath('//div[@id="topPicList"]/div/div/@_src')
    pos = 1
    prod['pic'] = [] 
    for pic_url in pic_url_list:
        try:
            pic_url = pic_url.extract().strip()
            pic_name = prod['id'] + '_' + str(pos) + '.jpg'
            prod['pic'].append(pic_name)
            print 'Downloading pic: ' + pic_name + ' ......'
            download_pic(pic_name, pic_url)
            pos += 1
        except:
            continue

def crawl_price(prod, hxs):
    hotel_id = prod['website'].split('/')[4].split('.')[0]
    print 'hotel_id: ' + hotel_id
    price_url = "http://hotels.ctrip.com/Domestic/tool/AjaxHotelRoomListForDetail.aspx?psid=h5|267,h57|244&MasterHotelID=0&hotel="+hotel_id+"&EDM=F&roomId=&IncludeRoom=&city=1&showspothotel=T&supplier=&contrast=0&startDate=2015-05-21&depDate=2015-05-22&RequestTravelMoney=F&hsids=&IsJustConfirm=F&contyped=0&priceInfo=-1&equip=&filter=&productcode=&couponList="
    data = get_html_by_data(price_url, fake_ip=True)
    data = data.replace("\/","/").replace('\\"','"')
    html = data.split('"html":"')[1].split('","roomNum')[0]
    file = open('price.html','w')
    print >> file, html
    file.close()
    pri_hxs = Selector(text=html)
    prod['price'] = pri_hxs.xpath('//span[@class="price"]/text()')[0].extract()
    print 'price: ' + prod['price']
    img_title_list = pri_hxs.xpath('//img/@title')
    for img_title in img_title_list:
        room_name = img_title.extract()
        if room_name.find('海景') != -1:
            prod['seaView'] = True
        else:
            prod['seaView'] = False 

def crawl_gps(prod, hxs):
    prod['latitude'] = hxs.xpath('//meta[@itemprop="latitude"]/@content')[0].extract()
    print 'latitude: ' + prod['latitude']
    prod['longitude'] = hxs.xpath('//meta[@itemprop="longitude"]/@content')[0].extract()
    print 'longitude: ' + prod['longitude']

def crawl_prod(prod):
    hxs = Selector(text=get_html_by_data(prod['website'],use_cookie=True,fake_ip=True))
    try:
        nameEn = hxs.xpath('//h2[@class="en_n"]/text()')
        if len(nameEn) > 0:
            prod['nameEn'] = nameEn[0].extract()
            print 'nameEn: ' + prod['nameEn']
        prod['grade'] = hxs.xpath('//div[@class="grade"]/span/@title')[0].extract()
        print 'grade: ' + prod['grade']
        info_text = hxs.xpath('//div[@class="htl_room_txt text_3l "]/p/text()')[0].extract().strip()
        if info_text.find('开业') != -1:
            prod['openingTime'] = info_text.split('开业')[0]
            print 'openingTime: ' + prod['openingTime']
        tel_text = hxs.xpath('//div[@class="htl_room_txt text_3l "]/p/span[@id="J_realContact"]/@data-real')[0].extract().strip().split(u'\xa0')[0].strip()
        for part in tel_text.split(' '):
            if part.find('电话') != -1:
                prod['phone'] = part.replace('电话','')
                print 'phone: ' + prod['phone']
            if part.find('传真') != -1:
                prod['fax'] = part.replace('传真','')
                print 'fax: ' + prod['fax']
            if part.find('手机') != -1:
                prod['mphone'] = part.replace('手机','')
                print 'mphone: ' + prod['mphone']
        tr_list = hxs.xpath('//div[@class="htl_info_table "]/table/tr')
        for tr in tr_list:
            key = tr.xpath('./th/text()')[0].extract()
            if key == "网络设施":
                tlist = tr.xpath('.//ul/li/text()|.//ul/li/span/text()')
                prod['internet'] = ""
                for t in tlist:
                    prod['internet'] += t.extract().strip()
                print 'internet: ' + prod['internet']
            elif key == "停车场":
                tlist = tr.xpath('.//ul/li/text()|.//ul/li/span/text()')
                prod['carPark'] = ""
                for t in tlist:
                    prod['carPark'] += t.extract().strip()
                print 'carPark: ' + prod['carPark']
        prod['facilities'] = []
        for li in hxs.xpath('.//div[@class="facilities_hide"]/ul/li'):
            fac = ""
            for text in li.xpath('./span/text()|./text()'):
                fac += text.extract().strip()
            prod['facilities'].append(fac)
        print_list('facilities',prod['facilities'])
        prod['creditCard'] = []
        for span in hxs.xpath('.//span[@data-role="jmp"]/text()'):
            credit_card = span.extract().strip()
            prod['creditCard'].append(credit_card)
        print_list('creditCard',prod['creditCard'])
        prod['introduction'] = ""
        for text in hxs.xpath('.//span[@itemprop="description"]/text()'):
            prod['introduction'] += text.extract().strip()
        print 'introduction: ' + prod['introduction']
        for tr in hxs.xpath('//div[@class="htl_info_table"]/table/tbody/tr'):
            key = tr.xpath('./th/text()')[0].extract()
            if key == "餐饮":
                prod['dinner'] = []
                for name in tr.xpath('./td/ul/li/text()'):
                    prod['dinner'].append(name.extract())
                print_list('dinner', prod['dinner'])
            if key == "娱乐":
                prod['pastimeHealth'] = []
                for name in tr.xpath('./td/ul/li/text()'):
                    prod['pastimeHealth'].append(name.extract())
                print_list('pastimeHealth', prod['pastimeHealth'])
        prod['commentNum'] = hxs.xpath('//span[@itemprop="reviewCount"]/text()')[0].extract().split('位')[0]
        print 'commentNum: ' + prod['commentNum']
        prod['scoreNum'] = hxs.xpath('//a[@class="commnet_score"]/@title')[0].extract()
        print 'scoreNum: ' + prod['scoreNum']
        crawl_gps(prod, hxs)
        crawl_price(prod, hxs)
        crawl_pic(prod, hxs)
    except Exception as e:
        print e

def crawl_list(title, list_url):
    hxs = Selector(text=get_html_by_data(list_url, use_cookie=True, fake_ip=True))
    item_list = hxs.xpath('//div[@id="hotel_list"]/div[@class="searchresult_list"]')
    for item in item_list:
        try:
            url = item.xpath('.//h2[@class="searchresult_name"]/a/@href')[0].extract()
            print 'content_url: ' + url
            prod = {}
            prod['website'] = 'http://hotels.ctrip.com' + url
            print 'website: ' + prod['website']
            prod['id'] = hashlib.md5(prod['website']).hexdigest().upper()
            print 'id: ' + prod['id']
            #prod['title'] = title
            prod['name'] = item.xpath('.//h2[@class="searchresult_name"]/a/@title')[0].extract()
            print 'name: ' + prod['name']
            prod['address'] = item.xpath('.//p[@class="searchresult_htladdress"]/text()')[0].extract().split('【')[0].strip()
            print 'address: ' + prod['address']
            prod['businessDistrict'] = item.xpath('.//p[@class="searchresult_htladdress"]/a/text()')[0].extract()
            print 'businessDistrict: ' + prod['businessDistrict']
            crawl_prod(prod)
            #import pdb;pdb.set_trace()
            save(prod)
        except Exception as e:
            print e
            print 'skip item'

def work(start_url, start_page):
    retry_times = 0
    while retry_times < 3:
        try:
            hxs = Selector(text=get_html_by_data(start_url,use_cookie=True,fake_ip=True))
            max_page = hxs.xpath('//div[@class="c_page_list layoutfix"]/a[@rel="nofollow"]/text()')[0].extract().strip()
            title = hxs.xpath('//h1/text()')[0].extract().strip()
            break
        except Exception as e:
            print e
            retry_times += 1
    if retry_times == 3:
        print 'Retry 3 times! No max_page or title info.'
        return False
    print title + ' ' + max_page + ' pages'
    for page in range(start_page, int(max_page) + 1):
        try:
            crawl_list(title, start_url + '/p' + str(page))
        except Exception as e:
            print e
            print traceback.format_exc()
            print 'skip page ' + start_url + '/p' + str(page)
    return True

if __name__ == '__main__':
    start_page = int(sys.argv[1])
    first = True
    for id in range(28, 2001):
        try:
            print 'current id: ' + str(id)
            if first:
                res = work("http://hotels.ctrip.com/hotel/qingdao" + str(id), start_page)
                first = False
            else:
                res = work("http://hotels.ctrip.com/hotel/qingdao" + str(id), 1)
            if not res:
                print 'skip city id ' + str(id)
        except Exception as e:
            print e
            print 'skip city id ' + str(id)
