import sys
import os
import hashlib
def load_file(file, col_num, col_key):
    f = open(file, 'r')
    d = {}
    id_list = []
    while True:
        buffer = f.readline()
        if not buffer:
            break;
        values = buffer.split()
        key = values[col_key]
        num = int(values[col_num])
        id = hashlib.md5(key).hexdigest().upper()
        d[id] = {'num' : num, 'values' : values}
        id_list.append(id)
    return d, id_list

def join(fileA, fileB, col_num_A, col_num_B, col_key_A, col_key_B):
    dictA, id_listA = load_file(fileA, col_num_A, col_key_A)
    dictB, id_listB = load_file(fileB, col_num_B, col_key_B)
    d = {}
    id_list = []
    for key in id_listA:
        numA = dictA[key]['num']
        numB = 0
        if dictB.has_key(key):
            numB = dictB[key]['num']
        num = numA + numB
        d[key] = {}
        d[key]['numA'] = numA
        d[key]['numB'] = numB
        d[key]['num'] = num
        d[key]['values'] = dictA[key]['values']
        id_list.append(key)
        
    for key in id_listB:
        if dictA.has_key(key):
            continue
        print 'not skip'
        numB = dictB[key]['num']
        numA = 0
        num = numA + numB
        d[key] = {}
        d[key]['numA'] = numA
        d[key]['numB'] = numB
        d[key]['num'] = num
        d[key]['values'] = dictA[key]['values']
        id_list.append(key)

    for key in id_list:
        info = ''
        for i in xrange(len(d[key]['values'])):
            if i != col_num_B:
                info = info + d[key]['values'][i] + ' '
            else:
                info = info + str(d[key]['num']) + ' ' + str(d[key]['numA']) + ' ' + str(d[key]['numB']) + ' '
        print info

def diff(fileA, fileB, col_num_A, col_num_B, col_key_A, col_key_B):
    dictA, id_listA = load_file(fileA, col_num_A, col_key_A)
    dictB, id_listB = load_file(fileB, col_num_B, col_key_B)
    d = {}
    id_list = []
    for key in id_listA:
        numA = dictA[key]['num']
        numB = 0
        if dictB.has_key(key):
            numB = dictB[key]['num']
        num = numB - numA
        d[key] = {}
        d[key]['numA'] = numA
        d[key]['numB'] = numB
        d[key]['num'] = num
        d[key]['values'] = dictA[key]['values']
        id_list.append(key)
        
    for key in id_listB:
        if dictA.has_key(key):
            continue
        print 'not skip'
        numB = dictB[key]['num']
        numA = 0
        num = numB - numA
        d[key] = {}
        d[key]['numA'] = numA
        d[key]['numB'] = numB
        d[key]['num'] = num
        d[key]['values'] = dictB[key]['values']
        id_list.append(key)

    for key in id_list:
        info = ''
        for i in xrange(len(d[key]['values'])):
            if i != col_num_B:
                info = info + d[key]['values'][i] + ' '
            else:
                delta = d[key]['num']
                str_delta = str(delta)
                if delta > 0:
                    str_delta = '+' + str_delta
                info = info + str(d[key]['numB']) + ' ' + str_delta + ' '
        print info

def show_help(argv0):
    print argv0 + " join A B col_num_A col_num_B col_key_A col_key_B"
    print argv0 + " diff A B col_num_A col_num_B col_key_A col_key_B"

if __name__ == "__main__":
    if len(sys.argv) != 8:
        show_help(sys.argv[0])
        sys.exit(-1)
    if sys.argv[1] == 'join':
        join(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]))
    elif sys.argv[1] == 'diff':
        diff(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]))
