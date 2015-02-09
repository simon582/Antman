#-*- coding:utf-8 -*-
import sys
import os
import time

curr_path = os.path.dirname(__file__)
sys.path.append(os.path.join(curr_path,'../../'))
sys.path.append(os.path.join(curr_path,'../comm_lib'))
from table import Table
import utils
import datetime
import hashlib
import logging
import logging.config
import traceback

rm_filter = [
    u'全国',
    u'包邮',
    u'天猫',
    u'京东商城',
    u'送',
    u'ml',
    u'ML',
    u'原价',
    u'现价',
    u'元',
    u'9.9包邮'
]

def filter(tstr):
    for item in rm_filter:
        tstr = tstr.replace(item, '')
    return tstr

# calculate the edit distance between two string
def get_edit_distance(str1, str2):
    str1 = filter(str1)
    str2 = filter(str2)
    m = len(str1)
    n = len(str2)
    f = []
    for i in range(m+1):
        ff = []
        for j in range(n+1):
            ff.append(0)
        f.append(ff)
    for i in range(m+1):
        f[i][0] = i
    for j in range(n+1):
        f[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            if str1[i-1] == str2[j-1]:
                temp = 0
            else:
                temp = 1
            f[i][j] = min(f[i-1][j] + 1, min(f[i][j-1] + 1, f[i-1][j-1] + temp))
    #print f
    #print ('len1: ' + str(m) + ' title1: ' + str1 + ' len2: ' + str(n) + ' title2:' + str2 + ' dis:' + str(f[m][n]))
    return f[m][n]

# main function
def get_similar_and_remove(table, similar_degree, realmod, tot_block, cur_block):
    print 'get_similar_and_remove start'
    not_access_table = Table('content_db', 'not_access')
    cursor = table.scan(condition={"type":1})
    similar_count = 0
    goods_num = 0
    realmod_num = 0
    goods_list = []
    print 'add items from db...'
    for item in cursor:
        goods_list.append(item)
        goods_num += 1
    print 'find ' + str(goods_num) + ' goods, calculating similar titles ......'
    for i in range(goods_num):
        for j in range(i+1, goods_num):
            if goods_list[i].has_key('title') and goods_list[j].has_key('title'):
                if len(goods_list[i]['title']) > len(goods_list[j]['title']):
                    long_item = goods_list[i]
                    short_item = goods_list[j]
                else:
                    long_item = goods_list[j]
                    short_item = goods_list[i]
                dis = get_edit_distance(long_item['title'], short_item['title'])
                full_dis = len(long_item['title'])
                deg = (1.0 - float(dis) / float(full_dis)) * 100
                if deg >= similar_degree:
                    similar_count += 1
                    print 'dis ' + str(dis) + ' full_dis ' + str(full_dis) + ' deg %.2f'%deg + ' similar_deg ' + str(similar_degree)
                    print ('id ' + short_item['id'].encode('utf8') + ' ' + short_item['title'].encode('utf8') +' similar to: ' + long_item['title'].encode('utf8'))
                    if realmod == 1:
                        not_access_table.save({'id': short_item['id'], 'not_access_reason': 'title similar with others'})
                        table.remove(short_item)
                        realmod_num += 1
    print 'total ' + str(goods_num) + ' realmod ' + str(realmod_num) + ' similar ' + str(similar_count) + ' similar_degree ' + str(similar_degree)
                
if __name__ == '__main__':
    if len(sys.argv) != 5 and len(sys.argv) != 7:
        print 'arg error args: ' + str(len(sys.argv))
        print 'realmod similar_degree db_name table_name [tot_block cur_block]'
        sys.exit(-1)
    realmod = int(sys.argv[1])
    similar_degree = int(sys.argv[2])
    db_name = sys.argv[3]
    table_name = sys.argv[4]
    tot_block = 1
    cur_block = 1
    if len(sys.argv) == 7:
        tot_block = int(sys.argv[5])
        cur_block = int(sys.argv[6])
    if realmod != 0 and realmod != 1:
        print 'realmod error, input 0 or 1'
        sys.exit(-1)
    if similar_degree < 0 or similar_degree > 100:
        print 'similar_degree error, range [0, 100]'
        sys.exit(-1)
    #start_time = time.time()
    get_similar_and_remove(Table(db_name, table_name), similar_degree, realmod, tot_block, cur_block)
    #use_time = time.time() - start_time
    #print 'run time: ' + str(use_time/60) + ' minutes'

