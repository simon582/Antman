# -*- coding:utf-8 -*-
from scrapy import Selector
import requests
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')

def get_html(url):
    headers = {
        'Cookie':'SINAGLOBAL=122.234.53.25_1426834714.990139; UOR=www.baidu.com,tech.sina.com.cn,; vjuids=546c27b5f.14c4cd397d1.0.fb3fc6ed; SGUID=1427218078185_46674594; U_TRS1=00000097.f94552b8.55119e96.40ac3f73; __utma=269849203.1945322866.1438845694.1438845694.1438845694.1; __utmz=269849203.1438845694.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; sso_info=v02m6alo5qztbOalrWvm6OUuIyimbWalpC9jJOks4yTkLeNo5C3jZDAwA==; lxlrtst=1442902043_o; Apache=125.120.151.105_1445011387.616913; U_TRS2=00000027.332b75fa.5624b006.9a139626; SUS=SID-1931476475-1445244934-GZ-f230o-be7ebbac115ef55c338d3cd62cfe1d66; SUE=es%3D29084c200f716749388a46a850e404c3%26ev%3Dv1%26es2%3Deb587f660962c56efb21e72c70f06498%26rs0%3Dm22RSxFrQuKI%252FIpc3if1AW9hY75JipxiGdR1cP%252FogzfjCFYHJgFj4kDcRslx9jCxqygST9YIndjCbHNPCGUCg24VCFT%252ByA9qY9ZMboCjhZ3hIo%252B3AwHcJquR4lMag9jd79uFZUrB6NABniuHLgVNmh9ZGlc%252FkIWrDFMaANWlJuQ%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1445244934%26et%3D1445331334%26d%3D40c3%26i%3D1d66%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D0%26st%3D0%26lt%3D7%26uid%3D1931476475%26user%3Dsimon582%2540163.com%26ag%3D4%26name%3Dsimon582%2540163.com%26nick%3Dsimon582%26sex%3D%26ps%3D0%26email%3D%26dob%3D%26ln%3D%26os%3D%26fmp%3D%26lcp%3D2012-11-08%252022%253A23%253A09; SUB=_2A257IMBWDeTxGedH6FMV9yjIzDmIHXVYV7aerDV_PUNbvtBeLUnfkW9oR4kYwhGRjy3WyeUUW7W5aysuyA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWFveKz-X1is5I8yZRIYxMf; ALF=1476780934; SessionID=ld1a6vi1ivdl58ki3krcqbqvq4; SINABLOGNUINFO=1931476475.731ffdfb.0; ULV=1445268824041:19:1:1:125.120.151.105_1445011387.616913:1442903990262; vjlast=1445268830; lxlrttp=1445220644; USRMDE16=usrmdinst_18; mYSeArcH=%u8682%u8681%u91D1%u670D%20%u4FB5%u6743%7CsEaRchHIS%7C%u8682%u8681%u91D1%u670D%u4FB5%u6743%7CsEaRchHIS%7C%u8682%u8681%u91D1%u670D%20%u88C1%u5458%7CsEaRchHIS%7C%u8682%u8681%u91D1%u670D%u88C1%u5458%7CsEaRchHIS%7C%u8682%u8681%u91D1%u670D%u8FDD%u6CD5%7CsEaRchHIS%7C%u8682%u8681%u91D1%u670D%20%u8FDD%u6CD5%7CsEaRchHIS%7C%u79EF%u6728%u76D2%u5B50%u8FDD%u6CD5%7CsEaRchHIS%7C%u79EF%u6728%u76D2%u5B50%20%u8FDD%u6CD5%7CsEaRchHIS%7C%u79EF%u6728%u76D2%u5B50%20%u8DD1%u8DEF%7CsEaRchHIS%7C%u79EF%u6728%u76D2%u5B50%u8DD1%u8DEF%7CsEaRchHIS%7C%u79EF%u6728%u76D2%u5B50%u8D1F%u9762%7CsEaRchHIS%7C%u6316%u8D22%u7F51%u8DD1%u8DEF%7CsEaRchHIS%7C%u6316%u8D22%u7F51%20%u8DD1%u8DEF%7CsEaRchHIS%7C%u6316%u8D22%u7F51%20%u8BC9%u8BBC%7CsEaRchHIS%7C%u6316%u8D22%u7F51%u8BC9%u8BBC%7CsEaRchHIS%7C%u6316%u8D22%u7F51%u66DD%u5149%7CsEaRchHIS%7C%u5C0F%u7C73%u79D1%u6280%u66DD%u5149%7CsEaRchHIS%7C%u5C0F%u7C73%u79D1%u6280%u8FDD%u6CD5%7CsEaRchHIS%7C%u5C0F%u7C73%u79D1%u6280%u8D1F%u9762%7CsEaRchHIS%7C%u4EBA%u4EBA%u8D37%u8DD1%u8DEF%7CsEaRchHIS%7C%u4EBA%u4EBA%u8D37%u5904%u7F5A%7CsEaRchHIS%7C%u4EBA%u4EBA%u8D37%u7092%u4F5C%7CsEaRchHIS%7C%u4EBA%u4EBA%u8D37%20%u7092%u4F5C%7CsEaRchHIS%7C%u4EBA%u4EBA%u8D37%u6B3A%u8BC8%7CsEaRchHIS%7C%u4EBA%u4EBA%u8D37%u4FB5%u6743%7CsEaRchHIS%7C%u4EBA%u4EBA%u8D37%20%u4FB5%u6743%7CsEaRchHIS%7C%u4EBA%u4EBA%u8D37',
        'Host':'search.sina.com.cn',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
    }
    while True:
        r = requests.get(url, headers=headers)
        html = r.text
        if len(html) == 0:
            time.sleep(1)
            continue
        if html.find('The server returned an invalid or incomplete response') != -1:
            time.sleep(1)
            continue
        with open('debug.html','w') as debug_file:
            print >> debug_file, html.encode('utf-8')
        return html

def get_max_page(company_name, keyword):
    search_url = "http://search.sina.com.cn/?q=" + company_name + "+" + keyword + "&range=all&c=news&sort=time"
    hxs = Selector(text=get_html(search_url))
    text = hxs.xpath('//div[@class="l_v2"]/text()')[0].extract()
    news_cnt = int(text.split('新闻')[1].split('篇')[0])
    if news_cnt % 10 != 0:
        max_page = news_cnt / 10 + 1
    else:
        max_page = news_cnt / 10
    print 'company_name: ' + company_name + ' keyword: ' + keyword + ' max_page: ' + str(max_page)
    return max_page

def crawl_part(news):
    info = {}
    print '=============================='
    info['title'] = ""
    title_parts = news.xpath('.//h2/a/text()|.//h2/a/span/text()')
    for part in title_parts:
        info['title'] += part.extract()
    print info['title']
    info['url'] = news.xpath('.//h2/a/@href')[0].extract()
    source_text = news.xpath('.//span[@class="fgray_time"]/text()')[0].extract()
    info['source'] = source_text.split(' ')[0]
    info['date'] = source_text.split(' ')[1] + ' ' + source_text.split(' ')[2]
    print info['source']
    print info['date']
    print info['url']
    return info

def add(key, prod):
    if key in prod:
        return prod[key].replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def write_csv(com_name, keyword, info):
    outline = com_name + ',' + keyword + ','
    outline += add('source', info)
    outline += add('title', info)
    outline += add('date', info)
    outline += add('url', info)
    with open('data/' + com_name + '.csv','a') as res_file:
        print >> res_file, outline    

def work(company_name, keyword, dst_page):
    print 'company_name: ' + company_name + ' keyword: ' + keyword + ' dst_page: ' + str(dst_page)
    search_url = "http://search.sina.com.cn/?q=" + company_name + "+" + keyword + "&range=all&c=news&sort=time&page=" + str(dst_page)
    hxs = Selector(text=get_html(search_url))

    news_list = hxs.xpath('//div[@class="box-result clearfix"]')
    print 'news_cnt: ' + str(len(news_list))
    for news in news_list:
        try:
            info = crawl_part(news)
            write_csv(company_name, keyword, info)
            #import pdb;pdb.set_trace()
        except Exception as e:
            print 'Occur an error:'
            print e
            continue
 
if __name__ == "__main__":
    com_list = []
    key_list = []
    with open('../cnf/companies.cnf') as com_file, open('../cnf/keywords.cnf') as key_file:
        for line in com_file.readlines():
            com_list.append(line.strip())
        for line in key_file.readlines():
            key_list.append(line.strip())
    for com in com_list:
        for key in key_list:
            max_page = get_max_page(com, key)
            for i in range(1, max_page + 1):
                work(com, key, i)
