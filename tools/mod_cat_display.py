#! /usr/bin/env python
# -*- coding: utf-8 -*-
#encoding=utf8
__author__ = 'shaoxinqi@maimiaotech.com'
import sys
import os
import datetime

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


start_url_info_dict = {}
start_urls_info_ord = []
new_cat_display_dict = {}
new_cat_display_urls = []

def read_new_cat_display(filePath):
    file = open(filePath)
    while True:
        buffer = file.readline()
        if not buffer:
            break
        ret = buffer.split(',')
        if len(ret) < 6:
            continue
        first_cat = ret[2]
        if first_cat == '商品' and int(ret[0]) < 500:
            continue
        cat = ret[3]
        crawl_source = ret[4]
        url = ret[5]
        if url and utils.has_prefix(url, 'http://'):
            new_cat_display_urls.append(url)
            new_cat_display = {}
            new_cat_display['cat'] = cat
            new_cat_display['display_name'] = crawl_source
            if len(ret) > 7:
                new_cat_display['score'] = ret[7]
            if len(ret) > 10 and ret[9] != 'none':
                new_cat_display['reserve_days'] = ret[9]
            new_cat_display_dict[url] = new_cat_display
    #print new_cat_display_dict     

def read_old_cat_display(filePath):
    file = open(filePath)
    start_url_info = {}
    start_url_info_ord = []
    while True:
        buffer = file.readline()
        if not buffer:
            break
        if buffer[0] == '#' and buffer[1] == '-':
            continue
        if utils.has_prefix(buffer, '#start_url') and start_url_info.has_key('start_url'):
            start_url = start_url_info['start_url']
            start_url_info_dict[start_url] = start_url_info
            start_urls_info_ord.append(start_url_info_ord)
            start_url_info = {}
            start_url_info_ord = []
            start_url_info['comment'] = True
        if utils.has_prefix(buffer, 'start_url') and start_url_info.has_key('start_url'):
            start_url = start_url_info['start_url']
            start_url_info_dict[start_url] = start_url_info
            start_urls_info_ord.append(start_url_info_ord)
            start_url_info = {}
            start_url_info_ord = []
        content = buffer.strip()
        equal = content.find('=')
        if equal == -1:
            continue
        key = content[:equal]
        value = content[equal + 1:]
        if key != None:
            if key == '#start_url':
                key = 'start_url'
            start_url_info[key] = value
            if key == 'start_url':
                start_url_info_ord.append(value)
            else:
                duplicate = False
                for item in start_url_info_ord:
                    if item == key:
                        duplicate = True
                        break
                if not duplicate:
                    start_url_info_ord.append(key)
    if start_url_info.has_key('start_url'):
        start_url = start_url_info['start_url']
        start_url_info_dict[start_url] = start_url_info
        start_urls_info_ord.append(start_url_info_ord)

def output_old2new(start_url):
    if start_url_info_dict[start_url].has_key('cat') and start_url_info_dict[start_url].has_key('display_name'):
        print start_url_info_dict[start_url]['display_name'] + ' ' + new_cat_display_dict[start_url]['display_name'] + ' ' + start_url_info_dict[start_url]['cat'] + ' ' + new_cat_display_dict[start_url]['cat']
     
def update_conf():
    for start_url in new_cat_display_urls:
        if start_url_info_dict.has_key(start_url):
            #output_old2new(start_url)
            if start_url_info_dict[start_url].has_key('cat'):
                start_url_info_dict[start_url]['cat'] = new_cat_display_dict[start_url]['cat']
            if start_url_info_dict[start_url].has_key('#cat'):
                start_url_info_dict[start_url]['#cat'] = new_cat_display_dict[start_url]['cat']

            if start_url_info_dict[start_url].has_key('display_name'):
                start_url_info_dict[start_url]['display_name'] = new_cat_display_dict[start_url]['display_name']
            if start_url_info_dict[start_url].has_key('#display_name'):
                start_url_info_dict[start_url]['#display_name'] = new_cat_display_dict[start_url]['display_name']
            
            if new_cat_display_dict[start_url].has_key('reserve_days'):
                if not (start_url_info_dict[start_url].has_key('reserve_days') or start_url_info_dict[start_url].has_key('#reserve_days')):
                    for start_url_info_ord in start_urls_info_ord:
                        if start_url_info_ord[0] == start_url:
                            if start_url_info_dict.has_key('comment'):
                                start_url_info_ord.append('#reserve_days')
                            else:
                                start_url_info_ord.append('reserve_days')
                if not start_url_info_dict.has_key('comment'):
                    start_url_info_dict[start_url]['reserve_days'] = new_cat_display_dict[start_url]['reserve_days']
                else:
                    start_url_info_dict[start_url]['#reserve_days'] = new_cat_display_dict[start_url]['reserve_days']
                
                    
                    
        else:
            start_url_info = {}
            start_url_info['#cat'] = new_cat_display_dict[start_url]['cat']
            start_url_info['#display_name'] = new_cat_display_dict[start_url]['display_name']
            start_url_info['#main_xpath'] = ''
            start_url_info['#xpath_file'] = ''
            start_url_info['#domain_name'] = ''
            start_url_info['comment'] = True
            if new_cat_display_dict[start_url].has_key('score'):
                start_url_info['#score'] = new_cat_display_dict[start_url]['score']
            else:
                start_url_info['#score'] = ''
            if new_cat_display_dict[start_url].has_key('reserve_days'):
                start_url_info['#reserve_days'] = new_cat_display_dict[start_url]['reserve_days']
            
            start_url_info_ord = [start_url, '#main_xpath', '#display_name', '#cat', '#xpath_file', '#score', '#reserve_days', '#domain_name']
            start_url_info_dict[start_url] = start_url_info
            start_urls_info_ord.append(start_url_info_ord)            
 
def output():
    #print start_urls_info_ord    
    for start_url_info_ord in start_urls_info_ord:
        print ('#-------------------------')
        start_url = start_url_info_ord[0]
        start_url_info = start_url_info_dict[start_url]
        if start_url_info:
            if start_url_info.has_key('comment') and start_url_info['comment']:
                print ('#start_url=' + start_url)
            else:
                print ('start_url=' + start_url)
            for each_key in start_url_info_ord[1:]:
                if start_url_info.has_key(each_key):
                    print (each_key + "=" + start_url_info[each_key])
                else:
                    print (each_key + "=")
read_new_cat_display("cat2_source.csv")
read_old_cat_display("../uniform/start_url_info_new.conf")
update_conf()
output()
