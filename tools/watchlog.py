#!/usr/bin/python
# encoding=utf-8
# Filename: watchlog.py
# author: shaoxinqi@maimiaotech.com
import os
import signal
import subprocess
import time
import sys
curr_path = os.path.dirname(__file__)
curr_file_path = os.path.abspath(__file__)
curr_abs_path = curr_file_path[0:curr_file_path.rfind("/")]
sys.path.append(os.path.join(curr_path,'../../'))
sys.path.append(os.path.join(curr_path,'../../spider/comm_lib'))
import utils
from table import Table

test_file = "../log/transform.log"
running_table = Table("job_list","running",uniq_key='job_id')
current_log = {}

def update_current_log():
    cursor = running_table.scan()
    for job_id in current_log.keys():
        if running_table.query(job_id) == None:
            del(current_log[job_id])
   
    for item in cursor:
        log_item = {}
        job_id = item['job_id']
        if current_log.has_key(job_id):
            continue
        log_file = job_id + '.err'
        log_path = curr_abs_path + '/log/'
        log_cursor = open(log_path + log_file)
        log_item['log_cursor'] = log_cursor
        current_log[job_id] = log_item
    
    #print current_log
 
def watch_log(job_id, log_item):
    while True:
        readbuf = log_item['log_cursor'].readline()
        if not readbuf:
            break
        print job_id.encode('utf8') + ' ' + readbuf,

if __name__ == '__main__':
    update_current_log()
    while True:
        for job_id in current_log.keys():
            watch_log(job_id, current_log[job_id])
        time.sleep(5)
        update_current_log()
