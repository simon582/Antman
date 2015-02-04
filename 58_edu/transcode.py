#-*- coding:utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

for parent, dirnames, filenames in os.walk('result/'):
    for filename in filenames:
        print filename
        hdict = {}
        if filename.find('csv') != -1:
            with open('result/' + filename) as input_file, open('gbk/' + filename, 'w') as output_file:
                lines = input_file.readlines()
                for line in lines:
                    tel = line.strip().split(',')[6]
                    if tel not in hdict:
                        hdict[tel] = 1
                        res = line.strip().split(',')
                        res[1] = res[1].replace(' ', ',')
                        line = ""
                        for part in res:
                            line += part + ','
                        print >> output_file, line.strip().encode('gbk', 'ignore')
