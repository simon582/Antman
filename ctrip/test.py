#coding:utf-8
import re

with open('ori_addr','r') as file, open('new_addr','w') as out_file:
    lines = file.readlines()
    lines = list(set(lines))
    for line in lines:
        road = num = ""

        pos = line.find('路')
        if pos != -1:
            road = line[:pos]
            if road.find('区') != -1:
                road = road.split('区')[1]
            if road.find('市') != -1:
                road = road.split('市')[1]
            if road.find('县') != -1:
                road = road.split('县')[1]
            if road.find('镇') != -1:
                road = road.split('镇')[1]
            road += "路"

        if road == "":
            pos = line.find('街')
            if pos != -1:
                road = line[:pos]
                if road.find('区') != -1:
                    road = road.split('区')[1]
                if road.find('市') != -1:
                    road = road.split('市')[1]
                if road.find('县') != -1:
                    road = road.split('县')[1]
                if road.find('镇') != -1:
                    road = road.split('镇')[1]
                road += "街"

        if road == "":
            pos = line.find('大道')
            if pos != -1:
                road = line[:pos]
                if road.find('区') != -1:
                    road = road.split('区')[1]
                if road.find('市') != -1:
                    road = road.split('市')[1]
                if road.find('县') != -1:
                    road = road.split('县')[1]
                if road.find('镇') != -1:
                    road = road.split('镇')[1]
                road += "大道"    
    
        pos = line.find("号")
        if pos != -1:
            tmp = line[:pos]
            m = re.search(r'\d+', tmp)
            if m:
                num = m.group() + "号"
        #print line
        #print road
        #print num
        if road != "" and num != "":
            print >> out_file, road + num
        else:
            print >> out_file, line.strip()
