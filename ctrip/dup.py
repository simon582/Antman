#coding:utf-8

addr_list = []
with open('new_addr','r') as data_file:
    for line in data_file.readlines():
        line = line.strip()
        addr_list.append(line)

with open('rm_dup.csv','r') as in_file, open('out.csv','w') as out_file:
    lines = in_file.readlines()
    for line in lines:
        line = line.strip()
        cur_addr = line.split(',')[1]
        dup = False
        for addr in addr_list:
            if cur_addr.find(addr) != -1 or addr.find(cur_addr) != -1:
                dup = True
                print 'curr: ' + line
                print 'data: ' + addr
                break
        if dup == False:
            print >> out_file, line
