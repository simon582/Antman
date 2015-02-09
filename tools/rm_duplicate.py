#-*- coding:utf-8 -*-
import sys
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

# extract the whole text from text_list
def text_list_to_str(text_list):
    count = 0
    info = ''
    for item in text_list:
        if item[0] == '1':
            info = info + 'p' + str(count) + ' ' + item[1] + '\n'
            count += 1
    return info

# get the max length sentence and return its hash_code
def get_long_sign_for_text_list(prod_item):
    max_len = 0
    max_sentence = ''
    if prod_item.has_key('title'):
         max_sentence = prod_item['title'].strip().strip(' ')
         max_len = len(max_sentence)
    for item in prod_item['text']:
        if item[0] == '1':
            try:
                para = item[1].strip().strip(' ')
            except:
                print "Cannot get paragraph"
            sentences = para.split(u'。')
            for s in sentences:
                if max_len < len(s):
                    max_len = len(s)
                    max_sentence = s
    if max_sentence:
        hash_code = hashlib.md5(max_sentence.encode('utf8')).hexdigest().upper()
        return hash_code
    return None

# main function
def get_long_sign_and_remove(table, max_item, realmod):
    not_access_table = Table('content_db', 'not_access')
    cursor = table.scan()
    hash_dict = {}
    count = 0
    weibo_num = 0
    realmod_num = 0
    change_num = 0
    desc_change_num = 0
    # get the long sign for each item
    for item in cursor:
        if item.has_key('stat') and item['stat'] == 1:
            continue
        if item.has_key('crawl_source') and item['crawl_source'] == u"运营添加":
            continue
        if item.has_key('type') and item['type'] == 2:
                weibo_num += 1
        if max_item > 0 and count > max_item:
            break
        count += 1
        if item.has_key('text'):
            hash_code = get_long_sign_for_text_list(item)
            if not hash_code:
                print 'Cannot get hash_code: ' + str(item['id'])
                continue
            if not hash_dict.has_key(hash_code):
                hash_dict[hash_code] = []

            hash_dict[hash_code].append(item)
            #print 'sign ' + str(hash_code) + ' ' + str(item['id'])
    uniq_num = 0
    dup_num = 0
    # save duplicate record and remove data
    for hash_code in hash_dict:
        if len(hash_dict[hash_code]) > 1:
            uniq_num += 1
            dup_num += len(hash_dict[hash_code])
            info = ""
            max_length = None
            max_item = None
            # find max length text item
            for item in hash_dict[hash_code]:
                url = ""
                if item.has_key('crawl_url'):
                    url = item['crawl_url']
                info = info + " id " + item['id'] + ' url ' + url + ' crawl_source ' + item['crawl_source']
                length = utils.get_article_len(item['text'])
                if not max_length:
                    max_length = length
                    max_item = item
                elif max_length < length:
                    max_length = length
                    max_item = item
            print 'hash_code ' + str(hash_code) + info.encode('utf8')
            
            # create duplicate dict
            if not max_item.has_key('duplicate'):
                max_item['duplicate'] = {}
            for item in hash_dict[hash_code]:
                change_num += 1
                if item['id'] != max_item['id']:
                    max_item['duplicate'][item['id']] = item['crawl_url']
                    # update not_access table
                    not_access_table.save({'id': item['id']})
                    print ('remove ' + " id " + item['id']).encode('utf8')
                    if realmod == 1:
                        table.remove(item)
                        realmod_num += 1
            # update duplicate list
            if realmod == 1:
                table.save(max_item)
            #print ('max item: ' + str(max_item))
        
    print 'total ' + str(count)  + ' change ' + str(change_num) + ' realmod ' + str(realmod_num) + ' weibo_num ' + str(weibo_num) + ' desc_change_num ' + str(desc_change_num) + ' uniq_num ' + str(uniq_num) + ' dup_num ' + str(dup_num)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print 'arg error'
        sys.exit(-1)
    max_item = int(sys.argv[1])
    realmod = int(sys.argv[2])
    db_name = sys.argv[3]
    table_name = sys.argv[4]
    get_long_sign_and_remove(Table(db_name, table_name), max_item, realmod)

