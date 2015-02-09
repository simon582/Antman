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
import datetime
import hashlib
import logging
import logging.config
import traceback
import socket
import time
import random
import cStringIO, urllib2, Image
#logging.config.fileConfig('../conf/consolelogger_transform.conf')
STAT_NOT_CHANGE=0
STAT_CHANGE=1
STAT_NOT_ACCESS=2
STAT_COPY=3
if __name__ == '__main__':
    logging.config.fileConfig('../conf/consolelogger_transform.conf')
logger = logging.getLogger(__name__)

def load_dict(file_name):
    if os.path.exists(file_name):
        file = open(file_name)
        d = {}
        while True:
            buffer = file.readline()
            if not buffer:
                break
            key = buffer.strip()
            if key:
                d[key] = 1
        return d
    return None

def load_cat_map(file_name):
    if os.path.exists(file_name):
        file = open(file_name)
        d = {}
        classify = utils.Classify('../comm_lib/cat.txt')
        cat_to_id_old = classify.get_dict()
        success = True
        while True:
            buffer = file.readline()
            if not buffer:
                break
            if buffer[0] == '#':
                continue
            key = buffer.strip()
            columns = key.split(' ')
            old_crawl_source = columns[0].decode('utf8')
            crawl_source = columns[1].decode('utf8')
            old_cat = columns[2].decode('utf8')
            cat = columns[3].decode('utf8')
            if cat_to_id_old.has_key(old_cat) and cat_to_id_old[old_cat].has_key('002'):
                old_cat_id = cat_to_id_old[old_cat]['002']['id']
            elif utils.cat_to_id.has_key(cat) and utils.cat_to_id[cat].has_key('002'):
                logger.warning('skip already new cat ' + cat)
                continue
            else:
                logger.warning('cannot find old cat [' + old_cat.encode('utf8') + '] line = [' + key + ']')
                sucess = False
            if utils.cat_to_id.has_key(cat) and utils.cat_to_id[cat].has_key('002'):
                cat_id = utils.cat_to_id[cat]['002']['id']
                if len(cat_id) < 9:
                    logger.warning('new cat is not level 2 ' + cat.encode('utf8') + ' line = [' + key + ']')
            else:
                logger.warning('cannot find new cat ' + cat.encode('utf8') + ' line = [' + key + ']')
                sucess = False
            if utils.cat_to_id.has_key(cat) and utils.cat_to_id[cat].has_key('002'):
                d[old_crawl_source] = [crawl_source, old_cat_id, cat_id]
        if not success:
            return None
        return d
    return None

def load_conf(filePath):
    file = open(filePath)
    display_name_info = {}
    display_name_info_dict = {}
    while True:
        buffer = file.readline()
        if not buffer:
            break
        if buffer[0] == '#':
            continue
        if utils.has_prefix(buffer, 'start_url') and display_name_info.has_key('display_name'):
            display_name = display_name_info['display_name']
            display_name_info_dict[display_name] = display_name_info
            display_name_info = {}
        content = buffer.strip()
        equal = content.find('=')
        if equal == -1:
            continue
        key = content[:equal]
        value = content[equal + 1:]
        if key != None:
            display_name_info[key] = value
        #if key == 'reserve_days':
           # logger.debug('reserve_days: ' + value)
    if display_name_info.has_key('display_name'):
        display_name = display_name_info['display_name']
        display_name_info_dict[display_name] = display_name_info
    return display_name_info_dict
    
class Transform:
    def __init__(self):
        self.function_list = []
        self.not_acces_table = Table('content_db', 'not_access')
        #self.driver = utils.create_firefox()
        #self.driver.set_page_load_timeout(60)
        #self.driver.set_script_timeout(60)
        socket.setdefaulttimeout(60)
        self.today=datetime.datetime.now().strftime('%Y-%m-%d')
        self.img_dir='/home/ops/appimg/'+self.today+'/'
        self.prefix='appimg/'+self.today+'/'
        self.func_list=[self.handle_desc_img, self.handle_text, self.handle_go_link_simple, self.handle_remove_go_link, self.handle_remove_short_article, self.handle_remove_crawl_desc_img, self.handle_mark_stat_use, self.handle_remove_empty_title_and_empty_desc, self.handle_gen_loc_code, self.handle_gen_score, self.handle_add_desc_img, self.handle_store_price, self.handle_recognize_link, self.handle_trans_good]
        self.info_table = Table('content_db', 'info')
        self.info_old_table = Table('content_db', 'info_old')
        self.region_table = Table('baseinfo', 'region', 'name')
        self.goods_table = Table('goods_db', 'info')
        self.id_dict = load_dict('id.list')        
        self.crawl_source_dict = load_cat_map('old2new_cat.txt')
        self.display_name_conf_dict = load_conf('../uniform/start_url_info_new.conf')
        self.neg_article_filter = ['002102003', '002114001', '002115001', '002108002'] 
    def set_func_list(self, func_list_str):
        func_str_array = func_list_str.split(',')
        self.func_list = []
        func_map = {
                'handle_desc_img' : self.handle_desc_img,
                'handle_text' : self.handle_text,
                'handle_go_link_simple' : self.handle_go_link_simple,
                'handle_go_link' : self.handle_go_link,
                'handle_remove_go_link' : self.handle_remove_go_link,
                'handle_remove_short_article' : self.handle_remove_short_article,
                'handle_remove_crawl_desc_img' : self.handle_remove_crawl_desc_img,
                'handle_mark_stat_use' : self.handle_mark_stat_use,
                'handle_rm_old_data' : self.handle_rm_old_data,
                'handle_auto_online_goods' : self.handle_auto_online_goods,
                'handle_pre_pub' : self.handle_pre_pub,
                'handle_remove_empty_title_and_empty_desc' : self.handle_remove_empty_title_and_empty_desc,
                'handle_gen_desc' : self.handle_gen_desc,
                'handle_show_img' : self.handle_show_img,
                'handle_show_title' : self.handle_show_title,
                'handle_sync_goods' : self.handle_sync_goods,
                'handle_gen_loc_code' : self.handle_gen_loc_code,
                'handle_gen_crawl_desc_img' : self.handle_gen_crawl_desc_img,
                'handle_mv_desc_img' : self.handle_mv_desc_img,
                'handle_trans_cat' : self.handle_trans_cat,
                'handle_rm_too_new_data' : self.handle_rm_too_new_data,
                'handle_gen_score' : self.handle_gen_score,
                'handle_add_desc_img' : self.handle_add_desc_img,
                'handle_rm_link_in_text' : self.handle_rm_link_in_text,
                'handle_store_price' : self.handle_store_price,
                'handle_trans_good' : self.handle_trans_good,
                'handle_recognize_link' : self.handle_recognize_link
                }
        for func_str in func_str_array:
            if func_map.has_key(func_str):
                self.func_list.append(func_map[func_str])
            else:
                logger.error('failed to find func ' + func_str)

    def same_table(self, src, dest):
        if src._db == dest._db and src._coll == dest._coll:
            return True
        return False

    def scan(self, table, dest_table, max_item, realmod, markdel, tot_block, cur_block):
        is_same_table = self.same_table(table, dest_table)
        cursor = table.scan()
        item_list = []
        for item in cursor:
            if (int(item['id'], 16) % tot_block + 1 == cur_block):
                item_list.append(item)
        count = 0
        realmod_num = 0
        change_num = 0
        copy_num = 0
        not_access_num = 0
        for item in item_list:
            if max_item > 0 and count >= max_item:
                break
            count += 1
            stat = self.handle(item)
            if stat == STAT_CHANGE or stat == STAT_COPY:
                if stat == STAT_CHANGE:
                    change_num += 1
                else:
                    copy_num += 1
                if realmod == 1:
                    if is_same_table:
                        table.save(item)
                    else:
                        dest_table.save(item)
                        if stat == STAT_CHANGE:
                            table.remove(item)
                    realmod_num += 1
            elif stat == STAT_NOT_ACCESS:
                if realmod == 1:
                    d = {}
                    for key in ['id', 'not_access_reason', 'crawl_source', 'crawl_url', 'pub_time']:
                        if item.has_key(key):
                            d[key] = item[key]
                    self.not_acces_table.save(d)
                    if not item.has_key('new_good') and item.has_key('desc_img'):
                        try:
                            os.remove('/home/ops/' + item['desc_img'])
                            logger.info('remove desc_img: ' + item['desc_img'])
                        except:
                            logger.warning('remove failed desc_img: ' + item['desc_img'])
                    if not item.has_key('new_good') and item.has_key('text'):
                        for elem in item['text']:
                            if elem[0] == '0':
                                try:
                                    os.remove('/home/ops/' + elem[1])
                                    logger.info('remove text img: ' + elem[1])
                                except:
                                    logger.warning('remove failed text img: ' + elem[1])
                    if markdel == 1:
                        item['stat'] = utils.STAT_DELETE
                        if is_same_table:
                            table.save(item)
                        else:
                            dest_table.save(item)
                            table.remove(item)
                    else:
                        table.remove(item)
                not_access_num += 1
        logger.info('total ' + str(count)  + ' change ' + str(change_num) + ' realmod ' + str(realmod_num) + ' not access num ' + str(not_access_num) + ' copy ' + str(copy_num))

    def handle(self, item):
        res_stat = STAT_NOT_CHANGE
        for func in self.func_list:
            stat = func(item)
            if stat == STAT_NOT_ACCESS:
                return stat
            if stat == STAT_CHANGE or stat == STAT_COPY:
                res_stat = stat
        return res_stat
    
    def quit(self):
        utils.driver_quit(self.driver)
    
    def handle_go_link_simple(self, item):
        if item.has_key('crawl_go_link'):
            url = item['crawl_go_link']
            if not utils.has_prefix(url, 'http://'):
                info = 'warning ignore ' + url
                logger.warning(info)
                item['not_access_reason'] = info
                return STAT_NOT_ACCESS
            item['go_link'] = url
            return STAT_CHANGE
        else:
            return STAT_NOT_CHANGE

    def handle_remove_go_link(self, item):
        if item['type'] == utils.TYPE_GOODS and (not item.has_key('crawl_go_link')):
            info = 'id ' + item['id']  + ' no crawl_go_link'
            logger.debug(info)
            item['not_access_reason'] = info
            return STAT_NOT_ACCESS
        else:
            return STAT_NOT_CHANGE

    def handle_remove_crawl_desc_img(self, item):
        if item['type'] == utils.TYPE_GOODS and (not item.has_key('crawl_desc_img')):
            info = 'id ' + item['id'] + ' no crawl_desc_img '
            logger.debug(info)
            item['not_access_reason'] = info
            return STAT_NOT_ACCESS
        elif item['type'] == utils.TYPE_GOODS and (not item.has_key('desc_img')):
            info = 'id ' + item['id'] + ' no desc_img '
            logger.debug(info)
            item['not_access_reason'] = info
            return STAT_NOT_ACCESS
        else:
            return STAT_NOT_CHANGE

    def handle_go_link(self, item):
        if item.has_key('crawl_go_link'):
            url = item['crawl_go_link']
            if not utils.has_prefix(url, 'http://'):
                info = 'warning ignore ' + url
                logger.debug(info)
                item['not_access_reason'] = info
                return STAT_NOT_ACCESS
            if utils.get_url_by_browser_for_times(self.driver, url, 3):
                time.sleep(1)
                current_url = utils.get_current_url(self.driver)
                if not current_url:
                    info = 'failed to get ' + url
                    logger.debug(info)
                    item['not_access_reason'] = info
                    return STAT_NOT_ACCESS
                info = str(item['crawl_go_link'])
                item['go_link'] = current_url
                info = info + ' -> ' + str(item['go_link'])
                logger.debug('change ' + info)
                return STAT_CHANGE
            else:
                info = 'failed to get url ' + url
                logger.debug(info)
                item['not_access_reason'] = info
                return STAT_NOT_ACCESS
        else:
            return STAT_NOT_CHANGE
    def handle_desc_img(self, item):
        if item.has_key('crawl_desc_img'):
            url = item['crawl_desc_img']
            if not utils.has_prefix(url, 'http://'):
                info = 'id ' + item['id'] + ' warning ignore ' + url
                logger.debug(info)
                item['not_access_reason'] = info
                return STAT_NOT_ACCESS
            if item['crawl_source'] == u'试客联盟':
                d = utils.resize_img_url(url, [60], self.img_dir, self.prefix, fix_width = False)
            elif item['type'] == utils.TYPE_GOODS:
                d = utils.resize_img_url(url, [130], self.img_dir, self.prefix, fix_width = False)
            #街拍分类
            elif item['cat'] == '002102006':
                d = utils.resize_img_url(url, [600], self.img_dir, self.prefix, fix_width = False)
            else:
                d = utils.resize_img_url(url, [250], self.img_dir, self.prefix, fix_width = False)
            if not d:
                info = 'id ' + item['id'] + ' failed to resize img url ' + url
                logger.debug(info)
                item['not_access_reason'] = info
                return STAT_NOT_ACCESS
            if item['type'] == utils.TYPE_GOODS and d.has_key('60x60'):
                img_file = d['60x60']
                item['desc_img'] = img_file
                logger.debug('id ' + item['id'] + ' success to resize img ' + img_file)
                return STAT_CHANGE
            elif item['type'] == utils.TYPE_GOODS and d.has_key('130x130'):
                img_file = d['130x130']
                item['desc_img'] = img_file
                logger.debug('id ' + item['id'] + ' success to resize img ' + img_file)
                return STAT_CHANGE
            elif item['cat'] == '002102006' and d.has_key('600x600'):
                img_file = d['600x600']
                item['desc_img'] = img_file
                logger.debug('id ' + item['id'] + ' success to resize img ' + img_file)
                return STAT_CHANGE 
            elif item['type'] != utils.TYPE_GOODS and d.has_key('250x250'):
                img_file = d['250x250']
                item['desc_img'] = img_file
                logger.debug('id ' + item['id'] + ' success to resize img ' + img_file)
                return STAT_CHANGE
            else:
                info = 'id ' + item['id'] + ' failed to resize img url for no key ' + url
                logger.debug(info)
                item['not_access_reason'] = info
                return STAT_NOT_ACCESS
        else:
            return STAT_NOT_CHANGE

    def handle_text(self, item):
        if item.has_key('crawl_text'):
            crawl_text = item['crawl_text']
            text = []
            for i in range(len(crawl_text)):
                for j in range(i+1, len(crawl_text)):
                    if i >= len(crawl_text) or j >= len(crawl_text):
                        break
                    if crawl_text[i][0] != crawl_text[j][0]:
                        continue
                    if crawl_text[i][1] == crawl_text[j][1]:
                        info =  'delete duplicated par:' + str(crawl_text[i]) + ' ' + str(crawl_text[j])
                        logger.debug(info)    
                        del crawl_text[j]

            for elem in crawl_text:
                if elem[0] == '0':
                    if item['crawl_source'] == u'试客联盟':
                        continue
                    if item['type'] == 1:
                        continue
                    img_url = elem[1]
                    d = utils.resize_img_url(img_url,[480], self.img_dir, self.prefix, fix_width = True, size_th = 100)
                    if not d:
                        info = 'failed to resize img url ' + img_url.encode('utf8')
                        logger.debug(info)
                        item['not_access_reason'] = info
                        return STAT_NOT_ACCESS
                    if d.has_key('480x480'):
                        img_file = d['480x480']
                        text.append(['0', img_file])
                else:
                    if item['type'] == utils.TYPE_WEIBO and elem[1].find("http://") != -1:
                        info = 'There is a http link in weibo text. id: ' + item['id']
                        logger.debug(info)
                        item['not_access_reason'] = info
                        return STAT_NOT_ACCESS
                    text.append(elem)
            item['text'] = text
            return STAT_CHANGE
        else:
            return STAT_NOT_CHANGE
    
    def handle_remove_short_article(self, item):
        if item['type'] == utils.TYPE_GOODS:
            return STAT_NOT_CHANGE
        for neg_cat in self.neg_article_filter:
            if item['cat'] == neg_cat:
                return STAT_NOT_CHANGE
        if not item.has_key('crawl_text'):
            info = 'id ' + item['id'] + ' no crawl_text'
            logger.debug(info)
            item['not_access_reason'] = info
            return STAT_NOT_ACCESS
        length = utils.get_article_len(item['crawl_text'])
        if item['type'] != utils.TYPE_GOODS and length < 30:
            info = 'id ' + item['id'] + ' crawl_text too short ' + str(length)
            logger.debug(info)
            item['not_access_reason'] = info
            return STAT_NOT_ACCESS
        else:
            return STAT_NOT_CHANGE
    
    def handle_mark_stat_use(self, item):
        if not item.has_key('stat'):
            info = 'id ' + item['id'] + ' no stat'
            logger.debug(info)
            item['not_access_reason'] = info
            return STAT_NOT_ACCESS
        if item['type'] != utils.TYPE_GOODS and item['stat'] == utils.STAT_NEW:
            logger.debug('id ' + item['id'] + ' stat new -> use ')
            item['stat'] = utils.STAT_USE
            return STAT_CHANGE
        else:
            return STAT_NOT_CHANGE
    
    def handle_auto_online_goods(self, item):
        if item.has_key('stat') and item['stat'] == utils.STAT_USE and item['type'] == utils.TYPE_GOODS and item.has_key('cur_price') and item['cur_price'] > 6000:
            item['stat'] = utils.STAT_NEW
            logger.debug('id ' + item['id'] + ' cur_price is ' + str(item['cur_price']) + ' bigger than 60 yuan ')
            return STAT_CHANGE
        return STAT_NOT_CHANGE

    def handle_rm_old_data(self, item):
        if (not item.has_key('type')) or (not item.has_key('pub_time')):
            info = "no type or pub_time: " + item['id']
            logger.warning(info)
            item['not_access_reason'] = info
            return STAT_NOT_ACCESS
        #控制上线商品不自动下线
        #if item['type'] == utils.TYPE_GOODS and item['stat'] == 1:
            #return STAT_NOT_CHANGE
        #只对feed进行操作 不对banner操作
        if item['type'] == utils.TYPE_GOODS and item['stat'] == 1 and item.has_key('ad_type') and item['ad_type'] == 1:
            return STAT_NOT_CHANGE
        threshold_day = 0
        item['crawl_source'] = item['crawl_source'].encode('utf8')
        if self.display_name_conf_dict.has_key(item['crawl_source']):
            if self.display_name_conf_dict[item['crawl_source']].has_key('reserve_days') and self.display_name_conf_dict[item['crawl_source']]['reserve_days']!='':
                #logger.debug('crawl_source: ' + item['crawl_source'] + ' reserve_days: ' + self.display_name_conf_dict[item['crawl_source']]['reserve_days'])
                threshold_day = int(self.display_name_conf_dict[item['crawl_source']]['reserve_days'])
        # 有reserve_days或者是GOODS或者是NEWS才继续处理
        if item['type'] != utils.TYPE_GOODS and item['type'] != utils.TYPE_NEWS and threshold_day == 0:
            return STAT_NOT_CHANGE
        if item['cat'] = '001012002':
            threshold_day = 15
        if threshold_day == 0:
            threshold_day = 7
        delta_time = time.time() - item['pub_time']
        one_day_second = 86400
        #logger.debug('id: ' + item['id'] + ' type: ' + str(item['type']) + ' delta_time: ' + str(delta_time / one_day_second) + ' Res_days:' + str(threshold_day))
        if delta_time > one_day_second * threshold_day:
            info = 'id: ' + item['id'] + ' is too old to be deleted. item time:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['pub_time']))
            logger.debug(info)
            self.info_old_table.save(item)
            item['not_access_reason'] = info
            return STAT_NOT_ACCESS
        return STAT_NOT_CHANGE

    def handle_pre_pub(self, item):
        now_time = int(time.time())
        if item.has_key('stat') and item['stat'] == utils.STAT_WAIT_ONLINE and item.has_key('pre_pub_time') and item['pre_pub_time'] <= now_time:
            item['stat'] = utils.STAT_USE
            logger.debug('id ' + item['id'] + ' pre_pub')
            return STAT_CHANGE
        return STAT_NOT_CHANGE

    def handle_gen_desc(self, item):
        if item.has_key('crawl_text') and not item.has_key('desc'):
            desc = None
            for text_item in item['crawl_text']:
                if text_item[0] == '1':
                    if not desc:
                        desc = text_item[1]
                    else:
                        desc = desc + text_item[1]
                    if len(desc) > 70:
                        break
            if desc:
                item['desc'] = desc
                logger.debug('id ' + item['id'] + ' gen desc [' + desc + ']')
                return STAT_CHANGE
        return STAT_NOT_CHANGE

    def handle_remove_empty_title_and_empty_desc(self, item):
        if (not item.has_key('title') or len(item['title'].strip()) == 0) and (not item.has_key('desc') or len(item['desc'].strip()) == 0):
            info = 'id ' + item['id'] + ' no title and no desc'
            logger.debug(info)
            item['not_access_reason'] = info
            return STAT_NOT_ACCESS
        else:
            return STAT_NOT_CHANGE

    def handle_show_img(self, item):
        if item.has_key('desc_img'):
            print 'id ' + item['id'] + ' desc_img ' + str(item['desc_img'])
        if item.has_key('text'):
            for text_item in item['text']:
                if text_item[0] == '0':
                    print 'id ' + item['id'] + ' text_img ' + str(text_item[1])
        return STAT_NOT_CHANGE
    
    def handle_show_title(self, item):
        if item.has_key('title'):
            print ('id ' + item['id'] + ' title [' + item['title'] + ']').encode('utf8')
        else:
            print ('id ' + item['id'] + ' None').encode('utf8')
        if item.has_key('title') and item.has_key('text') and not item.has_key('desc'):
            print ('id ' + item['id'] + ' no desc crawl_source ' + item['crawl_source']).encode('utf8')
        return STAT_NOT_CHANGE

    def handle_sync_goods(self, item):
        if item.has_key('type') and item['type'] == utils.TYPE_GOODS:
            self.handle_show_img(item)
            return STAT_COPY
        return STAT_NOT_CHANGE

    def handle_gen_loc_code(self, item):
        if item.has_key('location'):
            return STAT_NOT_CHANGE
        if item.has_key('crawl_location'):
            location = item['crawl_location'].encode('utf8')
            suffix_list = ['','市','县','区','州','岛','省']
            for suffix in suffix_list:
                ret = self.region_table.query(location + suffix)
                if ret:
                    print ('code:' + str(ret['id']) + ' location: ' + location + ' suffix: ' + suffix)
                    item['location'] = str(ret['id'])
                    return STAT_CHANGE 
        print ('location = 0 ' + ' id ' + item['id'])
        item['location'] = str(0)
        return STAT_CHANGE
    
    def handle_gen_score(self, item):
        if item.has_key('score'):
            return STAT_NOT_CHANGE
        item['score'] = 0
        print ('score = 0 ' + ' id ' + item['id'])
        return STAT_CHANGE

    def gen_desc_img(self, prod, text_attr, desc_img_attr):
        if prod.has_key(text_attr) and not prod.has_key(desc_img_attr):
            desc_img = None
            for text_item in prod[text_attr]:
                if text_item[0] == '0':
                    try:
                        buffer = urllib2.urlopen(text_item[1])
                        tmpIm = cStringIO.StringIO(buffer.read())
                        im = Image.open(tmpIm)
                        (x,y) = im.size
                        if x < 300 or y < 300:
                            continue    
                        desc_img = text_item[1]
                        break
                    except:
                        logger.error('Cannot download image:' + text_item[1] + ' id:' + prod['id'])
            if desc_img:
                prod[desc_img_attr] = desc_img
                logger.debug('id ' + prod['id'] + ' gen ' + desc_img_attr + ' ' + desc_img.encode('utf8'))
                return STAT_CHANGE
            else:
                logger.debug('id ' + prod['id'] + ' no pic to gen ' + desc_img_attr + ' ')
        return STAT_NOT_CHANGE
    
    def handle_gen_crawl_desc_img(self, item):
        ret = self.gen_desc_img(item, 'crawl_text', 'crawl_desc_img')
        if ret == STAT_CHANGE:
            return self.handle_desc_img(item)
        return ret

    def handle_mv_desc_img(self, item):
        if self.id_dict and self.id_dict.has_key(item['id']):
            if item.has_key('crawl_desc_img'):
                del item['crawl_desc_img']
            if item.has_key('desc_img'):
                del item['desc_img']
            logger.debug('id ' + item['id'] + ' remove crawl_desc_img desc_img')
            return STAT_CHANGE
        return STAT_NOT_CHANGE
    
    def handle_trans_cat(self, item):
        if self.crawl_source_dict:
            cat = item['cat']
            level2 = (len(cat) >= 9)
            if utils.has_prefix(cat, '002'):
                if utils.has_prefix(cat, '0020') or len(cat) < 9:
                    type = 'old'
                    if not utils.has_prefix(cat, '0020') and len(cat) < 9:
                        type = 'new'
                    old_crawl_source = item['crawl_source']
                    if not self.crawl_source_dict.has_key(old_crawl_source):
                        logger.warning(('id ' + item['id'] + ' ' + type + ' cat ' + cat + ' level2 ' + str(level2) + ' no map for crawl_source ' + old_crawl_source).encode('utf8'))
                        return STAT_NOT_CHANGE
                    item['crawl_source'] = self.crawl_source_dict[old_crawl_source][0]
                    item['cat'] = self.crawl_source_dict[old_crawl_source][2]
                    logger.debug(('id ' + item['id'] + ' ' + type + ' cat ' + cat + ' level2 ' + str(level2) + ' -> ' + item['cat'] + ' crawl_souce ' + old_crawl_source + ' -> ' + item['crawl_source']).encode('utf8'))
                    return STAT_CHANGE
                #elif len(cat) < 9:
                #    logger.warning(('id ' + item['id'] + ' new cat ' + cat + ' level2 ' + str(level2) + ' crawl_source ' + item['crawl_source'] + ' not level 2').encode('utf8'))
                else:
                    logger.debug(('id ' + item['id'] + ' new cat ' + cat + ' level2 ' + str(level2) + ' crawl_source ' + item['crawl_source']).encode('utf8'))
        return STAT_NOT_CHANGE

    def handle_rm_too_new_data(self, item):
        now_time = int(time.time())
        if item['pub_time'] > now_time:
            info = 'id ' + item['id'] + ' pub_time ' + str(item['pub_time'])
            logger.debug(info)
            item['not_access_reason'] = info
            return STAT_NOT_ACCESS
        return STAT_NOT_CHANGE

    def handle_add_desc_img(self, item):
        if item.has_key('desc_img'):
            return STAT_NOT_CHANGE
        #两性健康分类
        if item['cat'] != '002111002':
            return STAT_NOT_CHANGE
        fangshiimg = curr_abs_path + '/img/defaultimg/fangshi/resize'
        list = os.listdir(fangshiimg)
        filenum = len(list)
        item['desc_img'] = 'appimg/defaultimg/fangshi/resize/' + str(random.randint(0, filenum-1)) + '.png'
        item['text'].insert(0, ['0',item['desc_img']])
        print 'id: ' + item['id'] + ' add desc_img: ' + item['desc_img']
        return STAT_CHANGE

    def handle_rm_link_in_text(self, item):
        if item['type'] != utils.TYPE_WEIBO:
            return STAT_NOT_CHANGE
        for elem in item['text']:
            if elem[0] == '1' and elem[1].find("http://") != -1:
                info = 'There is a http link in weibo text. id: ' + item['id']
                logger.debug(info)
                logger.debug(elem[1])
                item['not_access_reason'] = info
                return STAT_NOT_ACCESS
        return STAT_NOT_CHANGE

    def handle_store_price(self, item):
        if item['type'] != utils.TYPE_GOODS:
            return STAT_NOT_CHANGE
        if not item.has_key('cur_price'):
            return STAT_NOT_CHANGE
        if not item.has_key('good_id'):    
            return STAT_NOT_CHANGE
        ret = self.info_table.query(item['id'])
        if ret and ret.has_key('old_price'):
            if len(ret['old_price']) > 0:
                item['old_price'] = ret['old_price']
                if item['cur_price'] != item['old_price'][-1]:
                    item['old_price'].append(item['cur_price'])
                else:
                    return STAT_NOT_CHANGE
        else:
            item['old_price'] = [item['cur_price']]
        info = 'item: ' + item['id'] + ' update new price: ' + str(item['cur_price'])
        logger.debug(info)
        return STAT_CHANGE

    def handle_trans_good(self, item):
        if item['type'] != utils.TYPE_GOODS:
            return STAT_NOT_CHANGE
        self.goods_table.save(item)
        info = 'Transform good into goods_db: ' + item['id']
        logger.debug(info)
        item['not_access_reason'] = info
        item['new_good'] = True
        return STAT_NOT_ACCESS
            
    def handle_recognize_link(self, item):
        if item['type'] != utils.TYPE_GOODS:
            return STAT_NOT_CHANGE
        if item.has_key('go_link'):
            if item['go_link'].find('taobao') != -1 or item['go_link'].find('tmall') != -1 or item['go_link'].find('jhs') != -1:
                item['b2c_source'] = 'taobao'
        
        if not item.has_key('b2c_source'):
            item['b2c_source'] = ''
        return STAT_CHANGE

def usage(argv0):
    print argv0 + ' db_name src_table_name dest_table_name run/run_test maxitem markdel=1/0 [func_list=[handle_desc_img,handle_text,handle_go_link_simple,remove_go_link,handle_rm_old_data, handle_auto_online_goods, handle_pre_pub, handle_gen_desc, handle_remove_empty_title_and_empty_desc, handle_gen_loc_code, handle_gen_score, handle_add_desc_img]] tot_block cur_block'

if __name__ == '__main__':
    if len(sys.argv) > 11 or len(sys.argv) < 8:
        usage(sys.argv[0])
        sys.exit(-1)
    #slice = int(sys.argv[3])
    #partition_num = int(sys.argv[4])
    src_db_name = sys.argv[1]
    src_table_name = sys.argv[2]
    dest_db_name = sys.argv[3]
    dest_table_name = sys.argv[4]
    cmd = sys.argv[5]
    maxitem = int(sys.argv[6])
    markdel = int(sys.argv[7])
    if cmd == 'run_test':
        mod = False
    elif cmd == 'run':
        mod = True
    else:
        usage(sys.argv[0])
        sys.exit(-1)

    t = Transform()
    tot_block = 1
    cur_block = 1
    if len(sys.argv) == 9 or len(sys.argv) == 11:
        func_str_list = sys.argv[8]
        t.set_func_list(func_str_list)
    if len(sys.argv) == 10:
        tot_block = int(sys.argv[8])
        cur_block = int(sys.argv[9])
    if len(sys.argv) == 11:
        tot_block = int(sys.argv[9])
        cur_block = int(sys.argv[10])
    t.scan(Table(src_db_name, src_table_name), Table(dest_db_name, dest_table_name), maxitem, mod, markdel, tot_block, cur_block)
    #t.quit()
