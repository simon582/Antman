#coding:utf-8

with open('city_list.back','r') as city_file, open('temp','r') as temp_file:
    city_list = city_file.readlines()
    temp_list = temp_file.readlines()

for city in city_list:
    city_name = city.strip().split(' ')[1]
    for temp in temp_list:
        if city_name == temp.strip():
            print city.strip()
