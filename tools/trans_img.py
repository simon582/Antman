#-*- coding:utf-8 -*-
# author:shaoxinqi@maimiaotech.com
import sys
import os
import datetime
curr_path = os.path.dirname(__file__)
curr_file_path = os.path.abspath(__file__)
sys.path.append(os.path.join(curr_path,'../../'))
sys.path.append(os.path.join(curr_path,'../comm_lib'))
from table import Table
import utils
import datetime
import hashlib
import logging
import traceback
RESIZE_SUCCESS = 1
RESIZE_FAIL_SMALL = -1
RESIZE_FAIL_TRANS = -2

def transdir(imgdir, size):
    filenum = 0
    try:
        list = os.listdir(imgdir)
    except:
        print "Donot exist image dir: " + imgdir
        return
    for line in list:
        filepath = os.path.join(imgdir, line)
        if os.path.isdir(filepath):
            continue
        elif os.path:
            if filepath.find("jpg") or filepath.find("jpeg") or filepath.find("png"):
                output_file_name = str(filenum) + '.png'
                if utils.resize_img(filepath, imgdir + '/resize/' + output_file_name, size, False, size) == RESIZE_SUCCESS:
                    filenum += 1
                    print "Transform file " + filepath + " to " + output_file_name + " size:" + str(size)
    print "Transform file " + imgdir + " finished. filenum: " + str(filenum)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(-1)
    dirname = sys.argv[1]
    size = int(sys.argv[2])
    index = curr_file_path.rfind("/")
    curr_path = curr_file_path[0:index]
    print "curr: " + curr_path
    transdir(curr_path + "/img/defaultimg/" + dirname, size)
