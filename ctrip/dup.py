#coding:utf-8

hotel_dict = {}

with open('res_new.csv', 'r') as res_file:
    for line in res_file.readlines():
        name = line.split(',')[0] + line.split(',')[1]
        if not name in hotel_dict:
            hotel_dict[name] = 1
            print line.strip()
