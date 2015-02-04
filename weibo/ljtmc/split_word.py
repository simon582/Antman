#encoding=utf8

import sys
import string

BOSS_CONF_FILE = '/usr/local/BOSS/conf/boss.conf'
sys.path.append('/usr/local/BOSS/lib/')
from Boss4Python import Boss4Python

class WordSeg(object):
    def __init__(self):
        self.boss = Boss4Python()
        self.boss.init(BOSS_CONF_FILE)
        self.table = string.maketrans("","")
    def do_segment(self,words):
        if isinstance(words,unicode):
            words = words.encode('utf8')
        word_list= []
        result = self.boss.process(words,1)
        for word in result:
            temp_list = word.split('\1')
            word_list.append(temp_list)
        return word_list
    def Q2B(self,uchar):
        inside_code=ord(uchar)
        if inside_code==0x3000:
            inside_code=0x0020
        else:
            inside_code-=0xfee0
        if inside_code<0x0020 or inside_code>0x7e: #转完之后不是半角字符返回原来的字符
            return uchar
        return unichr(inside_code)
    def stringQ2B(self,ustring):
        """把字符串全角转半角"""
        return "".join([self.Q2B(uchar) for uchar in ustring])
    def uniform(self,ustring):
        """格式化字符串，完成全角转半角，大写转小写的工作"""
        return self.stringQ2B(ustring).lower()
    def remove_punctuation(self,str):
        if isinstance(str,unicode):
            str = str.encode('utf8')
        return str.translate(self.table, string.punctuation + ' ')
class QueryProcess(object):
    def __init__(self):
        self.word_seg = WordSeg()
        self.term_dict = {}
        self.term_all_dict = {}
        self.cat_name = {}
        self.cat_parent = {}
        self.raw_cat_dict = {}
        self.raw_cat_all_dict = {}
        self.raw_cat_len_dict = {}
        self.TERM_CORE_TYPE = {'BL' : 0,
                               'CP_CORE' : 3,
                               'CP_XIUSHI' : 2,
                               'DAILI' : 0,
                               'FW' : 1,
                               'JG' : 1,
                               'JG_CORE' : 2,
                               'LKH' : 0,
                               'OTHER' : 0,
                               'PP' : 2,
                               'PP_CORE' : 3,
                               'PT' : 0,
                               'PZH' : 0,
                               'QH' : 2,
                               'RKH' : 0,
                               'XH' : 1,
                               'XH_CORE' : 2,
                               'XS' : 1,
                               'ZM' : 2,
                               'ZM_CORE' : 3
        }
    def process(self,in_file):
        word_dict = {}
        fp = open(in_file,'r')
        pp_list = []
        for line in fp:
            term_list = self.word_seg.do_segment(line.split(',')[4].strip())
            for term in term_list:
                #for par in term:
                #    print par + ' ',
                #print ''
                if len(term[0]) < 4:
                    continue
                if term[1].find('XS') == -1 and term[1].find('CP') == -1 and term[1].find('PT') == -1:
                    continue
                if not word_dict.has_key(term[0]):
                    word_dict[term[0]] = 1
                else:
                    word_dict[term[0]] += 1
        for key, value in word_dict.items():
            print key + ',' + str(value)

if __name__ == "__main__":
    in_file = sys.argv[1]
    QP = QueryProcess()
    QP.process(in_file)
