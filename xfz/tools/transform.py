#-*- coding:utf-8 -*-
import pymongo
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

company_types = ['跨国企业','跨国公司']
company_names = ['3M','ABB','雅培','苹果公司','巴斯夫','拜耳','宝马','普利司通','佳能','家乐福','可口可乐','戴姆勒','达能','戴尔','杜邦','艾默生','福特','富士通','通用电气','通用汽车','日立','本田','现代汽车','英特尔','强生','卡夫','爱立信','LG','马自达','麦德龙','米其林','三菱','NEC','雀巢','尼桑','诺基亚','诺华','松下','百事','标致','辉瑞','宝洁','理光','罗氏','飞利浦','三星','夏普','索尼','铃木','乐购','东芝','丰田','联合利华','大众汽车','沃尔玛','施乐']

try:
    conn = pymongo.Connection('localhost',27017)
    info_table = conn.content_db.info2
except Exception as e:
    print e
    exit(-1)

def add(key, prod):
    if key in prod:
        return prod[key].replace(',',' ').replace('\t','').replace('\n','').replace('\r','').replace('&nbsp','').strip() + ','
    else:
        return ','
def crawl_1():
    cursor = info_table.find()
    file = open('crawl_stat_1.csv','a')
    for item in cursor:
        if item['text'] == "":
            continue
        outline = ""
        outline += add('baseword',item)
        outline += add('date',item)
        outline += add('title',item)
        outline += add('text',item)
        try:
            print >> file, outline.encode('gbk')
            print 'write successfully ' + item['id']
        except:
            continue

def crawl_2():
    cursor = info_table.find()
    file = open('crawl_stat_2.csv','a')
    for item in cursor:
        if item['text'] == "":
            continue
        res_list = []
        for elem in company_types:
            if item['title'].find(elem) != -1:
                res_list.append(elem)
            elif item['text'].find(elem) != -1:
                res_list.append(elem)
        if len(res_list) == 0:
            continue
        outline = ""
        for res in res_list:
            outline += res + ' '
        outline += ','
        outline += add('baseword',item)
        outline += add('date',item)
        outline += add('title',item)
        outline += add('text',item)
        try:
            print >> file, outline.encode('gbk')
            print 'write successfully ' + item['id']
        except:
            continue

def crawl_3():
    cursor = info_table.find()
    file = open('crawl_stat_3.csv','a')
    for item in cursor:
        if item['text'] == "":
            continue
        res_list = []
        for elem in company_names:
            if item['title'].find(elem) != -1:
                res_list.append(elem)
            elif item['text'].find(elem) != -1:
                res_list.append(elem)
        if len(res_list) == 0:
            continue
        outline = ""
        for res in res_list:
            outline += res + ' '
        outline += ','
        outline += add('baseword',item)
        outline += add('date',item)
        outline += add('title',item)
        outline += add('text',item)
        try:
            print >> file, outline.encode('gbk')
            print 'write successfully ' + item['id']
        except:
            continue

if __name__ == "__main__":
    type = int(sys.argv[1])
    if type == 1:
        crawl_1()
    elif type == 2:
        crawl_2()
    elif type == 3:
        crawl_3()
