#! /usr/bin/env python
# -*- coding: utf-8 -*-
#encoding=utf8
__author__ = 'luoyan@maimiaotech.com'


import sys
import os
import datetime

curr_path = os.path.dirname(__file__)
sys.path.append(os.path.join(curr_path,'../../'))
sys.path.append(os.path.join(curr_path,'../../spider/comm_lib'))
sys.path.append(os.path.join(curr_path,'../../classify/'))
import utils
from table import Table
import datetime
import hashlib
import logging
import logging.config
import traceback
import socket
import time
from shangpin_classify_lib import ShangpinPredictCat
class GenCat:
    def __init__(self):
        cat_dir='../../classify/'
        self.predict_cat = ShangpinPredictCat(cat_dir + 'query_term_cat', cat_dir + 'cat_name', cat_dir + 'shangpin_cat')
        self.predict_cat.Init()
    #def __init__(self,term_cat_file,taobao_cat_file,maimiao_cat_file):
    def handle(self, item, start_url_info):
        cat_name = start_url_info['cat']
        type_id = utils.type_to_id[start_url_info['type']]
        if type_id != utils.TYPE_GOODS:
            if not utils.cat_to_id.has_key(cat_name) or not utils.cat_to_id[cat_name].has_key('002'):
                print (cat_name + ' not found ').encode('utf8')
                return
            item['cat'] = utils.cat_to_id[cat_name]['002']['id']
        else:
            item['cat'] = self.predict_cat.Predict(item)
