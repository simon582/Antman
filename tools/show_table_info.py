#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import hashlib
__author__ = 'luoyan@maimiaotech.com'
curr_path = os.path.dirname(__file__)
sys.path.append(os.path.join(curr_path,'../../'))
sys.path.append(os.path.join(curr_path,'../../spider/comm_lib'))
import utils
from table import Table
import datetime
import hashlib
import logging
import logging.config
import traceback
import socket
import time
def set_default_conf(start_url_info):
    if not start_url_info.has_key('type'):
        start_url_info['type'] = u'其它'

def load_conf(file_name):
    start_url_info_dict = {}
    file = open(file_name)
    start_url_info = {}
    while True:
        buffer = file.readline()
        if not buffer:
            break
        if buffer[0] == '#':
            continue
        if utils.has_prefix(buffer, 'start_url') and start_url_info.has_key('start_url'):
            start_url = start_url_info['start_url']
            set_default_conf(start_url_info)
            start_url_info_dict[start_url] = start_url_info
            start_url_info = {}

        content = buffer.strip()
        equal = content.find('=')
        if equal == -1:
            continue
        key = content[:equal]
        value = content[equal + 1:]
        #log.msg(('key = ' + key + ' value = ' + value), level = log.DEBUG)
        if value.strip() == '':
            value = None
        elif value == 'True':
            value = True
        elif value == 'False':
            value = False
        elif key == 'cat' or key == 'display_name' or key == 'type' or key == 'b2c_source' or key == 'crawl_location':
            value = value.decode('utf8')
        elif key == 'score' or key == 'crawl_priority' or key == 'reserve_days':
            value = int(value)
        elif key == 'stat':
            value = int(value)
        elif key == 'xml_suffix' or key == 'filter_urls' or key == 'crawl_text_xpath_tags' or key == 'content_next_page_url_match':
            value = value.split(',')
        elif key == 'xpath_file':
            value = 'html/' + value
        if value != None:
            start_url_info[key] = value
    if start_url_info.has_key('start_url'):
        start_url = start_url_info['start_url']
        start_url_info_dict[start_url] = start_url_info
        set_default_conf(start_url_info)
    return start_url_info_dict

def get_uniform_site_num(table, start_urls_file, conf):
    file = open(start_urls_file, 'r')
    start_url_info_dict = load_conf(conf)
    d = {}
    list = []
    while True:
        buffer = file.readline()
        if not buffer:
            break
        start_url = buffer.strip()
        if start_url_info_dict.has_key(start_url):
            crawl_source = start_url_info_dict[start_url]['display_name']
            count = table.scan(condition={"crawl_source":crawl_source}).count()
            #print 'crawl_source ' + crawl_source.encode('utf8') + ' ' + str(count)
            key = hashlib.md5(start_url).hexdigest().upper()
            d[key] = {'start_url' : start_url, 'crawl_source' : crawl_source, 'count' : count}
            list.append(key)
    return d, list

def get_weibo_site_num(table, crawl_source_file):
    file = open(crawl_source_file, 'r')
    d = {}
    list = []
    while True:
        buffer = file.readline()
        if not buffer:
            break
        crawl_source = buffer.strip().decode('utf8')
        count = table.scan(condition={"crawl_source":crawl_source}).count()
        #print 'crawl_source ' + crawl_source.encode('utf8') + ' ' + str(count)
        key = hashlib.md5(crawl_source.encode('utf8')).hexdigest().upper()
        start_url = 'http://weibo.cn/search/mblog?hideSearchFrame=&keyword='
        d[key] = {'start_url' : start_url, 'crawl_source' : crawl_source, 'count' : count}
        list.append(key)
    return d, list

def get_cat_num(table, cat_file):
    file = open(cat_file, 'r')
    d = {}
    list = []
    while True:
        buffer = file.readline()
        if not buffer:
            break
        buffer_array = buffer.strip().split('\t')
        cat_id = buffer_array[0]
        cat_name = buffer_array[1]
        count = table.scan(condition={"cat":cat_id}).count()
        key = cat_id
        d[key] = {'count': count, 'cat_id' : cat_id, 'cat_name' : cat_name}
        list.append(key)
    return d, list

def get_db_num():
    d = {}
    l = []
    for item in [
            ['content_db', 'info', {}, None],
            ['content_db', 'info_temp', {}, None],
            ['content_db', 'info_weibo_temp', {}, None],
            ['content_db', 'info_old', {}, None],
            ['content_index', 'info', {}, None],
            ['content_db', 'info', {"stat":1}, 'online'],
            ['content_db', 'info', {"stat":0}, 'offline'],
            ]:
        db_name = item[0]
        table_name = item[1]
        condition = item[2]
        name = item[3]
        table = Table(db_name, table_name)
        count = table.scan(condition=condition).count()
        if name:
            key = name
        else:
            key = db_name + '/' + table_name
        d[key] = {'num' : count, 'num1' : count, 'num2': 0}
        l.append(key)
    return d,l

def get_cur_info(start_urls_file, conf, crawl_source_file, cat_file):
    table = Table('content_db', 'info')
    old_table = Table('content_db', 'info_old')
    d_uniform_new, l_uniform_new = get_uniform_site_num(table, start_urls_file, conf)
    d_uniform_old, l_uniform_old = get_uniform_site_num(old_table, start_urls_file, conf)
    d_weibo_new, l_weibo_new = get_weibo_site_num(table, crawl_source_file)
    d_weibo_old, l_weibo_old = get_weibo_site_num(old_table, crawl_source_file)
    d_cat_new, l_cat_new = get_cat_num(table, cat_file)
    d_cat_old, l_cat_old = get_cat_num(old_table, cat_file)
    d_uniform, l_uniform = join(d_uniform_new, l_uniform_new, d_uniform_old, l_uniform_old)
    d_weibo, l_weibo = join(d_weibo_new, l_weibo_new, d_weibo_old, l_weibo_old)
    d_cat, l_cat = join(d_cat_new, l_cat_new, d_cat_old, l_cat_old)
    d_total, l_total = get_total_dict([[d_uniform, l_uniform, 'uniform_site'], [d_weibo, l_weibo, 'weibo_site'], [d_cat, l_cat, 'cat']])
    d_db, l_db = get_db_num()
    return [[d_db, l_db], [d_total, l_total], [d_uniform, l_uniform], [d_weibo, l_weibo], [d_cat, l_cat]]

def get_yesterday_info(yesterday_file):
    d_db = {}
    l_db = []
    d_total = {}
    l_total = []
    d_uniform = {}
    l_uniform = []
    d_weibo = {}
    l_weibo = []
    d_cat = {}
    l_cat = []
    if yesterday_file and os.path.exists(yesterday_file):
        file = open(yesterday_file, 'r')
        while True:
            buffer = file.readline()
            if not buffer:
                break
            buffer_array = buffer.strip().split('\t')
            info = {}
            key_name = ''
            for i in xrange(len(buffer_array)):
                if i == 1:
                    info['num'] = int(buffer_array[i])
                elif buffer_array[i] == 'diff':
                    info['diff'] = int(buffer_array[i+1])
                elif buffer_array[i] == 'cur':
                    info['num1'] = int(buffer_array[i+1])
                elif buffer_array[i] == 'old':
                    info['num2'] = int(buffer_array[i+1])
            key_name = buffer_array[9]
            key_attr_name = buffer_array[8]
            if buffer_array[0] == 'db_info':
                key = key_name
                info[key_attr_name] = key_name
                d_db[key] = info
                l_db.append(key)
            elif buffer_array[0] == 'total':
                key = key_name
                info[key_attr_name] = key_name
                d_total[key] = info
                l_total.append(key)
            elif buffer_array[0] == 'uniform_num':
                #start_url
                key_name = buffer_array[11]
                key = hashlib.md5(key_name).hexdigest().upper()
                info[key_attr_name] = key_name.decode('utf8')
                info['start_url'] = buffer_array[11]
                d_uniform[key] = info
                l_uniform.append(key)
            elif buffer_array[0] == 'weibo_num':
                key = hashlib.md5(key_name).hexdigest().upper()
                info[key_attr_name] = key_name.decode('utf8')
                info['start_url'] = buffer_array[11]
                d_weibo[key] = info
                l_weibo.append(key)
            elif buffer_array[0] == 'cat_num':
                key = buffer_array[11]
                info['cat_name'] = key_name
                d_cat[key] = info
                l_cat.append(key)
    return [
            [d_db, l_db],
            [d_total, l_total],
            [d_uniform, l_uniform],
            [d_weibo, l_weibo],
            [d_cat, l_cat],
            ]

def get_diff(dict1, list1, dict2, list2):
    d = {}
    l = []
    for key in list1:
        num1 = dict1[key]['num']
        if dict2.has_key(key):
            num2 = dict2[key]['num']
        else:
            num2 = 0
        diff = num1 - num2
        d[key] = dict1[key]
        d[key]['diff'] = diff
        l.append(key)

    for key in list2:
        num2 = dict2[key]['num']
        if dict1.has_key(key):
            continue
        num1 = 0
        diff = num2 - num1
        d[key] = dict2[key]
        d[key]['diff'] = diff
        l.append(key)

    return d, l

def get_total_num(start_urls_file, conf, crawl_source_file, cat_file, yesterday_file):
    d_yesterday_list = get_yesterday_info(yesterday_file)
    d_today_list = get_cur_info(start_urls_file, conf, crawl_source_file, cat_file)
    d_list = []
    for i in xrange(len(d_yesterday_list)):
        d, l = get_diff(d_today_list[i][0], d_today_list[i][1], d_yesterday_list[i][0], d_yesterday_list[i][1])
        if i >=2 and i <=4:
            l2 = sorted(l, key=lambda k:d[k]['num'],reverse=True)
            l = l2
        d_list.append([d, l])
    count = 0
    for pair in d_list:
        d = pair[0]
        l = pair[1]
        #print 'count ' + str(count)
        for key in l:
            diff = d[key]['diff']
            if diff > 0:
                diff_str = '+' + str(diff)
            else:
                diff_str = str(diff)
            if count == 0:
                print 'db_info\t%d\tdiff\t%s\tcur\t%d\told\t%d\tname\t%s'%(d[key]['num'], diff_str, d[key]['num1'], d[key]['num2'], key)
            elif count == 1:
                print 'total\t%d\tdiff\t%s\tcur\t%d\told\t%d\tname\t%s'%(d[key]['num'], diff_str, d[key]['num1'], d[key]['num2'], key)
            elif count == 2:
                print 'uniform_num\t%d\tdiff\t%s\tcur\t%d\told\t%d\tcrawl_source\t%s\tstart_url\t%s'%(d[key]['num'], diff_str, d[key]['num1'], d[key]['num2'], d[key]['crawl_source'].encode('utf8'), d[key]['start_url'])
            elif count == 3:
                print 'weibo_num\t%d\tdiff\t%s\tcur\t%d\told\t%d\tcrawl_source\t%s\tstart_url\t%s'%(d[key]['num'], diff_str, d[key]['num1'], d[key]['num2'], d[key]['crawl_source'].encode('utf8'), d[key]['start_url'])
            elif count == 4:
                print 'cat_num\t%d\tdiff\t%s\tcur\t%d\told\t%d\tcat\t%s\tcat_id\t%s'%(d[key]['num'], diff_str, d[key]['num1'], d[key]['num2'], d[key]['cat_name'], d[key]['cat_id'])
        count += 1

def join(dict1, list1, dict2, list2):
    d = {}
    list = []
    for key in list1:
        num1 = dict1[key]['count']
        if dict2.has_key(key):
            num2 = dict2[key]['count']
        else:
            num2 = 0
        num = num1 + num2
        d[key] = dict1[key]
        d[key]['num'] = num
        d[key]['num1'] = num1
        d[key]['num2'] = num2
        list.append(key)

    for key in list2:
        if dict1.has_key(key):
            continue
        num1 = 0
        num2 = dict2[key]['count']
        num = num1 + num2
        d[key] = dict2[key]
        d[key]['num'] = num
        d[key]['num1'] = num1
        d[key]['num2'] = num2
        list.append(key)

    return d, list

def get_total(dict, list, name):
    valid = 0
    count = 0
    sum = 0
    for key in list:
        num = dict[key]['num']
        if num > 0:
            valid += 1
        count += 1
        sum += num

    print "%s total %d valid %d sum %d"%(name, count, valid, sum)

def get_total_dict(total_list):
    dict = {}
    list = []
    for item in total_list:
        d = item[0]
        l = item[1]
        name = item[2]
        valid = 0
        count = 0
        sum = 0
        sum1 = 0
        sum2 = 0
        for key in l:
            num = d[key]['num']
            if num > 0:
                valid += 1
            count += 1
            sum += num
            sum1 += d[key]['num1']
            sum2 += d[key]['num2']
        dict[name + '_url'] = {'valid' : valid, 'count' : count, 'num' : sum, 'num1' : sum1, 'num2' : sum2}
        list.append(name + '_url')
        dict[name + '_total'] = {'num' : count, 'num1' : count, 'num2' : 0}
        list.append(name + '_total')
        dict[name + '_valid'] = {'num' : valid, 'num1' : valid, 'num2' : 0}
        list.append(name + '_valid')
    return dict, list

    print "%s total %d valid %d sum %d"%(name, count, valid, sum)
def show_help(argv0):
    print argv0 + " show_site_num start_urls_file cat_file yesterday_file"
    
if __name__ == "__main__":
    if len(sys.argv) != 5 and len(sys.argv) != 4:
        show_help(sys.argv[0])
        sys.exit(-1)
    if sys.argv[1] == 'show_site_num':
        if len(sys.argv) == 5:
            yesterday_file_name = sys.argv[4]
        elif len(sys.argv) == 4:
            yesterday_file_name = None
        #show_site_num(sys.argv[2], conf = '../uniform/start_url_info_new.conf')
        get_total_num(sys.argv[2], conf = '../uniform/start_url_info_new.conf', crawl_source_file = 'weibo_crawl_source', cat_file=sys.argv[3], yesterday_file=yesterday_file_name)
    else:
        sys.exit(-1)
