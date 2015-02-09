#coding=utf-8
__author__ = 'luoyan@maimiaotech.com'
import sys
import time
import datetime
import simplejson as json
sys.path.append('../../../')
from ToCNew.Stat.send_tools import SendTools
import logging
import logging.config
import traceback
def usage(argv0):
    print argv0 + ' user password  address title_file content_file'
if __name__ == '__main__':
    if len(sys.argv) != 6:
        usage(sys.argv[0])
        sys.exit(0)
    try:
        user = sys.argv[1]
        password = sys.argv[2]
        address = sys.argv[3]
        title_file = sys.argv[4]
        content_file = sys.argv[5]
        st = SendTools('1111111', user, password)
        title = open(title_file, 'r').read()
        content = open(content_file, 'r').read()
        st.send_email_with_file(address, content, title,[content_file])
    except:
        exstr = traceback.format_exc()
        print('failed to send mail ' + exstr)
        sys.exit(-1)
