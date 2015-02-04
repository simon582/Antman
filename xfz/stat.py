#-*- coding:utf-8 -*-
import sys
import os
import time
reload(sys)
sys.setdefaultencoding('utf-8')
import pymongo
try:
    conn = pymongo.Connection('localhost',27017)
    info_table = conn.content_db.info2
    print 'Create mongodb connection successfully.'
except Exception as e:
    print e
    exit(-1)

customer_types = ['消费者','顾客','客户']
conflicts = ['投诉','索赔','投诉','状告','告上法庭','不满','恶劣','损害','误导','欺骗','欺诈','违法','曝光','危机','丑闻','质量问题','安全问题','道歉','召回','下架','处罚','罚款']
company_types = ['跨国企业','跨国公司']
company_names = ['3M','ABB','雅培','苹果公司','巴斯夫','拜耳','宝马','普利司通','佳能','家乐福','可口可乐','戴姆勒','达能','戴尔','杜邦','艾默生','福特','富士通','通用电气','通用汽车','日立','本田','现代汽车','英特尔','强生','卡夫','爱立信','LG','马自达','麦德龙','米其林','三菱','NEC','雀巢','尼桑','诺基亚','诺华','松下','百事','标致','辉瑞','宝洁','理光','罗氏','飞利浦','三星','夏普','索尼','铃木','乐购','东芝','丰田','联合利华','大众汽车','沃尔玛','施乐','惠普','西门子']

def write_csv(stat_dict, file_name):
    file = open(file_name, 'a')
    for company_name, prod in stat_dict.items():
        outline = company_name + ','
        for year in range(2002,2015):
            if year in prod:
                outline += str(prod[year]) + ','
            else:
                outline += '0,'
        print >> file, outline.encode('utf8')

def stat_1():
    stat_dict = {}
    cursor = info_table.find()
    for item in cursor:
        try:
            year = int(item['date'].split('-')[0])
            if stat_dict.has_key(year):
                stat_dict[year] += 1
            else:
                stat_dict[year] = 1
        except Exception as e:
            print e
            continue
    for year, cnt in stat_dict.items():
        print str(year) + ',' + str(cnt)

def stat_2():
    stat_dict = {}
    for company_type in company_types:
        stat_dict[company_type] = {}
    cursor = info_table.find()
    for item in cursor:
        for company_type in company_types:
            try:
                if company_type in item['title'] or company_type in item['text']:
                    year = int(item['date'].split('-')[0])
                    if stat_dict[company_type].has_key(year):
                        stat_dict[company_type][year] += 1
                    else:
                        stat_dict[company_type][year] = 1
            except Exception as e:
                print e
                continue
    write_csv(stat_dict, 'stat_2.csv')

def stat_3():
    stat_dict = {}
    for company_name in company_names:
        stat_dict[company_name] = {}
    cursor = info_table.find()
    for item in cursor:
        for company_name in company_names:
            try:
                if company_name in item['title'] or company_name in item['text']:
                    year = int(item['date'].split('-')[0])
                    if stat_dict[company_name].has_key(year):
                        stat_dict[company_name][year] += 1
                    else:
                        stat_dict[company_name][year] = 1
            except Exception as e:
                print e
                continue
    write_csv(stat_dict, 'stat_3.csv')


if __name__ == '__main__':
    stat_1()
    stat_2()
    stat_3()
        
