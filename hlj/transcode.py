#-*- coding:utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

for parent, dirnames, filenames in os.walk('result/'):
    for filename in filenames:
        print filename
        if filename.find('csv') != -1:
            with open('result/' + filename, 'r') as input_file, open('gbk/' + filename, 'w') as output_file:
                lines = input_file.readlines()
                for line in lines:
                    print >> output_file, line.strip().encode('gbk', 'ignore')
