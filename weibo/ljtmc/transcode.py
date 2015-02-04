#-*- coding:utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

with open('result.csv','r') as input_file, open('weibo.csv', 'w') as output_file:
    lines = input_file.readlines()
    for line in lines:
        res = line.split(',')
        try:
            print >> output_file, line.strip().replace('\r','').replace('\n','').encode('gbk')
        except:
            continue
