# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from scrapy import Selector

with open('list.html') as html_file:
    html = html_file.read()
hxs = Selector(text=html)
a_list = hxs.xpath('//div[@class="all-city"]/dl/dd/a')
for a in a_list:
    url = a.xpath('./@href')[0].extract()
    city = a.xpath('./text()')[0].extract()
    print city + ' ' + url
