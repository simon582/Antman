# -*- coding:utf-8 -*-

patch_cnt = 0
with open('res_nodup.csv', 'r') as res_file:
    for line in res_file.readlines():
        try:
            res = line.split(',')
            if res[3] == '' and res[4] == '' and res[5] == '' and res[6] == '':
                patch_cnt += 1
                #continue
                print line.strip()
        except:
            continue
