#-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import datetime

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
        if value == 'True':
            value = True 
        elif value == 'False':
            value = False
        if not value:
            value = None 
        elif key == 'cat' or key == 'display_name' or key == 'type' or key == 'b2c_source':
            value = value.decode('utf8')
        elif key == 'score' or key == 'crawl_priority':
            value = int(value)
        elif key == 'stat':
            value = int(value)
        elif key == 'xml_suffix' or key == 'filter_urls':
            value = value.split(',')
        elif key == 'xpath_file':
            value = 'html/' + value
        if value:
            start_url_info[key] = value
    if start_url_info.has_key('start_url'):
        start_url = start_url_info['start_url']
        start_url_info_dict[start_url] = start_url_info
        set_default_conf(start_url_info)
    return start_url_info_dict

# main function
def init_conf_db(conf_file_path):
    info_conf_table = Table('baseinfo', 'info_source')
    start_url_info_dict = load_conf(conf_file_path) 
    for start_url in start_url_info_dict:
        #import pdb
        #pdb.set_trace()
        if start_url_info_dict[start_url].has_key('domain_name'):
            if start_url.find('taobao') != -1 and start_url_info_dict[start_url]['display_name'] != u'淘宝特色':
                continue
            if start_url_info_dict[start_url].has_key('type') and start_url_info_dict[start_url]['type'] == u'商品':
                print 'Success insert conf data:' + start_url
                item = {}
                item['crawl_source'] = start_url_info_dict[start_url]['display_name']
                item['id'] = id = hashlib.md5(item['crawl_source']).hexdigest().upper()
                info_conf_table.save(item)
  
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'arg error'
        sys.exit(-1)
    conf_file = sys.argv[1]
    init_conf_db(conf_file)
