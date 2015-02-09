#! /usr/bin/env python
#coding=utf-8
import decimal
import re
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import XmlXPathSelector
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import urllib
import urllib2
import time
import hashlib 
import md5 
import ast
from scrapy import log
import traceback
from datetime import datetime
from datetime import timedelta
import os
import simplejson as json
import Image
import logging
import logging.config
import socket
import pymongo
import gc
import sys
from readability.readability import Document
#import bs4
#from bs4 import BeautifulSoup
from BeautifulSoup import BeautifulSoup
import copy
import re
import lxml.html.soupparser as soupparser
import lxml.etree as etree
logger = logging.getLogger(__name__)

UNKNOWN_NUM = -1
UNLIMITED_NUM = 0
NOT_BEGIN = 1
BEGIN = 2
END = 3
RESIZE_SUCCESS = 1
RESIZE_FAIL_SMALL = -1
RESIZE_FAIL_TRANS = -2
#APP_KEY = '21065688'
#SECRET_CODE = '74aecdce10af604343e942a324641891'
#APP_KEY = '12651461'
#SECRET_CODE = '80a15051c411f9ca52d664ebde46a9da'
APP_KEY='21569590'
SECRET_CODE = '2505da58f14cae10cbe9d2e651f2dbe4'
STAT_NEW=0
STAT_USE=1
STAT_WAIT_ONLINE=2
STAT_DELETE=3
TYPE_GOODS=1
TYPE_WEIBO=2
TYPE_NEWS=3
TYPE_OTHER=4
class OpenTaobao:
    def __init__(self,app_key,sercet_code):
        self.app_key = app_key
        self.sercet_code = sercet_code
    def get_time(self):
        t = time.localtime()
        return time.strftime('%Y-%m-%d %X', t)
    def get_sign(self,params):
        params['format'] = 'json' 
        params.update({'app_key':self.app_key,'timestamp':self.get_time(),'v':'2.0'})
        src = self.sercet_code + ''.join(["%s%s" % (k, v) for k, v in sorted(params.iteritems())])
        return md5.new(src).hexdigest().upper()
    def get_result(self,params):
        params['sign'] = self.get_sign(params)
        form_data = urllib.urlencode(params)
        #return urllib2.urlopen('http://gw.api.taobao.com/router/rest', form_data).read()
        return urllib2.urlopen('http://223.5.20.253:8002/router/rest', form_data).read()
    
def get_pic_url(num_iid):
    try:
        op = OpenTaobao(APP_KEY, SECRET_CODE)
        params = {
            'method':'taobao.item.get',
            'fields':'pic_url',
            'num_iid':str(num_iid),
        }
        dict_str = op.get_result(params)
        ret_dict = ast.literal_eval(dict_str)
        if ret_dict.has_key('item_get_response'):
            if ret_dict['item_get_response'].has_key('item'):
                if ret_dict['item_get_response']['item'].has_key('pic_url'):
                    return ret_dict['item_get_response']["item"]["pic_url"].replace('\/', '/')
        print 'error [' +dict_str+']'
        return None
    except:
        exstr = traceback.format_exc()
        log.msg('failed to get_pic_url ' + exstr, level = log.WARNING)
        return None

def get_pic_url_and_detail_url(num_iid):
    try:
        op = OpenTaobao(APP_KEY, SECRET_CODE)
        params = {
            'method':'taobao.item.get',
            'fields':'pic_url, detail_url',
            'num_iid':str(num_iid),
        }
        dict_str = op.get_result(params)
        ret_dict = ast.literal_eval(dict_str)
        return ret_dict['item_get_response']["item"]["pic_url"].replace('\/', '/'),  ret_dict['item_get_response']["item"]["detail_url"].replace('\/', '/')
    except:
        exstr = traceback.format_exc()
        log.msg('failed to get_pic_and_detail_url ' + exstr, level = log.WARNING)
        return None, None


def get_taobao_item_info(num_iid):
    try:
        op = OpenTaobao(APP_KEY, SECRET_CODE)
        params = {
            'method':'taobao.item.get',
            'fields':'pic_url, detail_url, post_fee, express_fee, ems_fee, freight_payer, cid',
            'num_iid':str(num_iid),
        }
        dict_str = op.get_result(params)
        ret_dict = ast.literal_eval(dict_str)
        if ret_dict['item_get_response']["item"]["post_fee"] == '0.00' or ret_dict['item_get_response']["item"]["express_fee"] == '0.00' or ret_dict['item_get_response']["item"]["freight_payer"] == 'seller':
            baoyou = True
        else:
            baoyou = False
        log.msg('post_fee ' + str(ret_dict['item_get_response']["item"]["post_fee"]) + ' express_fee ' + str(ret_dict['item_get_response']["item"]["express_fee"]) + ' ems_fee ' + str(ret_dict['item_get_response']["item"]["ems_fee"]) + ' freight_payer ' + str(ret_dict['item_get_response']["item"]["freight_payer"]) + ' baoyou ' + str(baoyou), level = log.DEBUG)
        return ret_dict['item_get_response']["item"]["pic_url"].replace('\/', '/'),  ret_dict['item_get_response']["item"]["detail_url"].replace('\/', '/'), baoyou, ret_dict['item_get_response']["item"]["cid"]
    except:
        exstr = traceback.format_exc()
        log.msg('failed to get_pic_and_detail_url ' + exstr, level = log.WARNING)
        return None, None, None, None

def get_left_goods(num_iid):
    try:
        op = OpenTaobao(APP_KEY, SECRET_CODE)
        params = {
            'method':'taobao.item.get',
            'fields':'num',
            'num_iid':str(num_iid),
        }
        dict_str = op.get_result(params)
        ret_dict = ast.literal_eval(dict_str)
        if ret_dict.has_key('item_get_response'):
            if ret_dict['item_get_response'].has_key('item'):
                if ret_dict['item_get_response']['item'].has_key('num'):
                    return int(ret_dict['item_get_response']["item"]["num"])
    except:
        exstr = traceback.format_exc()
        log.msg('failed to get_pic_url ' + exstr, level = log.WARNING)
        return None

def get_item_id(url):
    L=re.findall(r'(?<=item_id=)\w+',url)
    if len(L) > 0:
        return int(L[0])
    return None

def get_id(url):
    L=re.findall(r'(?<=id=)\w+',url)
    if len(L) > 0:
        return int(L[0])
    return None

def get_task_id(string):
    L=re.findall(r'(?<=TaskId=)\w+', string)
    if len(L) > 0:
        return int(L[0])
    return None

def get_regex_value(string, regex):
    regex_expression = r'%s'%(regex)
    L=re.findall(regex_expression, string)
    if len(L) > 0:
        return int(L[0])
    return None
def get_one(array, index = 0):
    if len(array) > index:
        return array[index]
    else:
        return None
def get_one_string(array):
    if len(array) > 0:
        return array[0]
    else:
        return ""

def get_num(string):
    try:
        list_str = re.findall('[0-9]*', string)
        for elem in list_str:
            if elem != "":
                return int(elem)
    except:
        exstr = traceback.format_exc()
        if string == None:
            output_str = 'None'
        else:
            output_str = string
        log.msg('failed to get_num [' + output_str + '] ' + exstr, level = log.WARNING)
        return None
    return None

def get_float_str(string):
    list_str = re.findall('[0-9\.]*', string.replace(',', ''))
    for elem in list_str:
        if elem != "":
            return elem
    return None

def to_fen(price_str):
    return int(float(price_str) * 100)

def get_float_str_to_fen(string):
    price_str = get_float_str(string)
    if not price_str:
        return None
    if price_str == '':
        return None
    return to_fen(get_float_str(string))

def get_discount(current_price, origin_price):
    discount = float(current_price * 100)/float(origin_price)
    return int (round(discount, 0))
#    return int((current_price/origin_price) * 100)
#2.8折 => 28
def get_discount_int(discount_str):
    return int(float(discount_str) * 10)

def get_discount_int_from_float_str(string):
    return get_discount_int(get_float_str(string))

def set_origin_value(item, cursor, key):
    if cursor.has_key(key):
        origin_value = cursor[key]
        item[key] = origin_value

def set_origin_value_if_db_smaller(item, cursor, key):
    if cursor and cursor.has_key(key) and item.has_key(key):
        if cursor[key] < item[key]:
            origin_value = cursor[key]
            item[key] = origin_value
            return True
    return False

def status_to_str(stat):
    if stat == NOT_BEGIN:
        return 'not_begin'
    elif stat == BEGIN:
        return 'begin'
    elif stat == END:
        return 'end'
    else:
        return 'unknown status'

def check_status(item, cursor):
    if not cursor:
        log.msg('first status [%s] url [%s]'% (status_to_str(item['stat']), item['link']), level = log.DEBUG)
    if cursor and cursor.has_key('stat') and item.has_key('stat'):
        if cursor['stat'] != item['stat']:
            log.msg('change status [%s] -> [%s] url [%s]'% (status_to_str(cursor['stat']), status_to_str(item['stat']), item['link']), level = log.DEBUG)

def set_origin_value_list(item, cursor, key_list):
    if cursor :
        for key in key_list:
            if cursor.has_key(key):
                origin_value = cursor[key]
                item[key] = origin_value

def set_default_conf(start_url_info):
    if not start_url_info.has_key('type'):
        start_url_info['type'] = u'其它'

def load_conf(file_path_list):
    start_url_info_dict = {} 
    start_url_info = {} 
    for file_path in file_path_list:
        file = open(file_path)
        while True:
            buffer = file.readline()
            if not buffer:
                break
            if buffer[0] == '#': 
                continue
            if has_prefix(buffer, 'start_url') and start_url_info.has_key('start_url'):
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
            set_default_conf(start_url_info)    
            start_url_info_dict[start_url] = start_url_info
    return start_url_info_dict 

def get_url_by_browser(driver, url):
    try:
        driver.get(url)
        return True
    except TimeoutException:
        exstr = traceback.format_exc()
        log.msg('exception timeout when driver.get url ' + url + " " + str(exstr), level = log.WARNING)
        logger.warning('exception timeout when driver.get url ' + url + " " + str(exstr))
        return False
    except:
        exstr = traceback.format_exc()
        log.msg('failed when driver.get url ' + url + " " + str(exstr), level = log.WARNING)
        logger.warning('failed when driver.get url ' + url + " " + str(exstr))
        return False

def get_url_by_browser_for_times(driver, url, times):
    for i in xrange(times):
        if get_url_by_browser(driver, url):
            return True
        logger.warning("try " + str(i) + ' times')
    return True

def get_current_url(driver):
    try:
        return driver.current_url
    except:
        exstr = traceback.format_exc()
        log.msg('failed when return driver.current_url ' + str(exstr), level = log.WARNING)
        return None

def get_text_by_reg(h, xpath, index=0):
    real_h = None
    if xpath == 'text()':
        real_h = h
    elif len(xpath) > len('/text()'):
        xpath_end_idx = len(xpath) - len('/text()')
        real_h = get_one(h.select(xpath[0:xpath_end_idx]), index)
    else:
        log.msg("invalid text xpath " + xpath, level = log.ERROR)
    if real_h:
        cur_str = real_h.extract()
        attr_value = get_content(cur_str)
        return attr_value
    return None

#['title', 'div[@class="product-summary"]/div[@class="product-main-title"]/h1[@class="wb"]/@title', 'string', None],
def get_attr(xpath_list, h, by_reg = False):
    attr_dict = {}
    for attr_info in xpath_list:
        try:
            attr_name = attr_info[0]
            xpath = attr_info[1]
            func = attr_info[2]
            default_value = attr_info[3]
            index = 0
            if len(attr_info) > 4:
                index = attr_info[4]
            if by_reg and has_suffix(xpath, 'text()'):
                attr_value = get_text_by_reg(h, xpath, index)
            else:
                attr_value = get_one(h.select(xpath).extract(), index)

            if not attr_value:
                attr_value = default_value
                log.msg(attr_name + " None", level = log.DEBUG)
                if attr_value != None:
                    attr_dict[attr_name] = attr_value
            else:
                log.msg(attr_name + " [" + attr_value.encode('utf8') + ']', level = log.DEBUG)
                if func == 'int':
                    real_attr_value = int(attr_value)
                elif func == 'float':
                    real_attr_value = float(attr_value)
                elif func == 'string':
                    real_attr_value = attr_value
                elif func == 'strip':
                    real_attr_value = attr_value.strip()
                elif func == 'to_fen':
                    real_attr_value = to_fen(attr_value)
                elif func == 'get_num':
                    real_attr_value = get_num(attr_value)
                elif func == 'get_discount_int':
                    real_attr_value = get_discount_int(attr_value)
                elif func == 'get_float_str_to_fen':
                    real_attr_value = get_float_str_to_fen(attr_value)
                elif func == 'get_discount_int_from_float_str':
                    real_attr_value = get_discount_int_from_float_str(attr_value)
                else:
                    log.msg("error unknown func " + func, level = log.ERROR)
                    return None
                if not real_attr_value:
                    real_attr_value = default_value
                if real_attr_value:
                    attr_dict[attr_name] = real_attr_value
                if attr_dict.has_key(attr_name):
                    if func != 'string' and func != 'strip':
                        log.msg(attr_name + " [" + str(attr_dict[attr_name]) + ']', level = log.DEBUG)
                    else:
                        log.msg(attr_name + " [" + attr_dict[attr_name].encode('utf8') + ']', level = log.DEBUG)
                else:
                    log.msg(attr_name + " None", level = log.DEBUG)
        except:
            exstr = traceback.format_exc()
            log.msg('failed to get attr_name [' + attr_name + '] ' + exstr, level = log.ERROR)
            return None
    return attr_dict

#['title', 'div[@class="product-summary"]/div[@class="product-main-title"]/h1[@class="wb"]', 'title', 'string', None],
def get_obj_attr(xpath_list, obj):
    attr_dict = {}
    for attr_info in xpath_list:
        try:
            attr_name = attr_info[0]
            xpath = attr_info[1]
            tag_attr = attr_info[2]
            func = attr_info[3]
            default_value = attr_info[4]
            index = 0
            if len(attr_info) > 5:
                index = attr_info[5]
            try:
                if xpath != '':
                    if index != 0:
                        sub_obj = obj.find_elements_by_xpath(xpath)[index]
                    else:
                        sub_obj = obj.find_element_by_xpath(xpath)
                else:
                    sub_obj = obj
                if tag_attr == 'text()':
                    attr_value = sub_obj.text
                else:
                    attr_value = sub_obj.get_attribute(tag_attr)
                '''
                if tag_attr == 'text()':
                    if index == 0:
                        attr_value = obj.find_element_by_xpath(xpath).text
                    else:
                        attr_value = obj.find_elements_by_xpath(xpath)[index].text
                else:
                    if index == 0:
                        attr_value = obj.find_element_by_xpath(xpath).get_attribute(tag_attr)
                    else:
                        attr_value = obj.find_elements_by_xpath(xpath)[index].get_attribute(tag_attr)
                '''
            except NoSuchElementException:
                log.msg(attr_name + " None", level = log.DEBUG)
                attr_value = default_value
                if attr_value != None:
                    attr_dict[attr_name] = attr_value
            else:
                if attr_value:
                    log.msg(attr_name + " [" + attr_value.encode('utf8') + ']', level = log.DEBUG)
                    if func == 'int':
                        real_attr_value = int(attr_value)
                    elif func == 'float':
                        real_attr_value = float(attr_value)
                    elif func == 'string':
                        real_attr_value = attr_value
                    elif func == 'strip':
                        real_attr_value = attr_value.strip()
                    elif func == 'to_fen':
                        real_attr_value = to_fen(attr_value)
                    elif func == 'get_num':
                        real_attr_value = get_num(attr_value)
                    elif func == 'get_discount_int':
                        real_attr_value = get_discount_int(attr_value)
                    elif func == 'get_float_str_to_fen':
                        real_attr_value = get_float_str_to_fen(attr_value)
                    elif func == 'get_discount_int_from_float_str':
                        real_attr_value = get_discount_int_from_float_str(attr_value)
                    else:
                        log.msg("error unknown func " + func, level = log.ERROR)
                        return None
                    if not real_attr_value:
                        real_attr_value = default_value
                    if real_attr_value:
                        attr_dict[attr_name] = real_attr_value
                    if attr_dict.has_key(attr_name):
                        if func != 'string':
                            log.msg(attr_name + " [" + str(attr_dict[attr_name]) + ']', level = log.DEBUG)
                        else:
                            log.msg(attr_name + " [" + attr_dict[attr_name].encode('utf8') + ']', level = log.DEBUG)
                    else:
                        log.msg(attr_name + " None", level = log.DEBUG)
                else:
                    log.msg(attr_name + " None", level = log.DEBUG)
                    attr_value = default_value
                    if attr_value != None:
                        attr_dict[attr_name] = attr_value
        except:
            exstr = traceback.format_exc()
            log.msg('failed to get attr_name [' + attr_name + '] ' + exstr, level = log.ERROR)
            return None
    return attr_dict

def get_default_end_time():
    end_time_str = str(datetime.now().date()) + " 23:59:59"
    end_time = int(datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S").strftime("%s"))
    return end_time

def get_default_start_time():
    start_time_str = str(datetime.now().date()) + " 00:00:00"
    start_time = int(datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S").strftime("%s"))
    return start_time

def find_element_by_xpath(driver, xpath, log_level = log.ERROR):
    try:
        a_obj = driver.find_element_by_xpath(xpath)
        return a_obj
    except NoSuchElementException:
        exstr = traceback.format_exc()
        log.msg('failed to find_element_by_xpath ' + xpath + ' NoSuchElementException ' + exstr, level = log_level)
        return None
    except:
        exstr = traceback.format_exc()
        log.msg('failed to find_element_by_xpath ' + xpath + ' ' + exstr, level = log_level)
        return None

def find_elements_by_xpath(driver, xpath, log_level = log.ERROR):
    try:
        a_objs = driver.find_elements_by_xpath(xpath)
        return a_objs
    except NoSuchElementException:
        exstr = traceback.format_exc()
        log.msg('failed to find_elements_by_xpath ' + xpath + ' NoSuchElementException' + exstr, level = log_level)
        return None
    except:
        exstr = traceback.format_exc()
        log.msg('failed to find_elements_by_xpath ' + xpath + ' ' + exstr, level = log_level)
        return None

def driver_quit(driver, log_level = log.ERROR):
    try:
        log.msg('driver.quit()', level = log.INFO)
        logger.info('driver.quit()')
        driver.quit()
    except:
        exstr = traceback.format_exc()
        log.msg('failed to driver.quit() ' + exstr, level = log_level)

def click_url(driver, xpath, sleep_second = 2):
    try:
        a_obj = find_element_by_xpath(driver, xpath)
        if not a_obj:
            return None
        a_obj.click()
        time.sleep(sleep_second)

        url = driver.current_url
    except:
        exstr = traceback.format_exc()
        log.msg('failed when chick url xpath ' + xpath + ' ' + str(exstr), level = log.WARNING)
        return None
    return url

def click_a_obj(driver, a_obj):
    try:
        if not a_obj:
            return None
        a_obj.click()
        time.sleep(2)

        url = driver.current_url
    except:
        exstr = traceback.format_exc()
        log.msg('failed when chick a_obj ' + str(exstr), level = log.WARNING)
        return None
    return url

def execute_script(driver, command):
    try:
        driver.execute_script(command)
    except:
        exstr = traceback.format_exc()
        log.msg('failed when execute_script ' + command + str(exstr), level = log.WARNING)
        return False
    return True
def is_item_changed(item, cursor):
    if not cursor:
        return True
    elif cursor['ori_price'] != item['ori_price']:
        return True
    elif cursor['cur_price'] != item['cur_price']:
        return True
    return False

def check_url(url):
    try:
        a = urllib2.urlopen(url)
    except:
        exstr = traceback.format_exc()
        log.msg('failed to get url ' + str(exstr), level = log.WARNING)
        return False, 0
    return True, a.getcode()

def download_url(url):
    try:
        a = urllib2.urlopen(url)
        return a.read()
    except:
        exstr = traceback.format_exc()
        log.msg('failed to download url code ' + str(exstr), level = log.WARNING)
        return None

def get_string(item, key):
    value = item[key]
    if value.__class__.__name__ == 'list':
        info = ''
        for i in xrange(len(value)):
            #if i > 0:
            #    info = info + ' '
            info = info + value[i]
        return info
    else:
        return value

def async_get_cats_info(type):
    op = OpenTaobao(APP_KEY, SECRET_CODE)
    params = {
        'method':'taobao.topats.itemcats.get',
        'output_format':'json',
        'cids': '0',
        'type': type,
    }
    dict_str = op.get_result(params)
    ret_dict = json.loads(dict_str)
    return ret_dict

def async_get_result(taskid):
    op = OpenTaobao(APP_KEY, SECRET_CODE)
    params = {
        'method':'taobao.topats.result.get',
        'task_id': taskid,
    }
    dict_str = op.get_result(params)
    ret_dict = json.loads(dict_str)
    return ret_dict

def get_root_cid():
    op = OpenTaobao(APP_KEY, SECRET_CODE)
    params = {
        'method':'taobao.itemcats.get',
        'fields':'name, cid',
        'parent_cid': '0',
    }
    dict_str = op.get_result(params)
    ret_dict = json.loads(dict_str)
    return ret_dict

def download_result(taskid, download_file):
    while True:
        ret_dict = async_get_result(taskid)
        if ret_dict.has_key('topats_result_get_response') and ret_dict['topats_result_get_response']['task']['status'] == 'done':
            url = ret_dict['topats_result_get_response']['task']['download_url']

            form_data = urllib.urlencode({})
            buffer = urllib2.urlopen(url, form_data).read()
            file = open(download_file, 'w')
            file.write(buffer)
            file.close()
            break
        else:
            time.sleep(10)

def get_cats_info(type, download_file):
    ret_dict = async_get_cats_info(type)
    #print 'ret_dict ' + str(ret_dict)
    if ret_dict.has_key('topats_itemcats_get_response'):
        taskid = ret_dict['topats_itemcats_get_response']['task']['task_id']
    elif ret_dict.has_key('error_response'):
        sub_msg = ret_dict['error_response']['sub_msg']
        taskid = get_task_id(sub_msg)
        if not taskid:
            return
        #print 'taskid ' + str(taskid)
    async_ret_dict = async_get_result(taskid)
    #print 'async_ret_dict ' + str(async_ret_dict)
    download_result(taskid, download_file)
        

def build_root_leave_dict(origin_cat_dict, root_leave_dict, level = 0, verbose = False):
    if not origin_cat_dict.has_key('cid'):
        return
    if not origin_cat_dict['cid']:
        return
    cid = origin_cat_dict['cid']
    if not root_leave_dict.has_key(cid):
        root_leave_dict[cid] = {}

    if not origin_cat_dict.has_key('childCategoryList'):
        return
    if not origin_cat_dict['childCategoryList']:
        return
    #print 'origin_cat_dict.__class__.__name__ ' + origin_cat_dict.__class__.__name__ + " " + str(root_leave_dict)
    try:
        #print 'level ' + str(level) + ' ' + str(len(origin_cat_dict['childCategoryList']))
        for item in origin_cat_dict['childCategoryList']:
            sub_cid = item['cid']
            name = ''
            if item.has_key('name'):
                name = item['name'].encode('utf8')
            if verbose:
                print str(sub_cid) + '\t' + str(cid) + '\t' + name
            root_leave_dict[cid][sub_cid] = {}
            build_root_leave_dict(item, root_leave_dict[cid], level + 1, verbose)
    except:
        exstr = traceback.format_exc()
        log.msg('failed to build_root_leave_dict ' + exstr, level = log.WARNING)
        return 

def build_cat_tree(dir_list, verbose = False):
    root_leave_dict = {}
    for dir in dir_list:
        files = os.listdir(dir)
        #print 'files : ' + str(files)
        i = 0
        for file in files:
            path=dir + '/' + file
            f = open(path, 'r')
            #print 'open ' + path
            buffer = f.read()
            ret_dict = json.loads(buffer)
            build_root_leave_dict(ret_dict, root_leave_dict, 0, verbose)
            i = i + 1

        #print 'root_leave_dict ' + str(root_leave_dict)
        return root_leave_dict

def build_cat_map(root_leave_dict, root_cid, map_dict):

    for cid in root_leave_dict:
        if len(root_leave_dict[cid]) == 0:
            map_dict[cid] = root_cid
        else:
            build_cat_map(root_leave_dict[cid], root_cid, map_dict)

def build_cat_total_map(root_leave_dict):
    map_dict = {}
    for cid in root_leave_dict:
        build_cat_map(root_leave_dict[cid], cid, map_dict)

    return map_dict

def print_cat_tree(dir_list):
    root_leave_dict = build_cat_tree(dir_list, True)
    #print_sub_cat_tree(root_leave_dict, 0)

g_cid_map = {
        u'服饰箱包':u'穿的', 
        u'珠宝首饰':u'穿的', 
        u'鞋靴':u'穿的', 
        u'男装':u'穿的', 
        u'运动服/休闲服装':u'穿的', 
        u'流行男鞋':u'穿的', 
        u'女装/女士精品':u'穿的', 
        u'女鞋':u'穿的', 
        u'箱包皮具/热销女包/男包':u'穿的', 
        u'女士内衣/男士内衣/家居服':u'穿的', 
        u'服饰配件/皮带/帽子/围巾':u'穿的', 
        u'珠宝/钻石/翡翠/黄金':u'穿的', 
        u'运动鞋new':u'穿的', 
        u'饰品/流行首饰/时尚饰品新':u'穿的', 
        u'手表':u'穿的', 
        u'运动包/户外包/配件':u'穿的',

        u'食品':u'吃的',
        u'餐饮美食': u'吃的',
        u'零食/坚果/特产': u'吃的',
        u'粮油米面/南北干货/调味品' : u'吃的',
        u'茶/咖啡/冲饮':u'吃的',
        u'水产肉类/新鲜蔬果/熟食':u'吃的',
        u'酒类':u'吃的',

        u'小家电':u'数码/家电', 
        u'数码影音':u'数码/家电', 
        u'手机/通讯':u'数码/家电', 
        u'电视、音响':u'数码/家电', 
        u'电脑用品':u'数码/家电', 
        u'国货精品数码':u'数码/家电', 
        u'手机':u'数码/家电', 
        u'数码相机/单反相机/摄像机':u'数码/家电', 
        u'MP3/MP4/iPod/录音笔':u'数码/家电', 
        u'笔记本电脑':u'数码/家电', 
        u'平板电脑/MID':u'数码/家电', 
        u'台式机/一体机/服务器':u'数码/家电', 
        u'电脑硬件/显示器/电脑周边':u'数码/家电', 
        u'网络设备/网络相关':u'数码/家电', 
        u'3C数码配件':u'数码/家电', 
        u'闪存卡/U盘/存储/移动硬盘':u'数码/家电', 
        u'办公设备/耗材/相关服务':u'数码/家电', 
        u'电子词典/电纸书/文化用品':u'数码/家电', 
        u'电玩/配件/游戏/攻略':u'数码/家电', 
        u'大家电':u'数码/家电', 
        u'影音电器':u'数码/家电', 
        u'生活电器':u'数码/家电', 
        u'厨房电器':u'数码/家电',

        u'个护健康':u'日用品', 
        u'家居':u'日用品', 
        u'家居装修':u'日用品', 
        u'钟表':u'日用品', 
        u'厨具':u'日用品', 
        u'住宅家具':u'日用品', 
        u'居家日用/婚庆/创意礼品':u'日用品', 
        u'厨房/餐饮用具':u'日用品', 
        u'清洁/卫浴/收纳/整理用具':u'日用品', 
        u'床上用品/布艺软饰':u'日用品', 
        u'洗护清洁剂/卫生巾/纸/香薰':u'日用品', 

        u'彩妆/香水/美妆工具':u'化妆品',
        u'美容护肤/美体/精油':u'化妆品',
        u'美发护发/假发':u'化妆品',

        }
def get_root_cid_map():
    ret_dict = get_root_cid()
    root_cid_map = {}
    if ret_dict.has_key('itemcats_get_response'):
        for item in ret_dict['itemcats_get_response']['item_cats']['item_cat']:
            cid = item['cid']
            name = item['name']

            if g_cid_map.has_key(name):
                root_cid_map[cid] = {'origin_category_name' : name, 'category_name' : g_cid_map[name]}
            else:
                root_cid_map[cid] = {'origin_category_name' : name, 'category_name' : u'其它'}
    return root_cid_map

def get_url_content(url):
    try:
        params = {}
        form_data = urllib.urlencode(params)
        buffer = urllib2.urlopen(url, form_data).read()
        return buffer
    except:
        exstr = traceback.format_exc()
        log.msg('failed to get_url_content ' + url + ' ' + exstr, level = log.WARNING)
        return None 

class CategoryGet:
    def __init__(self, dir_list):
        self.root_cid_map = get_root_cid_map() 
        self.root_dict = build_cat_tree(dir_list)
        self.map_dict = build_cat_total_map(self.root_dict)

    def get_cid_name(self, cid):
        if self.map_dict.has_key(cid):
            root_cid = self.map_dict[cid]
            if self.root_cid_map.has_key(root_cid):
                return self.root_cid_map[root_cid]['origin_category_name'], self.root_cid_map[root_cid]['category_name']
        return u'其它', u'其它'

    def tranverse(self):
        for key in self.map_dict:
            print str(key) + ' -> ' + self.get_cid_name(key).encode('utf8')

g_zseckill_category_map = {
        u'鞋靴':u'穿的',
        u'服饰箱包':u'穿的',

        u'食品':u'吃的',

        u'小家电':u'数码/家电', 
        u'数码影音':u'数码/家电',
        u'手机/通讯':u'数码/家电',
        u'电视、音响':u'数码/家电',
        u'电脑用品':u'数码/家电',

        u'家居':u'日用品',
        u'钟表':u'日用品',
        u'运动户外休闲':u'日用品',

        u'珠宝首饰':u'化妆品',

        u'汽车用品':u'其它',
        u'图书':u'其它',
        u'乐器':u'其它',
        u'家居装修':u'其它',
        u'玩具':u'其它',
        u'宠物用品':u'其它',
        u'厨具':u'其它',
        u'个护健康':u'其它',
        u'母婴用品':u'其它',

        }
def get_zseckill_cateogry_name(origin_category_name):
    if g_zseckill_category_map.has_key(origin_category_name):
        return g_zseckill_category_map[origin_category_name]
    else:
        return u'其它'

def scroll_down(driver, count, sleep_second = 1):
    for i in xrange(count):
        if not execute_script(driver, "window.scrollTo(0,Math.max(document.documentElement.scrollHeight," + 
                "document.body.scrollHeight,document.documentElement.clientHeight));"):
            return
        time.sleep(sleep_second)

def write_file(file_name, buffer):
    file = open(file_name, 'w')
    file.write(buffer)
    file.close()

def encode(string, code_type):
    try:
        return string.encode(code_type)
    except:
        exstr = traceback.format_exc()
        log.msg('failed to encode ' + code_type + ' ' + exstr, level = log.WARNING)
        return None

def decode(string, code_type):
    try:
        return string.decode(code_type)
    except:
        exstr = traceback.format_exc()
        log.msg('failed to decode ' + code_type + ' ' + exstr, level = log.WARNING)
        return None

def extract(obj, xpath):
    try:
        attr_list = {'/@href':'href', '/@src':'src', '/text()':'/text()'}
        for attr in attr_list:
            len_text = len(attr)
            if len(xpath) >= len(attr) and xpath[(-1)*len_text:] == attr:
                real_xpath = xpath[:(-1)*len_text]
                obj_array = find_elements_by_xpath(obj, real_xpath)
                if not obj_array:
                    return []
                values = []
                for obj in obj_array:
                    if attr == '/text()':
                        values.append(obj.text)
                    else:
                        values.append(obj.get_attribute(attr_list[attr]))
                return values
        return []
    except:
        exstr = traceback.format_exc()
        log.msg('failed to extract ' + xpath + ' ' + exstr, level = log.WARNING)
        return []

def unix_time_to_datetime(u):
    #return datetime.utcfromtimestamp(u)
    return datetime.fromtimestamp(u)

def resize_img(input_file, output_file, size, fix_width = False, size_th=0):
    try:
        im = Image.open(input_file)
        (x,y) = im.size #read image size
        if size_th > 0 and (x < size_th or y < size_th):
            logger.warning('img has been neglected as too small')
            return RESIZE_FAIL_SMALL
        if not fix_width:
            if x < y:
                y_s = size #define standard width
                x_s = x * y_s / y #calc height based on standard width
            else:
                x_s = size #define standard width
                y_s = y * x_s / x #calc height based on standard width
        else:
            if x < size:
                x_s = x
                y_s = y
            else:
                x_s = size #define standard width
                y_s = y * x_s / x #calc height based on standard width
        out = im.resize((x_s,y_s),Image.ANTIALIAS) #resize image with high-quality
        logger.info('x ' + str(x) + ' y ' + str(y) + ' x_s ' + str(x_s) + ' y_s ' + str(y_s))
	output_dir = output_file[:output_file.rfind('/')]
	if not os.path.isdir(output_dir):
	    os.makedirs(output_dir)
	out.save(output_file)
        return RESIZE_SUCCESS
    except:
        exstr = traceback.format_exc()
        logger.error('failed to resize_img ' + exstr)
        return RESIZE_FAIL_TRANS

def feed_is_timeout(item, keywords, second, attr='title'):
    title = get_string(item, attr)
    now_time = int(time.time())
    pub_time_str = item['pub_time']
    pub_time = int(datetime.strptime(pub_time_str, "%Y-%m-%d %H:%M:%S").strftime("%s"))
    for key in keywords:
        if title and title.find(key) != -1:
            if now_time - pub_time > second:
                logger.info('id : ' + str(item['id'])+ ' pub_time ' + pub_time_str + ' title ' + title)
                return True
    return False

def feed_check_timeout(item):
    if feed_is_timeout(item, [u'手慢无', u'神价'], 6 * 3600):
        return True
    if feed_is_timeout(item, [u'秒杀', u'开抢', u'今日'], 24 * 3600):
        return True
    if feed_is_timeout(item, [u'今日'], 24 * 3600, 'desc'):
        return True
    if feed_is_timeout(item, [u'限时'], 72 * 3600):
        return True
    return False

def resize_img_url(img_url, size_list, img_dir, prefix, fix_width, size_th=0):
    try:
        buffer = download_url(img_url)
        if not buffer:
            logger.warning('failed to download_url ' + img_url)
            return None
        hash_code = hashlib.md5(img_url).hexdigest().upper()
        input_file_name = hash_code + ".orig"
        write_file(input_file_name, buffer)
        d = {}
        for size in size_list:
            size_name = str(size) + 'x' + str(size)
            output_file_name = hash_code + "_" + size_name + '.png'
            ret = resize_img(input_file_name, img_dir + '/' + output_file_name, size, fix_width, size_th)
            if ret == RESIZE_FAIL_TRANS:
                logger.error('failed to resize_img_url ' + img_url)
                os.remove(input_file_name)
                return None
            if ret == RESIZE_FAIL_SMALL:
               d['0x0'] = prefix + output_file_name 
            elif ret == RESIZE_SUCCESS:
                d[size_name] = prefix + output_file_name
        os.remove(input_file_name)
        return d
    except:
        exstr = traceback.format_exc()
        logger.error('failed to resize_img_url ' + img_url + ' ' + exstr)
        return None

def get_size_of_img(input_file):
    try:
        im = Image.open(input_file)
        (x,y) = im.size #read image size
        return (x, y)
    except:
        exstr = traceback.format_exc()
        logger.error('failed to get_size_of_img ' + exstr)
        return None

def get_size_of_img_url(img_url):
    try:
        buffer = download_url(img_url)
        if not buffer:
            logger.warning('failed to download_url ' + img_url)
            return None
        hash_code = hashlib.md5(img_url).hexdigest().upper()
        input_file_name = hash_code + ".orig"
        write_file(input_file_name, buffer)
        img_size = get_size_of_img(input_file_name)
        os.remove(input_file_name)
        return img_size
    except:
        exstr = traceback.format_exc()
        logger.error('failed to get_size_of_img_url ' + img_url + ' ' + exstr)
        return None

def resize_ztmhs_img_url(img_url, size_list, img_dir, prefix, fix_width, hash_code):
    try:
        buffer = download_url(img_url)
        if not buffer:
            logger.warning('failed to download_url ' + img_url)
            print 'warning failed to download_url ' + img_url
            return None
        #hash_code = hashlib.md5(img_url).hexdigest().upper()
        input_file_name = hash_code + ".orig"
        write_file(input_file_name, buffer)
        d = {}
        date_str = datetime.now().strftime('%Y%m%d%H%M%S')
        for size in size_list:
            size_name = str(size) + 'x' + str(size)
            output_file_name = '%s_%s_%s.%s'%(size_name, hash_code, date_str, 'png')
            #output_file_name = size_name + '_' + hash_code + "_" +  + '.png'
            if resize_img(input_file_name, img_dir + '/' + output_file_name, size, fix_width) < 0:
                print 'error failed to resize_img_url ' + img_url
                os.remove(input_file_name)
                return None
            d[size_name] = prefix + output_file_name
        os.remove(input_file_name)
        img_path = '/' + prefix + '%s_%s.%s'%(hash_code, date_str, 'png')
        return d, img_path
    except:
        exstr = traceback.format_exc()
        logger.error('failed to resize_img_url ' + img_url + ' ' + exstr)
        return None, None

def gen_ztmhs_img(item, img_dir, prefix):
    if item.has_key('img'):
        if not item['img']:
            logger.warning('img is None id ' + str(item['id']))
            print 'warning img is None id ' + str(item['id'])
            return True
        logger.info('img_url ' + str(item['img']))
        if item['img'].__class__.__name__ == 'list' and len(item['img']) > 0:
            img_url = item['img'][0]
        elif item['img'].__class__.__name__ != 'list':
            img_url = item['img']
        else:
            logger.warning('invalid format id ' + str(item['id']))
            print 'warning invalid format id ' + str(item['id'])
            return False
        #if is_ztmhs:
        #    img_url = 'http://www.ztmhs.com' + img_url
        d, img_path = resize_ztmhs_img_url(img_url,[80, 100, 130], img_dir, prefix,  fix_width = False, hash_code = item['id'])
        if not d:
            logger.warning('failed to resize_img_url invalid format id ' + str(item['id']))
            print 'warning failed to resize_img_url invalid format id ' + str(item['id'])
            return False
        item['img_app'] = d
        item['img'] = img_path
        return True
    return True

def gen_img(item, img_dir, prefix, is_ztmhs = False):
    if item.has_key('img'):
        if not item['img']:
            logger.warning('img is None id ' + str(item['id']))
            return True
        logger.info('img_url ' + str(item['img']))
        if item['img'].__class__.__name__ == 'list' and len(item['img']) > 0:
            img_url = item['img'][0]
        elif item['img'].__class__.__name__ != 'list':
            img_url = item['img']
        else:
            logger.warning('invalid format id ' + str(item['id']))
            return False
        if is_ztmhs:
            img_url = 'http://www.ztmhs.com' + img_url
        d = resize_img_url(img_url,[80, 100, 130], img_dir, prefix,  fix_width = False)
        if not d:
            logger.warning('failed to resize_img_url invalid format id ' + str(item['id']))
            return False
        item['img_app'] = d
        return True
    return True

def gen_text_img(item, img_dir, prefix):
    if item.has_key('text'):
        if not item.has_key('img_text_app'):
            item['img_text_app'] = {}
        for elem in item['text']:
            if elem[0] == '0':
                img_url = elem[1]
                logger.info('text_img_url ' + str(img_url.encode('utf8')))
                try:
                    hash_code = hashlib.md5(img_url).hexdigest().upper()
                    d = resize_img_url(img_url,[480], img_dir, prefix, fix_width = True)
                    if not d:
                        logger.warning('failed to resize_img_url in gen_text_img id ' + str(item['id']))
                        return False
                except:
                    exstr = traceback.format_exc()
                    logger.error('failed to gen hash_code for text_img_url ' + str(img_url.encode('utf8')) + exstr)
                    log.msg('failed to gen hash_code for text_img_url ' + str(img_url.encode('utf8')) + exstr, level = log.ERROR)
                    return True
                item['img_text_app'][hash_code] = d
    return True

def create_firefox(try_times = 1):
    for i in xrange(try_times):
        driver = None
        try:
            driver = webdriver.Firefox()
            logger.info('success to create_firefox pid = ' + str(driver.binary.process.pid))
            log.msg('success to create_firefox pid = ' + str(driver.binary.process.pid), level = log.INFO)
            return driver
        except:
            exstr = traceback.format_exc()
            logger.error('failed to create_firefox ' + exstr)
            log.msg('failed to create_firefox ' + exstr, level = log.ERROR)
            if driver:
                logger.error('failed to create_firefox but driver not None')
                log.msg('failed to create_firefox but driver not None', level = log.ERROR)
                driver_quit(driver)
            continue
    return None

def has_prefix(string, prefix):
    if len(string) >= len(prefix):
        if string[0:len(prefix)] == prefix:
            return True
    return False

def has_suffix(string, suffix):
    if len(string) >= len(suffix):
        if string[(-1)*len(suffix):] == suffix:
            return True
    return False

def get_url_by_domain(url, domain_name):
    if not has_prefix(url, 'http'):
        return_url = ''
        if not has_prefix(url, '/'):
            return_url = domain_name + '/' + url
        else:
            return_url = domain_name + url
        infos = url.encode('utf8') + ' -> ' + return_url.encode('utf8')
        #print infos
        logger.debug(infos)
        log.msg(infos, level = log.DEBUG)
        return return_url
    else:
        return url

def get_one_value(d, key_list):
    value = None
    for key in key_list:
        if d.has_key(key):
            value = d[key]
            break
    return value

def has_key(d, key_list):
    for key in key_list:
        if d.has_key(key):
            return True
    return False

def get_index(list, value):
    for i in xrange(len(list)):
        if value == list[i]:
            return i
    return -1

def get_content(cur_str, min_str_len = 2):
    dr = re.compile(r'<[^>]+>',re.S)
    if not '<script' in cur_str:
        desc_str = dr.sub('',cur_str)
        if len(desc_str) > min_str_len:
            log.msg("content by re [" + str(desc_str.encode('utf8')) + ']', level = log.DEBUG)
            return desc_str
        else:
            log.msg('content has no data desc_str [%s] cur_str [%s]'%(desc_str, cur_str), level = log.WARNING)
            return None
    else:
        log.msg('conten has script cur_str[%s]'%(cur_str), level = log.WARNING)
        return None

def remove_expression(cur_str):
    dr = re.compile(r'\[[^\]]+\]',re.S)
    desc_str = dr.sub('',cur_str)
    change = False
    if len(desc_str) != len(cur_str):
        infos = 'content after remove expression [' + str(desc_str.encode('utf8')) + '] origin [' + str(cur_str.encode('utf8')) + ']'
        log.msg(infos, level = log.DEBUG)
        print infos
        change = True
    return desc_str, change

def is_xml(response):
    return has_prefix(response.body, '<?xml')

def get_xpath_selector(response):
    if is_xml(response):
        return XmlXPathSelector(response)
    else:
        return HtmlXPathSelector(response)

def get_xpath_selector_from_buffer(text):
    if has_prefix(text, '<?xml'):
        return XmlXPathSelector(text=text)
    else:
        return HtmlXPathSelector(text=text)

def get_xpath_selector_from_response(text, response):
    if is_xml(response):
        return XmlXPathSelector(text=text)
    else:
        return HtmlXPathSelector(text=text)

def get_article_len(text_list):
    article_len = 0
    for text_item in text_list:
        if text_item[0] == '1':
            article_len += len(text_item[1])
    return article_len 

g_pingce_category = {
        u'生活知识' : 2,
        u'生活评测' : 2,
        u'生活百科' : 2,
        u'养生' : 3,
        u'食品安全预警' : 5,
        u'家电评测' : 4,
        u'商品导购' : 6,
        u'新闻' : 7,
        u'段子' : 8,
        u'本地生活' : 9,
        u'资讯网站' : 10,
        u'汽车' : 11,
        u'阅读' : 12,
        u'电影' : 13,
        u'女人' : 14,
        u'美食' : 15
        }

filter_common_list = [
        u'不得转载',
        u'未经作者许可',
        u'请勿转载',
        u'如需转载',
        u'请注明出处',
        u'网络编辑',
        u'转至微博',
        u'编辑点评',
        u'推荐阅读',
        u'欢迎广大网友、厂商互动',
        u'美食杰有话说：',
        u'当前位置',
        u'关键字',
        u'下一页',
        u'上一页',
        u'上一篇',
        u'下一篇',
        u'上一条',
        u'下一条',
        u'责任编辑',
        u'关键词：',
        u'前一页',
        u'后一页',
        u'原标题：',
        u'<!--',
        u'-->',
        u'相关推荐',
        u'相关文章',
        u'没有评论',
        u'getElementById',
        u'JiaThis Button BEGINJiaThis Button END',
        u'这行和图片列表唯一区别暂停播放自动播放',
        u'以下是haibao.com提供的广告',
        u'购买链接',
        ]

filter_content_list = [
        u'该文章不存在'
        ]

filter_jieqi_list = [
        u'立春',
        u'雨水',
        u'惊蛰',
        #u'春分',
        #u'清明',
        #u'谷雨',
        #u'立夏',
        u'小满',
        u'芒种',
        u'夏至',
        u'小暑',
        u'大暑',
        u'立秋',
        u'处暑',
        u'白露',
        u'秋分',
        u'寒露',
        u'霜降',
        u'立冬',
        u'小雪',
        u'大雪',
        u'冬至',
        u'小寒',
        u'大寒',
        u'酷暑',
        #u'春季',
        #u'夏季',
        #u'秋季',
        u'春节',
        u'端午节',
        u'菊花香',
        u'三月',
        u'十一',
        u'十月',
        u'炎热',
        u'中秋',
        u'清热解暑',
        u'父亲节',
        #u'春天',
        u'端午',
        u'解暑',
        u'蛇年',
        u'黄梅季节',
        u'国庆',
        u'秋天',
        u'节后',
        #u'梅雨季',
        u'高考',
        u'元宵',
        u'月饼',
        #u'春日',
        #u'初春',
        u'入秋',
        u'八月',
        u'母亲节',
        u'寒食节',
        u'奥运',
        #u'夏天',
        #u'夏',
        u'酷暑',
        #u'夏季',
        u'null',
        u'立秋',
        u'防暑',
        u'大雪',
        u'高温',
        u'小寒',
        u'秋季',
        u'处暑',
        u'消暑',
        u'白露',
        u'考试',
        u'腊八粥',
        u'圣诞',
        u'秋风',
        u'寒露',
        u'十一',
        u'初秋',
        u'霜降',
        u'中暑',
        u'立冬',
        u'小雪',
        #news
        u'视频',
        u'NEWS',
        u'$',
        u'评论(0)',
        ]

filter_invalid_desc = [
        u'分享人人网',
        ]
def need_filter(string, filter_list):
    for filter_item in filter_list:
        if string.find(filter_item) != -1:
            return True
    return False

def get_prev_datetime_str(old_datetime):
    old_year = int(old_datetime[:4])
    now_datetime = str(datetime.now())[:19]
    ret_datetime = old_datetime
    while (ret_datetime > now_datetime):
        old_year -= 1
        ret_datetime = str(old_year) + old_datetime[4:]
        print str(old_datetime) + ' -> ' + str(ret_datetime)
    return ret_datetime

def get_prev_datetime(old_datetime):
    old_datetime_str = str(old_datetime)[:19]
    ret_datetime_str = get_prev_datetime_str(old_datetime_str)
    ret_datetime = datetime.strptime(ret_datetime_str, '%Y-%m-%d %H:%M:%S')
    return ret_datetime

def valid_url(url):
    if not url:
        return False
    if url[0] == '#':
        return False
    if url.find('javascript') != -1:
        return False
    return True

def find_string(string, match_list):
    for match in match_list:
        index = string.find(match)
        if index != -1:
            return index
    return -1

def get_title_from_weibo(desc, id):
    desc_str = desc.strip()
    index = desc_str.find(u'【')
    if index == -1:
        index = desc_str.find('{')
    print ('item id ' + str(id) + '[' + desc + ']').encode('utf8')
    if index == 0:
        end_index = desc_str.find(u'】')
        if end_index == -1:
            end_index = desc_str.find('}')
        if end_index != -1:
            title = desc_str[1:end_index]
            content = desc_str[end_index + 1:]
        else:
            print ('error not match desc [' + desc_str + ']').encode('utf8')
            return None, None
    else:
        title = ''
        content = desc_str
    index2 = find_string(content, [u'via', u'（转）', u'by', u'分享自', u'发布自', u'@', u'阅读详情', u'详情点击', u'详情请点击', u'点链接看全文', u'详情'])
    if index2 != -1:
        if content[index2 - 1] == u'（':
            index3 = content.find(u'）', index2)
            if index3 != -1:
                content = content[:index2 - 1] + content[index3 + 1:]
            else:
                content = content[:index2]
        else:
            content = content[:index2]
    content = content.replace(u'（）', '').replace(u'【】', '')
    if len(content) < 40:
        print ('item id ' + str(id) + ' skip title [' + title + '] content ' + content).encode('utf8')
        return None, None
    print ('item id ' + str(id) + ' title [' + title + '] content ' + content).encode('utf8')
    if title == '':
        return None, content
    return title, content

def get_replset_conn():
    host_url = '%s:%i,%s:%i'%('localhost',27017,'localhost',27018)
    connection = pymongo.MongoReplicaSetClient(host=host_url, replicaSet='zhs_replset', read_preference=pymongo.ReadPreference.PRIMARY_PREFERRED)
    return connection

def is_filter(item):
    if item.has_key('type') and item['type'] == 0 and ((item.has_key('title') and item['title'] and need_filter(item['title'], filter_jieqi_list)) or (item.has_key('desc') and item['desc'] and need_filter(item['desc'], filter_jieqi_list))):
        return True
    return False

def print_memory_usage():
    from collections import defaultdict 
    d = defaultdict(int) 
    objects = gc.get_objects() 
    print 'gc objects size:', len(objects) 
    total_size = 0
    for o in objects: 
        d[type(o)] += sys.getsizeof(o) 
        total_size += sys.getsizeof(o)
    from pprint import pprint 
    pprint(dict(d))
    print 'total_size ' + str(total_size)

def dump_memory_usage(filename):
    from meliae import scanner
    scanner.dump_all_objects(filename)

def parse_memory_usage(filename):
	from meliae import loader
	#加载dump文件
	om = loader.load(filename)
	#计算各Objects的引用关系
	om.compute_parents()
	#去掉各对象Instance的_dict_属性
	om.collapse_instance_dicts()
	#分析内存占用情况
	om.summarize()

import objgraph
def show_objgraph():
    gc.collect()
    objgraph.show_most_common_types(limit=50)

type_to_id = {
        u"商品" : TYPE_GOODS,
        u"微博" : TYPE_WEIBO,
        u"新闻" : TYPE_NEWS,
        u"其它" : TYPE_OTHER
        }
class Classify:
    def __init__(self, cat_file = '../comm_lib/cat2.txt'):
        file = open(cat_file, 'r')
        self.cat_to_id = {}
        while True:
            buffer = file.readline()
            if not buffer:
                break
            buffer_array = buffer.split()
            level_1_id_str = buffer_array[0]
            level_1_name = buffer_array[1].decode('utf8')
            level_1_id = level_1_id_str
            if len(buffer_array) > 2:
                level_2_id_str = buffer_array[2]
                level_2_name = buffer_array[3].decode('utf8')
                name_list = level_2_name.split(u'/')
                for name in name_list:
                    id = level_2_id_str
                    #self.cat_to_id[name] = {'id':id, 'parent_id':level_1_id}
                    self.set_id(name, id, level_1_id)
            #self.cat_to_id[level_1_name] = {'id':level_1_id}
            self.set_id(level_1_name, level_1_id, None)
    def set_id(self, name, id, parent_id):
        if not self.cat_to_id.has_key(name):
            self.cat_to_id[name] = {}
        if not parent_id:
            info = {'id':id}
        else:
            info = {'id':id, 'parent_id': parent_id}
        if has_prefix(id, '001'):
            self.cat_to_id[name]['001'] = info
        elif has_prefix(id, '002'):
            self.cat_to_id[name]['002'] = info
        else:
            print 'unknow cat name'

    def dump(self):
        for key in self.cat_to_id:
            id = self.cat_to_id[key]['id']
            if self.cat_to_id[key].has_key('parent_id'):
                parent_id = self.cat_to_id[key]['parent_id']
            else:
                parent_id = 0
            print key + ' id ' + str(id) + ' parent_id ' + str(parent_id)
    def get_dict(self):
        return self.cat_to_id

classify = Classify()
cat_to_id = classify.get_dict()

def html_to_text(unicode_string):
    info_dict = {
            u'&ensp;' : u' ',
            u'&emsp;' : u' ',
            u'&nbsp;' : u' ',
            u'&lt;' : u'<',
            u'&gt;' : u'>',
            u'&amp;' : u'&',
            u'&quot;' : u'"',
            u'&copy;' : u'©',
            u'&reg;' : u'®',
            u'&times;' : u'×',
            u'&divide;' : u'÷',
            }
    for key in info_dict:
        unicode_string = unicode_string.replace(key, info_dict[key])
    return unicode_string

class gen_time_from_string:

    @classmethod
    def match_string(self, date_str, i, total_len):
        time_str = [ u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9',
                u'-', u' ', u':', u'/', u',',
                u'秒钟前', u'分钟前', u'小时前',u'天前', u'个月前', u'年前',  
                u'年', u'月', u'日', u'上午', u'下午',
                u'今天', u'昨天', u'前天',
                ]
        end = False
        for sub_time_str in time_str:
            if i + len(sub_time_str) <= total_len:
                sub_str = date_str[i:i + len(sub_time_str)]
            else:
                continue
            if sub_str != sub_time_str:
                continue
            else:
                if sub_time_str == u'秒钟前' or sub_time_str == u'分钟前' or sub_time_str == u'小时前' or sub_time_str == u'天前' or sub_time_str == u'个月前' or sub_time_str == u'年前':
                    end = True
                return len(sub_time_str), end
        return 0, end

    @classmethod
    def get_valid_date_str(self, date_str):
        i = 0
        start = -1
        end = 0
        total_len = len(date_str)
        prev_match_len = 0
        max_match_len = 0
        max_match_string = None
        while i < total_len:
            match_len, is_end = self.match_string(date_str, i, total_len)
            if match_len > 0:
                if prev_match_len == 0:
                    start = -1
                if start < 0:
                    start = i
                end = i + match_len
                i = i + match_len
                prev_match_len = match_len
                if is_end:
                    break
            else:
                if prev_match_len > 0:
                    if max_match_len < end - start:
                        max_match_len = end - start
                        max_match_string = date_str[start:end]
                i = i + 1
                prev_match_len = match_len
        if start == -1:
            return None
        if max_match_len < end - start:
            max_match_len = end - start
            max_match_string = date_str[start:end]
        return max_match_string.strip()

    @classmethod
    def general_gen_time(self, date_str, time_format, no_log = False):
        if has_prefix(time_format, 'noyear_format_'):
            now_year = datetime.now().year
            new_date_str = str(now_year) + ' ' + date_str
            new_time_format = "%Y " + time_format[len('noyear_format_'):]
            return self.general_gen_time(new_date_str, new_time_format, no_log)
        elif has_prefix(time_format, 'text_format_'):
            new_date_str = self.get_valid_date_str(date_str)
            new_time_format = time_format[len('text_format_'):]
            #log.msg('text_format_ new_date_str [' + new_date_str.encode('utf8') + ']', level = log.DEBUG)
            return self.general_gen_time(new_date_str, new_time_format, no_log)
        elif has_prefix(time_format, 'before_format_'):
            info_dict = {
                    u'秒钟前' : 60,
                    u'分钟前' : 60,
                    u'小时前' : 3600,
                    u'天前' : 86400,
                    u'个月前' : 2592000,
                    u'年前' : 31536000,
                    }
            for key in info_dict:
                before_seconds = info_dict[key]
                index = date_str.find(key)
                if index >= 0:
                    seconds = int(date_str.replace(key, '')) * before_seconds
                    return int(time.time()) - seconds
            new_date_str = date_str
            new_time_format = time_format[len('before_format_'):]
            return self.general_gen_time(new_date_str, new_time_format, no_log)
        elif has_prefix(time_format, 'today_format_'):
            info_dict = {
                    u'今天' : 0,
                    u'昨天' : 1,
                    u'前天' : 2,
                    }
            for key in info_dict:
                index = date_str.find(key)
                before_days = info_dict[key]
                if index >= 0:
                    new_date_str = str(((datetime.now()) - timedelta(days=before_days)).date()) + ' ' + date_str[index + len(key):]
                    new_time_format = "%Y-%m-%d %H:%M"
                    return self.general_gen_time(new_date_str, new_time_format, no_log)
            new_date_str = date_str
            new_time_format = time_format[len('today_format_'):]
            return self.general_gen_time(new_date_str, new_time_format, no_log)
        else:
            #date_str=date_str.replace(u'')
            return self.gen_time(date_str, time_format, no_log)

    @classmethod
    def gen_time(self, date_str, time_format, no_log):
        zh_to_en = [
                ['星期一' , 'Mon'],
                ['星期二' , 'Tue'],
                ['星期三' , 'Wed'],
                ['星期四' , 'Thu'],
                ['星期五' , 'Fri'],
                ['星期六' , 'Sat'],
                ['星期日' , 'Sun'],
                ['十一月' , 'Nov'],
                ['十二月' , 'Dec'],
                ['一月' , 'Jan'],
                ['二月' , 'Feb'],
                ['三月' , 'Mar'],
                ['四月' , 'Apr'],
                ['五月' , 'May'],
                ['六月' , 'Jun'],
                ['七月' , 'Jul'],
                ['八月' , 'Aug'],
                ['九月' , 'Sep'],
                ['十月' , 'Oct'],
                ['年' , '-'],
                ['月' , '-'],
                ['日' , ' '],
                ['点' , ':'],
                ['分' , ' '],
                ['上午' , 'AM'],
                ['下午' , 'PM'],
                ['　', ' '],
                ['：', ':'],
                ]
        for key_value in zh_to_en:
            key = key_value[0]
            value = key_value[1]
            date_str = date_str.replace(key.decode('utf8'), value.decode('utf8'))
        try:
            date_str = date_str.replace(u'\xa0', u' ')
            gen_time = int(datetime.strptime(date_str.strip(), time_format).strftime("%s"))
        except:
            if no_log:
                return None
            exstr = traceback.format_exc()
            log.msg('failed to format time_str [' + date_str.encode('utf8') + '] time_format [' + time_format + '] '+ exstr, level = log.WARNING)
            return None
        return gen_time

def get_time_format(date_str):
    time_formats = [
        "%a, %d %b %Y %H:%M:%S +0800",
        "%a, %d %b %Y %H:%M:%S GMT",
        "before_format_",
        "before_format_today_format_%m %d %H:%M",
        "%d %b %Y",
        "noyear_format_%m-%d",
        "noyear_format_ (%m %d  %H:%M)",
        "noyear_format_ (%m/%d %H:%M)",
        "noyear_format_%m-%d  %H:%M",
        "noyear_format_%m-%d %H:%M",
        "noyear_format_%m/%d %H:%M",
        "text_format_before_format_noyear_format_%m-%d %H:%M",
        "text_format_before_format_today_format_no_year_format_%m-%d %H:%M",
        "text_format_before_format_%Y-%m-%d  -",
        "text_format_noyear_format_%m-%d %H:%M",
        "text_format_noyear_format_%m/%d %H:%M",
        "text_format_%Y-%m-%d",
        "text_format_%Y-%m-%d  %H",
        "text_format_%Y-%m-%d %H:%M",
        "text_format_%Y-%m-%d %H:%M,",
        "text_format_%Y-%m-%d %H:%M:%S",
        "text_format_%Y - %m - %d  , %p %I:%M,",
        "[%Y-%m-%d]",
        "%Y-%m-%d",
        "%Y.%m.%d",
        "[%Y %m %d %H:%M]",
        "[%Y-%m-%d %H:%M]",
        "[%Y-%m-%d%H:%M]",
        "%Y - %m - %d   %H:%M",
        "%Y %m %d %H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d   %p %I:%M",
        "text_format_%y/%m/%d",
    ]
    new_date_str = gen_time_from_string.get_valid_date_str(date_str)
    if not new_date_str:
        return None
    now_time = int(time.time())
    for time_format in time_formats:
        gen_time = gen_time_from_string.general_gen_time(new_date_str, time_format, no_log = True)
        if gen_time:
            interval = now_time - gen_time
            if interval < 365 * 3 * 86400 and interval > - 365 * 3 * 86400:
                log.msg('find format ' + time_format + ' gen_time ' + str(gen_time), level = log.DEBUG)
                return time_format
    return None

def get_longest_string(string_list):
    longest_string = None
    max_len = 0
    for string in string_list:
        if len(string) > max_len:
            max_len = len(string)
            longest_string = string
    return longest_string

def get_uniq_list(list):
    d = {}
    for item in list:
        id = hashlib.md5(item).hexdigest().upper()
        if d.has_key(id):
            log.msg("skip duplicate item " + item, level = log.DEBUG)
        d[id] = item

    new_list = []
    for id in d:
        new_list.append(d[id])
    return new_list

def get_uniq_list_from_base(list1, list2):
    d1 = {}
    d2 = {}
    for item in list1:
        id = hashlib.md5(item).hexdigest().upper()
        d1[id] = item

    for item in list2:
        id = hashlib.md5(item).hexdigest().upper()
        d2[id] = item
    new_list1 = []
    for id in d1:
        if not d2.has_key(id):
            new_list1.append(d1[id])
        else:
            log.msg("skip duplicate item from base " + item, level = log.DEBUG)
    return new_list1

class ExtractLib:

    @classmethod
    def is_title(self,maybe_title,content_title):
        #print 'maybe title','\t',maybe_title.encode('utf8')
        #print 'content title','\t',content_title.encode('utf8')

        title_dict = {}
        same_num = 0
        for i_str in maybe_title:
            title_dict[i_str] = 1
        for i_str in content_title:
            if i_str in title_dict:
                same_num += 1
                #if cur_title == title or title in cur_title or cur_title in title:
        #print same_num,len(maybe_title),len(content_title),float(same_num)/len(maybe_title),float(same_num)/len(content_title)
        if float(same_num)/len(maybe_title) > 0.6 or float(same_num)/len(content_title) > 0.6:
            title_match = True
        else:
            title_match = False
        return title_match

    @classmethod
    def get_content(self,url):
        rt_result = []
        dr = re.compile(r'<[^>]+>',re.S)
        html = urllib.urlopen(url).read()
        cur_title = Document(html).short_title().replace(' ','')
        readable_article = Document(html).summary()
        #print readable_article.encode('utf8')
        readable_article = readable_article.replace('&#13;','')
        cur_list = readable_article.replace('</p>','\n').split('\n')
        for item in cur_list:
            if '<img' in item and 'src=' in item:
                #print item.split('src=')[1].split('"')[1]
                dom = soupparser.fromstring(item)
                if len(dom) > 0:
                    img_path = dom[0].xpath('.//img')
                    for img in img_path:
                        rt_result.append(['0',img.get('src')])
            else:
                use_item = dr.sub('',item).replace(' ','')
                if len(use_item) > 10:
                    rt_result.append(['1',use_item])
        return cur_title,rt_result

def get_interval_str(seconds):
    if seconds < 60:
        return '%ss'%(seconds)
    elif seconds < 3600:
        return '%sm%ss'%(seconds/60, seconds%60)
    else:
        return '%sh%sm%ss'%(seconds/3600, (seconds%3600)/60, seconds%60)

if __name__ == '__main__':
    #get_cats_info('1', 'download.txt')
    #root_dict = build_cat_tree(['1', '2'])
    #map_dict = build_cat_total_map(root_dict)
    #for key in map_dict:
    #    print str(key) + ' -> ' + str(map_dict[key])
    #print str(get_root_cid())
    #cg = CategoryGet(['1', '2'])
    #cg.tranverse()
    #print str(get_prev_datetime(datetime.now() + timedelta(days = 365 + 10)))
    #print str(get_prev_datetime_str('2014-11-1'))
    #print str(get_prev_datetime_str('2013-11-1'))
    '''
    driver = create_firefox()
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)
    socket.setdefaulttimeout(60)
    get_url_by_browser(driver, 'http://tuan.yixun.com/?YTAG=2.15000805&_ut_=1389604167600')
    time.sleep(10)
    main_xpath = '//ul[@class="t_pub_list1 clearfix"]/li'
    li_obj_array = driver.find_elements_by_xpath(main_xpath)
    print 'li_obj_array ' + str(len(li_obj_array))
    html_source = driver.page_source
    write_file("www.amazon.cn.firefox2.html", html_source.encode('utf8'))
    driver_quit(driver)
    '''
    #pic_url = get_pic_url(get_id('http://a.m.tmall.com/i12465295391.htm?id=12465295391'))
    #id = get_id('http://a.m.taobao.com/i18965407241.htm?tg_key=jhs&juid=10000001874391')
    #print 'id ' + str(id)
    #pic_url = get_pic_url(get_id('http://a.m.taobao.com/i18965407241.htm?tg_key=jhs&juid=10000001874391'))
    #print 'pic_url ' + pic_url
    #print 'fen ' + str(get_float_str_to_fen(u'￥1,100.00'))
    #print_memory_usage()
    #l = []
    #for i in xrange(0, 50000000):
    #    l.append(i)
    #print_memory_usage()
    #dump_memory_usage()
    #parse_memory_usage('dump1391747498.41.txt')
    #time.sleep(100)
    #show_objgraph()
    #print get_pic_url(35466310345)
    print str(get_regex_value('http://a.m.tmall.com/i35466310345.htm?tg_key=jhs&juid=10000001963463', '(?<=a.m.tmall.com/i)\w+'))
