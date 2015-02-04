#-*- coding:utf-8 -*-
import sys
import urllib2
import urllib
import cookielib
import json
import zlib
from StringIO import StringIO
from scrapy import Selector
reload(sys)
sys.setdefaultencoding('utf-8')
import io

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

def get_html_by_gzip(url):
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    opener = urllib2.build_opener()
    response = opener.open(request)
    html = response.read()
    gzipped = response.headers.get('Content-Encoding')
    if gzipped:
        html = zlib.decompress(html, 16+zlib.MAX_WBITS)
    else:
        html = ''
    html = html.decode('gbk', 'ignore')
    html_file = open('test.html','w')
    print >>html_file, html
    response.close()
    return html

def crawl_text(hxs, prod):
    p_list = hxs.xpath('//div[@id="articleContent"]/p|//div[@id="artibody"]/p|//div[@class="moduleParagraph"]/p')
    for p in p_list:
        text_list = p.xpath('.//text()') 
        for text in text_list:
           prod['content'] += text.extract().strip()
    try:
        next_url = hxs.xpath('//span[@class="pagebox_next"]/a/@href')[0].extract()
        crawl_text(Selector(text=get_html_by_gzip(next_url)), prod)
    except:
        return

def crawl_prod(url, prod):
    print url
    hxs = Selector(text=get_html_by_gzip(url))
    source_list = hxs.xpath('//span[@id="media_name"]/a/text()|//span[@id="media_name"]/text()')
    source = ""
    for s in source_list:
        source += s.extract()
    prod['source'] = source.strip()
    prod['content'] = ''
    crawl_text(hxs, prod)
    write_csv(prod)

def add(key, prod):
    if key in prod:
        return prod[key].replace('&nbsp','').replace(',',' ').replace('\n','').replace('\r','').replace('\t','').strip() + ','
    return ','

def write_csv(prod):
    file = open('result.csv','a')
    resline = "门户网站,新浪行业新闻,"
    resline += add('label',prod)
    resline += add('url',prod)
    resline += add('title',prod)
    resline += add('date',prod)
    resline += add('source',prod)
    resline += add('author',prod)
    resline += add('content',prod)
    print >> file, resline.encode('utf-8')

def work(start_url):
    text = get_html_by_data(start_url)
    eq = text.find('(')
    if eq != -1:
        text = text[:len(text)-1]
        source_dict = json.loads(text[eq+1:])
        for news in source_dict['data']:
            prod = {}
            prod['author'] = news['author']
            prod['label'] = news['label_name']
            prod['title'] = news['title']
            prod['url'] = news['url']
            prod['date'] = news['createtime']
            crawl_prod(news['url'], prod)

if __name__ == '__main__':
    label = sys.argv[1]
    url_dict = {}
    with open('start_urls','r') as url_file:
        lines = url_file.readlines()
    for line in lines:
        res = line.strip().split(' ')
        url_dict[res[0]] = {"max_page":int(res[1]), "start_url":res[2]}
    for page in range(1, url_dict[label]['max_page']):
        print label + ' ' + str(page)
        try:
            work(url_dict[label]['start_url'].replace('[page]',str(page)))
        except Exception as e:
            print e
    print 'Crawl Finished!'
