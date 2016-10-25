# -*- coding:utf-8 -*-

import urllib2, urllib, cookielib
from scrapy import Selector
import pdb
import sys
import time
import datetime
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
    download = True
    return html

def get_english_title(ori_title):
    res = ori_title.split(' ')
    english_title = ''
    for i in xrange(len(res)):
        if res[i][0].isalpha():
            for j in xrange(i, len(res)):
                english_title += res[j]
            break
    return english_title

key_list = [
    'title',
    'url',
    'chinese',
    'english',
    'year',
    'mainpic',
    'director',
    'writer',
    'actor',
    'type',
    'website',
    'country',
    'language',
    'publish_time',
    'length',
    'nickname',
    'imdb',
    'score',
    'rating_people',
    '5star_rate',
    '4star_rate',
    '3star_rate',
    '2star_rate',
    '1star_rate',
    'better',
    'intro',
    'prevue_cnt',
    'pic_cnt',
    'recommend',
    'short_cmt_cnt',
    'tags',
    'doulie',
    'viewed',
    'want',
    'ask_cnt',
    'review_cnt',
    'dis_cnt',
]

def add(key, prod):
    if prod.has_key(key):
        return prod[key].replace('\r','').replace('\n','').replace(',',' ') + ','
    return ','

def write_csv(prod):
    global key_list
    with open('result.csv', 'a') as res_file:
        resline = ''
        for key in key_list:
            resline += add(key, prod)
        print >> res_file, resline.encode('utf-8')

def work(prod):
    print 'detail_url:' + prod['url']
    hxs = Selector(text=get_html_by_data(prod['url'], use_cookie=True))
    prod['chinese'] = prod['title']
    ori_title = hxs.xpath('//div[@id="content"]/h1/span/text()')[0].extract()
    print 'ori_title:' + ori_title
    prod['english'] = get_english_title(ori_title)
    print 'chinese:' + prod['chinese']
    print 'english:' + prod['english']
    prod['year'] = hxs.xpath('//span[@class="year"]/text()')[0].extract()
    prod['year'] = prod['year'].replace('(','').replace(')','')
    print 'year:' + prod['year']
    try:
        prod['mainpic'] = hxs.xpath('//div[@id="mainpic"]/a/img/@src')[0].extract()
        prod['mainpic'] = 'https://img3.doubanio.com/view/photo/photo/public/' + prod['mainpic'].split('/')[-1]
        print 'mainpic:' + prod['mainpic']
    except:
        pass
   
    text_list = []
    for text in hxs.xpath('//div[@id="info"]/text()|//div[@id="info"]/span/text()|//div[@id="info"]/span/span/a/text()|//div[@id="info"]/span/span/text()|//div[@id="info"]/a/@href'):
        text = text.extract().strip()
        if text == ":" or text == "" or text == "/":
            continue
        if text in ("导演", "编剧", "主演"):
            text += ":"
        text_list.append(text)
    print 'source_text_list:' + '||'.join(text_list)

    i = 0
    while i < len(text_list):
        t = text_list[i]
        if t.find(':') != -1:
            key = t[:-1]
            print 'key:' + key
            val_list = []
            j = i + 1
            while j < len(text_list):
                tt = text_list[j]
                if tt.find(':') != -1 and tt.find('http') == -1:
                    break
                val_list.append(tt)
                j += 1
            i = j
            val = '/'.join(val_list)
            print 'val:' + val
         
        if key.find('导演') != -1:
            prod['director'] = val
        elif key.find('编剧') != -1:
            prod['writer'] = val
        elif key.find('主演') != -1:
            prod['actor'] = val
        elif key.find('类型') != -1:
            prod['type'] = val
        elif key.find('官方网站') != -1:
            prod['website'] = val
        elif key.find('制片国家') != -1:
            prod['country'] = val
        elif key.find('语言') != -1:
            prod['language'] = val
        elif key.find('上映日期') != -1:
            prod['publish_time'] = val
        elif key.find('片长') != -1:
            prod['length'] = val
        elif key.find('又名') != -1:
            prod['nickname'] = val
        elif key.find('IMDb') != -1:
            prod['imdb'] = val        

    try:
        prod['score'] = hxs.xpath('//strong[@class="ll rating_num"]/text()')[0].extract()
        print 'score:' + prod['score']
    except:
        pass
    
    try:
        prod['rating_people'] = hxs.xpath('//a[@class="rating_people"]/span/text()')[0].extract()
        print 'rating_people:' + prod['rating_people']
    except:
        pass

    i = 5
    for text in hxs.xpath('//span[@class="rating_per"]/text()'):
        text = text.extract()
        key = str(i) + 'star_rate'
        prod[key] = text
        print key + ':' + text
        i -= 1

    try:
        text_list = []
        for text in hxs.xpath('//div[@class="rating_betterthan"]/a/text()'):
            text_list.append(text.extract())
        prod['better'] = '/'.join(text_list)
        print 'better:' + prod['better']
    except:
        pass

    try:
        prod['intro'] = hxs.xpath('//span[@property="v:summary"]/text()')[0].extract().strip()
        print 'intro:' + prod['intro']
    except:
        pass

    try:
        for text in hxs.xpath('//div[@id="related-pic"]/h2/span/a/text()'):
            text = text.extract()
            if text.find('预告片') != -1:
                prod['prevue_cnt'] = text.split('片')[1]
                print 'prevue_cnt:' + prod['prevue_cnt']
            if text.find('图片') != -1 and text.find('添加') == -1:
                prod['pic_cnt'] = text.split('片')[1]
                print 'pic_cnt:' + prod['pic_cnt']
            if text.find('全部') != -1:
                prod['pic_cnt'] = text.split('全部')[1]
                print 'pic_cnt:' + prod['pic_cnt']
    except:
        pass

    try:
        recommend_list = []
        for text in hxs.xpath('//div[@class="recommendations-bd"]/dl/dd/a/text()'):
            recommend_list.append(text.extract().strip())
        prod['recommend'] = '/'.join(recommend_list)
        print 'recommend:' + prod['recommend']
    except:
        pass

    try:
        text = hxs.xpath('//div[@id="comments-section"]/div/h2/span/a/text()')[0].extract()
        prod['short_cmt_cnt'] = text.split(' ')[1]
        print 'short_cmt_cnt:' + prod['short_cmt_cnt']
    except:
        pass

    try:
        tag_list = []
        for tag in hxs.xpath('//div[@class="tags-body"]/a/text()'):
            tag_list.append(tag.extract())
        prod['tags'] = '/'.join(tag_list)
        print 'tags:' + prod['tags']
    except:
        pass

    try:
        get_doulie_length(prod)
    except:
        pass

    try:
        prod['viewed'] = hxs.xpath('//div[@class="subject-others-interests-ft"]/a[1]/text()')[0].extract().split('人')[0]
        print 'viewed:' + prod['viewed']
    except:
        pass

    try:
        prod['want'] = hxs.xpath('//div[@class="subject-others-interests-ft"]/a[2]/text()')[0].extract().split('人')[0]
        print 'want:' + prod['want']
    except:
        pass

    try:
        prod['ask_cnt'] = hxs.xpath('//div[@id="askmatrix"]/div/h2/span/a/text()')[0].extract().split('全部')[1].split('个')[0]
        print 'ask_cnt:' + prod['ask_cnt']
    except:
        pass

    try:
        prod['review_cnt'] = hxs.xpath('//div[@id="review_section"]/div/h2/span/a/text()')[0].extract().split('全部')[1].split('个')[0]
        print 'review_cnt:' + prod['review_cnt']
    except:
        pass

    try:
        prod['dis_cnt'] = hxs.xpath('//h2[@class="discussion_link"]/a/text()')[0].extract().split('全部')[1].split('条')[0]
        print 'dis_cnt:' + prod['dis_cnt']
    except:
        pass
    write_csv(prod)
    #import pdb;pdb.set_trace()

def get_doulie_length(prod):
    doulie_url = prod['url'] + 'doulists'
    hxs = Selector(text=get_html_by_data(doulie_url, use_cookie=True))
    prod['doulie'] = hxs.xpath('//div[@class="paginator"]/span[@class="count"]/text()')[0].extract().split('共')[1].split('个')[0]
    print 'doulie:' + prod['doulie']

with open('patch2.csv', 'r') as movie_file:
    lines = movie_file.readlines()
    total_cnt = len(lines)
    cur = 0
    for line in lines:
        cur += 1
        res = line.strip().split(';')
        prod = {}
        prod['title'] = res[0]
        #prod['year'] = res[1]
        prod['url'] = res[1]
        try:
            work(prod)
            print str(cur) + '/' + str(total_cnt) + ' ' + prod['title'] + ' ' + prod['url']
            resline = '%s,%s,%s' % (prod['title'], prod['year'], prod['url'])
            print >> url_file, resline.encode('utf-8')
        except:
            with open('spider_err.csv', 'a') as err_file:
                print >> err_file, line.strip().encode('utf-8')
