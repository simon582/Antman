#! /usr/bin/env python
# -*- coding: utf-8 -*-
#encoding=utf8
__author__ = 'shaoxinqi@maimiaotech.com'


import sys
import os
import datetime
curr_path = os.path.dirname(__file__)
curr_file_path = os.path.abspath(__file__)
curr_abs_path = curr_file_path[0:curr_file_path.rfind("/")]
sys.path.append(os.path.join(curr_path,'../../'))
sys.path.append(os.path.join(curr_path,'../../spider/comm_lib'))
import utils
from table import Table
from shutil import copy

goods_table = Table('goods_db', 'info')
info_table = Table('content_db', 'info')
dest_dir = '~/appimg/'

def copy_img(filepath):
    try:
        copy(filepath, dest_dir)
        print 'move ' + filepath + ' to ' + dest_dir + ' successfully.'
    except:
        print 'move ' + filepath + ' failed.'

def trans_img(table):
    cursor = table.scan()
    cnt = 0
    for item in cursor:
        cnt += 1
        print 'cnt ' + str(cnt)
        if item.has_key('desc_img'):
            copy_img(curr_abs_path + '/' + item['desc_img'][3:])
        if item.has_key('text'):
            for elem in item['text']:
                if elem[0] == '0':
                    copy_img(curr_abs_path + '/' + elem[1][3:])

trans_img(goods_table)
trans_img(info_table)
