#-*- coding:utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

for parent, dirnames, filenames in os.walk('csv/'):
    for filename in filenames:
        print filename
        if filename.find('csv') != -1:
            with open('csv/' + filename) as input_file, open('ascii/' + filename, 'w') as output_file:
                lines = input_file.readlines()
                for line in lines:
                    print >> output_file, line.strip().encode('gbk', 'ignore')
                
