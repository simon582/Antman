#-*- coding:utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

with open('result.csv','r') as input_file, open('weibo_90.csv', 'w') as output_file:
    lines = input_file.readlines()
    for line in lines:
        res = line.split(',')
        birth = res[4]
        if len(birth) > 4:
            if birth[:3] == "199":
                try:
                    print >> output_file, line.strip().replace('\r','').replace('\n','').encode('gbk')
                except:
                    continue
