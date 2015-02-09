#!/usr/bin/python
#encoding=utf8
__author__ = 'luoyan@maimiaotech.com'


import sys
import os
import datetime

curr_path = os.path.dirname(__file__)
sys.path.append(os.path.join(curr_path,'../../'))
sys.path.append('../../spider/comm_lib')
import utils
from table import Table
import datetime
import logging
import logging.config
import traceback
import gc
if __name__ == '__main__':
    logging.config.fileConfig('../conf/consolelogger_build_index.conf')
logger = logging.getLogger(__name__)

BOSS_CONF_FILE = '/usr/local/BOSS/conf/boss.conf'
sys.path.append('/usr/local/BOSS/lib/')
from Boss4Python import Boss4Python
import datetime
import time

class WordSeg(object):
    def __init__(self):
        self.boss = Boss4Python()
        self.boss.init(BOSS_CONF_FILE)
    def do_segment(self,words):
        if isinstance(words,unicode):
            words = words.encode('utf-8')
        word_list= []
        result = self.boss.process(words, 1)
        for word in result:
            word_list.append(word)
        return word_list

class GetStringIndex:
    def __init__(self, string):
        self.string = string
        self.idx = 0
        #self.skip(' ')

    def skip(self, charactor):
        length = len(self.string)
        while self.idx < length:
            if self.string[self.idx] == charactor:
                self.idx = self.idx + 1
            else:
                return

    def get_string_idx(self, term):
        #self.skip(' ')
        length = len(term)
        start = self.idx
        end = self.idx + length
        if self.string[start:end] == term:
            idx = self.idx
            self.idx = self.idx + length
            return idx
        return -1
def decode_utf8(string):
    try:
        term = string.decode('utf8')
    except:
        exstr = traceback.format_exc()
        logger.warning('failed to decode ' + string + ' to utf8 ' + exstr)
        return None
    return term 

def get_desc(desc_list):
    desc = ""
    for sub_desc in desc_list:
        desc = desc + ' ' + sub_desc.strip()
    return desc.strip()

class GenIndex:
    def __init__(self, genall, is_new = False, recreate = False):
        self.genall = genall
        self.is_new = is_new
        self.recreate = recreate

    def save_index(self, term_doc_dict, cls):
        for term in term_doc_dict:
            doc_list = []
            for id in term_doc_dict[term]:
                for term_in_doc in term_doc_dict[term][id]:
                    doc_list.append(term_in_doc)
            term_info = {}
            term_info['term'] = term
            term_info['term_len'] = len(term)
            term_info['doc_list'] = doc_list
            cls.save(term_info, self.is_new)
            #del term_info

    def load_index(self, cls):
        term_doc_dict = {}
        cursor = cls.scan(is_new = self.is_new)
        item_list = []
        #print 'before load_index1 '
        #utils.print_memory_usage()
        for item in cursor:
            item_list.append(item)
        #print 'before load_index2 '
        #utils.print_memory_usage()

        count = 0
        for item in item_list:
            term = item['term']
            term_doc_dict[term] = {}
            for term_in_doc in item['doc_list']:
                id = term_in_doc['doc_id']
                if not term_doc_dict[term].has_key(id):
                    term_doc_dict[term][id] = []

                term_doc_dict[term][id].append(term_in_doc)
            count += 1
        
        #print 'before load_index3 ' + str(count)
        #utils.print_memory_usage()
        #print 'before load_index4 done'
        return term_doc_dict

    def get_item_value(self, item, key):
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
    def get_table_name(self, db):
        db_name = db.__class__.__name__
        if db_name == 'Table':
            db_name = db._db + '_' + db._coll
        elif db_name == 'type':
            db_name = db.__name__
        return db_name

    def base_gen_index(self, index_db, origin_db):
        db_name = self.get_table_name(origin_db)
        index_db_name = self.get_table_name(index_db)
        #print 'before load_index ' + index_db_name
        #utils.print_memory_usage()
        #term_doc_dict = self.load_index(index_db)
        term_doc_dict = {}
        #print 'after load_index ' + index_db_name
        #utils.print_memory_usage()
        cursor = origin_db.scan()
        end_time = int(time.time())
        no_time = 0
        total = 0
        display = 0
        no_valid_time = 0
        segmentor = WordSeg()
        for item in cursor:
            total = total + 1
            has_time, valid_time = self.is_valid_item(item, end_time)
            if not has_time:
                no_time = no_time + 1
                continue
            if not valid_time:
                no_valid_time = no_valid_time + 1
                continue
            try:
                display = display + 1
                if item.has_key('title'):
                    info = 'title ' + self.get_item_value(item, 'title').strip() + ' id ' + item['id']
                    logger.debug(info.encode('utf8'))
                self.segment_word(segmentor, item, term_doc_dict)
            except:
                exstr = traceback.format_exc()
                logger.warning('failed to segment ' + exstr)
                continue
        if self.recreate:
            logger.info('start to drop')
            index_db.drop()
            logger.info('end to drop')
        logger.info('start to save_index')
        #print 'before save_index ' + index_db_name
        #utils.print_memory_usage()
        self.save_index(term_doc_dict, index_db)
        #print 'after save_index ' + index_db_name
        #utils.print_memory_usage()
        logger.info('end to save_index')
        logger.debug('db_name ' + db_name + ' index_db_name ' + index_db_name + ' total ' + str(total) + ' no_time ' + str(no_time) + ' no_valid_time ' + str(no_valid_time) + ' display ' + str(display))
        #del term_doc_dict
        #gc.collect()

    def is_valid_item(self, item, end_time):
        has_time = True
        valid_time = True
        return has_time, valid_time

    def base_segment_word(self, segmentor, item, string, term_doc_dict, id, string_type):
        string = string.lower()
        gsi = GetStringIndex(string)
        logger.debug(string_type + ' ' + string.encode('utf8'))
        word_list = segmentor.do_segment(string)
        word_list_str = ""
        word_seg_info_list = []
        #if term_doc_dict.has_key(id):
            #return
        for word in word_list:
            term = decode_utf8(word.split('\1')[0])
            if not term:
                return
            word_type = word.split('\1')[1]
            idx = gsi.get_string_idx(term)
            #logger.debug('idx ' + str(idx))
            word_seg_info = {'word_type': word_type, 'idx': idx, 'doc_id': id, 'string_type': string_type}
            self.handle_word_seg_info(word_seg_info, item)
            word_seg_info_list.append(word_seg_info)
            if not term_doc_dict.has_key(term):
                term_doc_dict[term] = {}
            if not term_doc_dict[term].has_key(id):
                term_doc_dict[term][id] = []
            term_doc_dict[term][id].append(word_seg_info)
            word_list_str = word_list_str + ', ' + term.encode('utf8') #+ ' ' + word_type
        logger.debug('seg ' + word_list_str)
        return

    def base_dump(self, index_db, origin_db):
        cursor = index_db.scan(self.is_new)
        for item in cursor:
            for doc in item['doc_list']:
                info = 'db ' + origin_db.__name__ + ' '+ item['term'] + ' ' + 'string type ' + doc['string_type'] + ' id ' + doc['doc_id'] + ' idx ' + str(doc['idx'])
                if doc.has_key('feed_in'):
                    info = info + ' feed_in ' + str(doc['feed_in'])
                logger.debug(info)
                continue
                origin_db_cursor = origin_db.query(doc['doc_id'])
                if not origin_db_cursor:
                    info = info + ' None'
                    logger.debug(info)
                    continue
                title = ''
                if origin_db_cursor.has_key('title'):
                    title = self.get_item_value(origin_db_cursor, 'title').strip()
                desc = ''
                if origin_db_cursor.has_key('desc'):
                    desc_list = origin_db_cursor['desc']
                    desc = get_desc(desc_list)

                if origin_db_cursor.has_key('link'):
                    link = origin_db_cursor['link']
                elif origin_db_cursor.has_key('go_link'):
                    link = origin_db_cursor['go_link']
                else:
                    link = ''

                if origin_db_cursor.has_key('display_time_end'):
                    time_second = (origin_db_cursor['display_time_end'])
                    time_str = str(datetime.datetime.utcfromtimestamp(time_second))
                else:
                    time_str = ''

                info = info + ' title [' + title + '] desc [' + desc + '] link '+ link + ' time ' + time_str
                logger.debug(info)

    def handle_word_seg_info(self, word_seg_info, item):
        pass

class ContentDBGenIndex(GenIndex):

    def __init__(self, genall, is_new, recreate):
        GenIndex.__init__(self, genall, is_new, recreate)
        self.origin_db = Table('content_db', 'info')
        self.index_db = Table('content_index', 'info', 'term')
    
    def is_valid_item(self, item, end_time):
        has_time = True
        valid_time = True
        if not item.has_key('stat'):
            return False, False
        if item['stat'] != utils.STAT_USE:
            return False, False
        return has_time, valid_time

    def gen_index(self):
        self.base_gen_index(self.index_db, self.origin_db)

    def segment_word(self, segmentor, item, term_doc_dict):
        if item.has_key('title'):
            self.base_segment_word(segmentor, item, item['title'].strip(), term_doc_dict, item['id'], 'title')
        elif item.has_key('desc'):
            self.base_segment_word(segmentor, item, item['desc'].strip(), term_doc_dict, item['id'], 'desc')

    def dump(self):
        self.base_dump(self.index_db, self.origin_db)
    
    def handle_word_seg_info(self, word_seg_info, item):
        word_seg_info['pub_time'] = item['pub_time']
        word_seg_info['score'] = item['score']
        word_seg_info['cat'] = item['cat']
        word_seg_info['crawl_source'] = item['crawl_source']
        word_seg_info['location'] = item['location']
        if item.has_key('yunying'):
            word_seg_info['yunying'] = item['yunying']

default_url = '/static/upload_images/badimg.png'

def gen_idx(genall=False, is_new=False, recreate = False):
    gi = ContentDBGenIndex(genall, is_new, recreate)
    gi.gen_index()

def usage(argv0):
    print argv0 + ' ' + 'gen'
    print argv0 + ' ' + 'gennew'
if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage(sys.argv[0])
        sys.exit(-1)
    if sys.argv[1] == 'gen':
        gen_idx()
    elif sys.argv[1] == 'gennew':
        gen_idx(is_new=True)
    else:
        usage(sys.argv[0])
        sys.exit(-1)
