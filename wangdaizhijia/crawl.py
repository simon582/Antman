# coding:utf-8
import requests
import pdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from scrapy import Selector

def get_html_by_data(url, use_cookie=False):
    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36',
        'Referer':'http://yuqing.wangdaizhijia.com/index.php?app=wangdairen&mod=Index&act=search&k=%E4%BA%BA%E4%BA%BA%E8%B4%B7&nk=&pt=90&tr=2&sr=1&t=1&m=4%2C3%2C2&f=2&s=desc&p=1',
        'Host':'yuqing.wangdaizhijia.com'
    }
    if use_cookie:
        with open('cookie','r') as cookie_file:
            cookies = cookie_file.read().strip()
            headers['Cookie'] = cookies
    r = requests.get(url, headers=headers)
    with open('test.html','w') as test_file:
        print >> test_file, r.text
    return r.text
    
def crawl_detail(prod):
    hxs = Selector(text=get_html_by_data(prod['content_url'],use_cookie=True))
    prod['content'] = ""
    if prod['type'].find(u'QQ群') != -1:
        for dl in hxs.xpath('.//div[@class="msgBox"]/dl'):
            qq = dl.xpath('./dt/span/text()')[0].extract().strip()
            content = dl.xpath('./dd/text()')[0].extract().strip().replace('\n','').replace('\r','').replace(' ','')
            prod['content'] += qq + content + '/'
    elif prod['type'].find(u'论坛') != -1:
        prod['content'] += hxs.xpath('//div[@class="bd"]/dl/dd/text()')[0].extract().strip().replace('\n','').replace('\r','').replace(' ','')
    else:
        for text in hxs.xpath('.//div[@class="detailsFont"]/text()'):
            prod['content'] += text.extract().strip().replace('\n','').replace('\r','').replace(' ','')
    print 'content:' + prod['content']

def add(key, prod):
    if prod.has_key(key):
        return prod[key].replace('\r','').replace('\n','').replace(',',' ') + ','
    return ','

def write_csv(prod):
    file = open('result/' + prod['keyword'] + '.csv', 'a')
    resline = ""
    resline += add('keyword', prod)
    resline += add('type', prod)
    resline += add('time', prod)
    resline += add('title', prod)
    resline += add('content_url', prod)
    resline += add('content', prod)
    print >> file, resline

def work(keyword, page):
    # test luntan
    #list_url = "http://yuqing.wangdaizhijia.com/index.php?app=wangdairen&mod=Index&act=search&k=%E4%BA%BA%E4%BA%BA%E8%B4%B7&nk=&pt=90&tr=2&sr=1&t=1&m=3&f=2&s=desc"
    # test weibo
    #list_url = "http://yuqing.wangdaizhijia.com/index.php?app=wangdairen&mod=Index&act=search&k=%E4%BA%BA%E4%BA%BA%E8%B4%B7&nk=&pt=90&tr=2&sr=1&t=1&m=2&f=2&s=desc"
    list_url = "http://yuqing.wangdaizhijia.com/index.php?app=wangdairen&mod=Index&act=search&k=" + keyword + "&nk=&pt=90&tr=2&sr=1&t=1&m=4%2C3%2C2&f=2&s=desc&p=" + str(page)
    print 'list_url: ' + list_url
    html = get_html_by_data(list_url, use_cookie=True)
    if html.find(u'暂无搜索结果') != -1:
        print 'Out of page:' + str(page)
        return False
    hxs = Selector(text=html)
    li_list = hxs.xpath('//div[@class="bd"]/ul[@class="list"]/li')
    if len(li_list) == 0:
        print 'Out of page:' + str(page)
        return False
    for li in li_list:
        try:
            prod = {}
            prod['keyword'] = keyword
            print 'keyword:' + prod['keyword']
            prod['title'] = ""
            for part in li.xpath('.//h2[@class="title"]/a/text()|.//h2[@class="title"]/a/font/text()'):
                prod['title'] += part.extract().strip()
            print 'title:' + prod['title']
            prod['content_url'] = li.xpath('.//h2[@class="title"]/a/@href')[0].extract()
            print 'content_url:' + prod['content_url']
            prod['type'] = li.xpath('.//h2[@class="title"]/span[@class="from"]/text()')[0].extract().replace('[','').replace(']','')
            print 'type:' + prod['type']
            prod['time'] = li.xpath('.//p[@class="time"]/text()')[0].extract()
            print 'time:' + prod['time']
            crawl_detail(prod)
            write_csv(prod)
            #pdb.set_trace()    
        except Exception as e:
            print e
            continue
    return True

if __name__ == "__main__":
    with open('keyword_list_new','r') as keyword_file:
        for keyword in keyword_file.readlines():
            page = 1
            while True:
                if work(keyword.strip(), page):
                    page += 1
                else:
                    break
