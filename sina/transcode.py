#-*- coding:utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

with open('result.csv','r') as input_file, open('sina.csv', 'w') as output_file:
    lines = input_file.readlines()
    for line in lines:
        try:
            print >> output_file, line.strip().replace('&nbsp',' ').replace('\r','').replace('\n','').encode('gbk')
        except:
            continue
