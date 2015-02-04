#=============================================================================
#coding:utf-8
#
#Author: SimonS
#
#Email: 
#
#Last modified: 2015-01-21 17:06
#
#Filename: baidu.py
#
#Description: 抓取百度关键词结果数
#
#=============================================================================

import sys
import re
import urllib
import urllib2
import cookielib

'''
    根据url获取相应的html源码
    使用了urllib2开源库实现
'''
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
    return html

'''
    对关键词keyword进行抓取分析
'''
def crawl(keyword):
    print 'Current crawling ' + keyword + ' ...',
    # 拼接百度搜索url，并使用了精确搜索
    url = 'http://www.baidu.com/s?wd=%22' + keyword + '%22'
    html = get_html_by_data(url)
    # 解析html，提取结果数
    cnt = html.split('百度为您找到相关结果约')[1].split('个')[0].replace(',','')
    print cnt
    return cnt


'''
    脚本入口
'''
if __name__ == "__main__":
    # 判断输入参数个数是否合法
    if len(sys.argv) != 2:
        print 'python baidu.py input_file_name'
        exit(-1)
    input_file_name = sys.argv[1]
    # 打开要操作的文件
    with open(input_file_name, 'r') as input_file, open('result.txt', 'w') as output_file:
        lines = input_file.readlines()
        for line in lines:
            try:
                keyword = line.strip()
                cnt = crawl(keyword)
                print >> output_file, keyword + "|" + cnt
            except Exception as e:
                print e
                print 'Cannot crawl keyword: ' + keyword
    
