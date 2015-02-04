#-*- coding:utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

with open('modoer_subject.csv','r') as in1_file, open('modoer_subject_shops.csv','r') as in2_file, open('modoer_subject_gbk.csv', 'w') as out1_file, open('modoer_subject_shops_gbk.csv','w') as out2_file:
    in1_lines = in1_file.readlines()
    in2_lines = in2_file.readlines()
    for i in range(min(len(in2_lines),len(in1_lines))):
        try:
            line1 = in1_lines[i].encode('gbk','ignore').strip()
            line2 = in2_lines[i].encode('gbk','ignore').strip()
            print >> out1_file, line1
            print >> out2_file, line2
        except:
            continue
