#-*- coding:utf-8 -*-
import urllib2, urllib, cookielib
import pdb
import sys
import json
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
    download = False
    try_times = 0
    f = opener.open(req)
    html = f.read()
    html_file = open('test.html','w')
    print >> html_file, html
    f.close()
    download = True
    return html

def handle_article(uid, req_url):
    print 'START ARTICLES'
    json_str = get_html_by_data(req_url)
    file_name = uid + '_article.txt'
    file = open(file_name, 'w')
    article_list = json.loads(json_str)['data']['rows']
    for prod in article_list:
        art_id = prod['art_id']
        item_id = prod['item']
        url = 'http://bbs.tianya.cn/post-'+item_id+'-'+art_id+'-1.shtml'
        print url
        print >> file, url.encode('utf-8')
    print 'END ARTICLES'

def handle_replay(uid, req_url):
    print 'START REPLAYS'
    json_str = get_html_by_data(req_url)
    file_name = uid + '_replay.txt'
    file = open(file_name, 'w')
    article_list = json.loads(json_str)['data']['rows']
    for prod in article_list:
        item_id = prod['item']
        id = prod['art_id']
        replay_id = prod['reply_id']
        url = 'http://bbs.tianya.cn/go_reply_position.jsp?item='+item_id+'&id='+id+'&rid='+replay_id
        print url
        print >> file, url.encode('utf-8')
    print 'END REPLAYS'

def crawl(uid):
    article_url = 'http://www.tianya.cn/api/tw?method=userinfo.ice.getUserTotalArticleList&params.userId=' + uid + '&params.pageSize=100'
    replay_url = 'http://www.tianya.cn/api/tw?method=userinfo.ice.getUserTotalReplyList&params.userId=' + uid + '&params.pageSize=100'
    handle_article(uid, article_url) 
    handle_replay(uid, replay_url)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'python tianya.py uid'
        exit(-1)
    uid = sys.argv[1]
    crawl(uid)
