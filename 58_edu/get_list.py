#coding:utf-8
import os
crawled_list = []
for parent, dirnames, filenames in os.walk('result/'):
    for filename in filenames:
        crawled_list.append(filename.split('.')[0])

with open('city_list.back','r') as city_file:
    city_list = city_file.readlines()

cdict = {}
for city in crawled_list:
    cdict[city.strip()] = 1

for city in city_list:
    name = city.strip().split(' ')[1]
    if not name in cdict:
        print city.strip()    
