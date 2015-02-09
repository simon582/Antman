#! /usr/bin/env python
# -*- coding: utf-8 -*-
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

info_old = Table('content_db','info_old')

cursor = info_old.scan()
count = 0
rm_count = 0
for item in cursor:
    count += 1
    print 'current position: ' + str(count)
    if item.has_key('desc_img'):
        try:
            os.remove(curr_abs_path + '/' + item['desc_img'][3:])
            print 'remove desc_img: ' + item['desc_img']
            rm_count += 1
        except:
            print 'remove failed desc_img: ' + item['desc_img']
    if item.has_key('text'):
        for elem in item['text']:
            if elem[0] == '0':
                try:
                    os.remove(curr_abs_path + '/' + elem[1][3:])
                    print 'remove text img: ' + elem[1]
                    rm_count += 1
                except:
                    print 'remove failed text img: ' + elem[1]
print 'Removed ' + str(rm_count) + ' imgs successfully.'
