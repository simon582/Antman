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
import utils
from table import Table
import datetime
import hashlib
import logging
import logging.config
import traceback
import socket
import time
import threading
if __name__ == '__main__':
    logging.config.fileConfig('../conf/consolelogger_spider_schedule.conf')
logger = logging.getLogger(__name__)

def usage(argv0):
    print argv0 + ' conf_file'

def generate_time(date_str, time_format):
    try:
        gen_time = int(datetime.datetime.strptime(date_str.strip(), time_format).strftime("%s"))
    except:
        exstr = traceback.format_exc()
        log.msg('failed to format time_str [' + date_str.encode('utf8') + '] time_format [' + time_format + '] '+ exstr, level = log.WARNING)
        return None
    return gen_time

class Job:
    def __init__(self, job_id, command, stdout, stderr, start_url):
        self.pid = -1
        self.job_id = job_id
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.start_url = start_url
        self.queue_time = -1
        self.waiting_time_sec = -1
        self.run_time_sec = -1
        self.priority = 0

    def start(self):
        job_starter = JobStarter(self, 'crawl_' + self.job_id)
        job_starter.start()
        pid_command = 'ps aux|grep \'%s\'|grep -v grep | awk \'{print $2}\'|head -n 1'%(self.command)
        output = os.popen(pid_command)
        pid_str = output.read()
        logger.debug('get pid [%s]'%(pid_str.strip()))
        try:
            pid = int(pid_str)
            logger.debug('start pid %d'%(pid))
            self.pid = pid
        except:
            exstr = traceback.format_exc()
            logger.warning('failed error message ' + exstr)

    def start_process(self):
        command = 'cd ../uniform/;%s>>%s 2>>%s'%(self.command, self.stdout, self.stderr)
        os.system(command)

    def check(self):
        check_command = 'ps aux|grep \'%s\'|grep -v grep | awk \'{print $1}\'|wc -l'%(self.command)
        output = os.popen(check_command)
        check_str = output.read()
        try:
            check_num = int(check_str)
            logger.debug('check_num %d'%(check_num))
        except:
            exstr = traceback.format_exc()
            logger.warning('failed error message ' + exstr)
        return check_num

class JobStarter(threading.Thread):
    def __init__(self, job, threadName):
        super(JobStarter, self).__init__(name = threadName)
        self.job = job
        #self.lock = lock

    def run(self):
        self.job.start_process()

class Scheduler:
    def gen_job_list(self, start_url_job_dict):
        output = os.popen('ps aux|grep start_url=|grep max_item|grep python|grep -v grep|awk -f ps_cmd.awk')
        d = {}
        while True:
            buffer = output.readline()
            if not buffer:
                break
            array = buffer.strip().split()
            pid = int(array[0])
            start_url = None
            max_item = None
            max_pages = None
            job_id = None
            for i in xrange(len(array)):
                if utils.has_prefix(array[i], 'start_url='):
                    start_url = array[i][len('start_url='):]
                elif utils.has_prefix(array[i], 'max_item='):
                    max_item = int(array[i][len('max_item='):])
                elif utils.has_prefix(array[i], 'max_pages='):
                    max_pages = int(array[i][len('max_pages='):])
                elif utils.has_prefix(array[i], 'job_id='):
                    job_id = array[i][len('job_id='):]
            if start_url and max_item and max_pages and job_id:
                logger.debug('gen_job_list start_url %s max_item %d max_pages %d job_id %s', start_url, max_item, max_pages, job_id)
                start_url_job = start_url_job_dict[start_url]
                d[start_url] = self.gen_job(start_url_job, job_id)
        return d

    def __init__(self, conf_name):
        self.job_list = {
                "running":{},
                "done":{},
                "pending":{}
                }
        self.start_url_info_dict = utils.load_conf(['../uniform/start_url_info_new.conf','../uniform/start_url_info_soufun.conf'])
        self.start_url_job_dict = self.load_conf(conf_name)
        self.job_pending_list = []
        self.job_list['running'] = self.gen_job_list(self.start_url_job_dict)
        self.job_list_db = {
                'pending': Table('job_list', 'pending', 'job_id'),
                'running': Table('job_list', 'running', 'job_id'),
                'done': Table('job_list', 'done', 'job_id')
                }
        self.max_slots = 10

    def load_conf(self, file_name):
        '''
        #min hour * * * max_item max_pages url
        start_time end_time interval command
        '''
        d = {}
        file = open(file_name, 'r')
        while True:
            buffer = file.readline()
            if not buffer:
                break
            if buffer[0] == '#':
                continue
            array = buffer.strip().split()
            #date_str = str(datetime.datetime.now())[:10]
            #start_time_str = date_str + ' ' + array[0] + ':00'
            #end_time_str = date_str + ' ' + array[1] + ':00'
            #start_time = generate_time(start_time_str, '%Y-%m-%d %H:%M:%S'
            #end_time = generate_time(end_time_str, '%Y-%m-%d %H:%M:%S'
            start_time_str = array[0]
            end_time_str = array[1]
            interval = int(array[2])
            max_item = int(array[3])
            max_pages = int(array[4])
            start_url_conf = array[5]
            start_url = array[6]
            if not self.start_url_info_dict.has_key(start_url):
                continue
            if self.start_url_info_dict[start_url].has_key('score'):
                score = self.start_url_info_dict[start_url]['score']
            else:
                score = 2
            #print 'url: ' + start_url + ' score: ' + str(score)
            #cmd_idx = len(start_time) + 1 + len(end_time) + 1 + len(interval) + 1 + 
            #command = buffer.strip()[cmd_idx:]
            #print "start_time %d end_time %d interval %d max_item %d max_pages %d start_url %s"%(start_time, end_time, interval, max_item, max_pages, start_url)
            id = hashlib.md5(start_url).hexdigest().upper()
            start_urls_file = 'conf/start_urls.' + id
            file2 = open(start_urls_file, 'w')
            file2.write(start_url)
            file2.close()
            d[start_url] = {
                'start_url':start_url,
                'start_time_str':start_time_str,
                'end_time_str':end_time_str,
                'interval':interval,
                'max_item':max_item,
                'max_pages':max_pages,
                'start_url_conf':start_url_conf,
                'start_urls_file':start_urls_file,
                'score':score,
                }
        return d

    def gen_job_id(self, start_time, start_url):
        id = hashlib.md5(start_url).hexdigest().upper()
        time_format = '%Y%m%d%H%M'
        start_time_str = datetime.datetime.fromtimestamp(start_time).strftime(time_format)
        job_id = start_time_str + '_' + id
        logger.debug('start_time %s start_url %s -> job_id %s'%(start_time, start_url, job_id))
        return job_id

    def get_run_time(self, start_url_job):
        start_time_str = start_url_job['start_time_str']
        end_time_str = start_url_job['end_time_str']
        interval = start_url_job['interval']
        date_str = str(datetime.datetime.now())[:10]
        start_time = generate_time(date_str + ' ' + start_time_str + ':00', '%Y-%m-%d %H:%M:%S')
        end_time = generate_time(date_str + ' ' + end_time_str + ':00', '%Y-%m-%d %H:%M:%S')
        now_time = int(time.time())
        if now_time < start_time or now_time > end_time:
            return None
        N = (end_time - start_time)/(interval * 60)
        run_time = start_time + interval * 60 * N
        return run_time

    def gen_job(self, start_url_job, job_id):
        start_url = start_url_job['start_url']
        start_url_conf = start_url_job['start_url_conf']
        start_urls_file = start_url_job['start_urls_file']
        stdout = '/dev/null'
        stderr = '../tools/log/' + job_id + '.err'
        command = 'scrapy crawl uniform -a start_urls_file=../tools/%s -a max_item=%d -a max_pages=%d -a job_id=%s -a conf=%s'%(start_urls_file, start_url_job['max_item'], start_url_job['max_pages'], job_id, start_url_conf)
        job = Job(job_id, command, stdout, stderr, start_url)
        return job

    def queue_job(self, start_url_job, run_time, job_id):
        #logger.info('start job_id ' + job_id)
        job = self.gen_job(start_url_job, job_id)
        job.queue_time = int(time.time())
        self.job_list['pending'][job_id] = job

    def start_job(self, job):
        check_num = job.check()
        if check_num == 0:
            job.start()
            return True
        return False

    def calc_priority(self):
        for job_id in self.job_list['pending']:
            job = self.job_list['pending'][job_id]
            job.waiting_time_sec = int(time.time()) - job.queue_time
            job.priority = int(job.waiting_time_sec / 900) + self.start_url_job_dict[job.start_url]['score']           
        self.job_pending_list = sorted(self.job_list['pending'].items(), key=lambda d:d[1].priority, reverse=True)
        #for item in self.job_pending_list:
            #job_id = item[0]
            #job = item[1]
            #print job.start_url + ' score:' + str(job.priority)

    def scan_pending(self):
        del_job_id_list = []
        for item in self.job_pending_list:
            job_id = item[0]
            job = item[1]
            if len(self.job_list['running']) >= self.max_slots:
                break
            if self.start_job(job):
                self.job_list['running'][job_id] = job
                job.waiting_time_sec = int(time.time()) - job.queue_time
                del_job_id_list.append(job_id)

        for job_id in del_job_id_list:
            del self.job_list['pending'][job_id]

    def scan_running(self):
        del_job_id_list = []
        for job_id in self.job_list['running']:
            job = self.job_list['running'][job_id]
            check_num = job.check()
            job.run_time_sec = int(time.time()) - job.queue_time - job.waiting_time_sec
            if check_num == 0 or job.run_time_sec > (3600 * 5):
                self.job_list['done'][job_id] = job
                del_job_id_list.append(job_id)

        for job_id in del_job_id_list:
            del self.job_list['running'][job_id]

    def has_job(self, job_id_to_search):
        for list_name in ['pending', 'running', 'done']:
            for job_id in self.job_list[list_name]:
                if self.job_list[list_name].has_key(job_id_to_search):
                    return True
        return False

    def show_job_list(self):
        for list_name in ['pending', 'running', 'done']:
            for job_id in self.job_list[list_name]:
                job = self.job_list[list_name][job_id]
                logger.debug("job_id %s status %s pid %d command [%s]"%(job.job_id, list_name, job.pid, job.command))

    def save(self):
        for list_name in ['pending', 'running']:
            cursor = self.job_list_db[list_name].scan()
            old_items = {}
            for item in cursor:
                old_items[item['job_id']] = item

            new_items = {}
            for job_id in self.job_list[list_name]:
                new_items[job_id] = self.job_list[list_name][job_id].__dict__

            del_items = {}
            for key in old_items:
                if not new_items.has_key(key):
                    del_items[key] = old_items[key]

            for job_id in new_items:
                self.job_list_db[list_name].save(new_items[job_id])

            for job_id in del_items:
                self.job_list_db[list_name].remove(del_items[job_id])

        for list_name in ['done']:
            for job_id in self.job_list[list_name]:
                self.job_list_db[list_name].save(self.job_list[list_name][job_id].__dict__)

        
    def loop(self):
        while True:
            logger.debug('start check')
            for start_url in self.start_url_job_dict:
                start_url_job = self.start_url_job_dict[start_url]
                run_time = self.get_run_time(start_url_job)
                if run_time:
                    job_id = self.gen_job_id(run_time, start_url)
                    if self.has_job(job_id):
                        continue
                    else:
                        self.queue_job(start_url_job, run_time, job_id)
            logger.debug('end check')
            self.calc_priority()
            self.scan_pending()
            self.scan_running()
            self.show_job_list()
            self.save()
            time.sleep(10)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage(sys.argv[0])
        sys.exit(-1)
    conf_file = sys.argv[1]
    sched = Scheduler(conf_file)
    sched.loop()
