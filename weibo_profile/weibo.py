# -*- coding: utf-8 -*-

'''
    新浪微博粉丝数和关注数抓取
    输入参数：
    微博用户id
'''

import urllib2
import urllib
import cookielib
import sys 

reload(sys)
# 设置默认编码用于正确显示中文
sys.setdefaultencoding('utf-8')

'''
    get_html_by_data函数
    输入url和是否使用cookie标记use_cookie，返回该url对应的html源码
    返回源码会存储在debug.html文件中，用于分析网页结构，可以将其注释
'''
def get_html_by_data(url, use_cookie=False):
    # 初始化
    data = {}
    post_data = urllib.urlencode(data)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    req = urllib2.Request(url)
    if use_cookie:
        # 读取cookie
        cookie_file = open('cookie')
        cookie = cookie_file.read()
        req.add_header("Cookie", cookie)
    # 添加user_agent头以模拟浏览器防止反抓取
    req.add_header("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36")
    # 发送post请求
    f = opener.open(req)
    # 获取html
    html = f.read()
    # 写入debug.html文件中
    html_file = open('debug.html','w')
    print >> html_file, html
    f.close()
    return html


'''
    work函数
    获取微博的关注和粉丝数，并写入结果文件中
    如果无法获取，请更新cookie并检查url是否正确
'''
def work(url):
    try:
        html = get_html_by_data(url, use_cookie=True)
        # 利用split函数解析html
        follow_cnt = html.split('关注[')[1].split(']')[0]
        print u'关注数: ' + str(follow_cnt)
        fans_cnt = html.split('粉丝[')[1].split(']')[0]
        print u'粉丝数: ' + str(fans_cnt)

        # 输出结果到文件result.txt
        res_file = open('result.txt','w')
        res_str = url + '\n' + 'follow_cnt: ' + str(follow_cnt) + '\n' + 'fans_cnt: ' + str(fans_cnt)
        print >> res_file, res_str.encode('utf-8')
    except Exception as e:
        print e
        print u'无法获取该页面上的关注和粉丝数！请更新cookie并检查输入id是否正确！'
        exit(-1) 


'''
    脚本程序入口
'''
if __name__ == '__main__':
    # 输入参数不合法
    if len(sys.argv) != 2:
        print 'python weibo.py weibo_id'
        exit(-1)
    # 获取输入id
    id = sys.argv[1]
    url = 'http://weibo.cn/u/' + id
    work(url)
    
