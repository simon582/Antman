#-*- coding:utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

hdict = {}
with open('result.csv','r') as input_file, open('yunda.csv', 'w') as output_file:
    lines = input_file.readlines()
    for line in lines:
        try:
            if line in hdict:
                continue
            hdict[line] = 1
            if line.split(',')[1].find('便民服务') != -1:
                continue
            print >> output_file, line.strip().replace(';',' ').replace('&nbsp',' ').replace('\r','').replace('\n','').encode('gbk')
        except:
            continue
