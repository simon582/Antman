#-*- coding:utf-8 -*-
dict = ""
with open('crawled','r') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        dict += line

with open('code.conf','r') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if dict.find(line) != -1:
            continue
        print line
