#coding:utf-8
from scrapy import Selector
import requests

start_url_list = [
    'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/1-10000',
    'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/10001-20000',
    'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/20001-30000',
    'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/30001-40000',
    'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/40001-50000',
    'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/50001-60000',
    'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/60001-70000',
    'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/70001-80000',
    'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/80001-90000',
    'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/90001-100000',
]

def get_html(url):
    headers = {
        'Connection':'keep-alive',
        'Cookie':'GeoIP=CN:Hangzhou:30.2936:120.1614:v4; uls-previous-languages=%5B%22en%22%5D; mediaWiki.user.sessionId=pFaQO4fo2Dh1lRtk4UNwoesTKOdXe4Xp',
        'Host':'en.wiktionary.org',
        'Referer':'http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36',
    }
    res = requests.get(url,headers=headers)
    return res.text

def work():
    file = open('word_dict.txt','a')
    for start_url in start_url_list:
        hxs = Selector(text=get_html(start_url))
        words = hxs.xpath('//p/a/text()')
        for word in words:
            print word.extract()
            print >> file, word.extract().encode('utf-8')

if __name__ == "__main__":
    work()
