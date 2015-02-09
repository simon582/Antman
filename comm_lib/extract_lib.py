#encoding=utf8
__author__ = 'gaonan'
from readability.readability import Document
import urllib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import bs4
from bs4 import BeautifulSoup
import copy
import re
import lxml.html.soupparser as soupparser
import lxml.etree as etree

'''attr dict key value
    have_title:是否有title字段,1表示正常提取,2表示只使用最长子串
    have_desc:是否有desc字段
    have_content:是否有后续点击正文
    have_desc_img:是否有desc img字段
    have_price:是否有价格字段
    have_go_link:是否有直达链接'''
class ExtractHtml(object):
    def __init__(self):
        self.attr_dict = {}
        self.neg_word_list = []
        self.neg_tag_dict = {}
        self.pre_url = None
        self.have_desc = 0
        self.have_desc_img = 0
        self.have_content = 0
        self.have_price = 0
        self.have_go_link = 0
        self.have_title = 0
    def parser_attr_dict(self):
        if 'have_title' in self.attr_dict:
            self.have_title = self.attr_dict['have_title']
        if 'have_desc' in self.attr_dict and self.attr_dict['have_desc'] == 1:
            self.have_desc = 1
        if 'have_content' in self.attr_dict and self.attr_dict['have_content'] == 1:
            self.have_content = 1
        if 'have_desc_img' in self.attr_dict and self.attr_dict['have_desc_img'] == 1:
            self.have_desc_img = 1
        if 'have_price' in self.attr_dict and self.attr_dict['have_price'] == 1:
            self.have_price = 1
        if 'have_go_link' in self.attr_dict and self.attr_dict['have_go_link'] == 1:
            self.have_go_link = 1

    def get_dom_position(self,cur_dom,dict):
        if cur_dom.parent:
            key = cur_dom.name + '_' + cur_dom.parent.name
        else:
            key = cur_dom.name + '_' + 'head'
        if key not in dict:
            dict[key] = 1
        else:
            dict[key] += 1
    def is_right_dom(self,cur_dom,key):
        if cur_dom.parent:
            cur_key = cur_dom.name + '_' + cur_dom.parent.name
        else:
            cur_key = cur_dom.name + '_' + 'head'
        if cur_key == key:
            return True
        return False

    def process(self,html_list,attr_dict,pre_url,neg_word_list,neg_tag_dict):
        self.attr_dict = copy.deepcopy(attr_dict)
        self.neg_word_list = copy.deepcopy(neg_word_list)
        self.neg_tag_dict = copy.deepcopy(neg_tag_dict)
        self.parser_attr_dict()
        self.pre_url = pre_url
        final_result = []
        if self.have_content:
            for cur_html in html_list:
                cur_dom = BeautifulSoup(cur_html)
                rt_dict = self.process_item(cur_dom)
                if 'title' in rt_dict:
                    print 'final title:',rt_dict['title'].encode('utf8')
                    print 'final url',rt_dict['url']
                else:
                    print 'no title'
                    continue
                if 'text' in rt_dict:
                    for temp_item in rt_dict['text']:
                        print temp_item[0],temp_item[1].encode('utf8')
                else:
                    print 'no content'
                if 'desc_img' in rt_dict:
                    print 'final img:',rt_dict['desc_img']
                if 'price' in rt_dict:
                    print 'final price',rt_dict['price']
                if 'go_link' in rt_dict:
                    print 'final go link',rt_dict['go_link']
                print '****************************************'
                final_result.append(rt_dict)
                #break
        else:
            dom_title_dict = {}
            dom_desc_dict = {}
            rt_result = []
            for cur_html in html_list:
                cur_dom = BeautifulSoup(cur_html)
                rt_dict = self.process_item(cur_dom)
                rt_result.append(rt_dict)
                if self.have_title:
                    if 'temp_title' not in rt_dict:
                        continue
                    self.get_dom_position(rt_dict['temp_title_dom'],dom_title_dict)
                if self.have_desc:
                    if 'temp_desc' not in rt_dict:
                        continue
                    self.get_dom_position(rt_dict['temp_desc_dom'],dom_desc_dict)
            if self.have_title:
                for(key,value) in dom_title_dict.items():
                    print key,value
                title_sorted_list = sorted(dom_title_dict.items(),key=lambda d:d[1],reverse=True)
                print title_sorted_list[0]

            if self.have_desc:
                for(key,value) in dom_desc_dict.items():
                    print key,value
                desc_sorted_list = sorted(dom_desc_dict.items(),key=lambda d:d[1],reverse=True)
                print desc_sorted_list[0]

            for item in rt_result:
                if self.have_title:
                    if 'temp_title' not in item:
                        continue
                    if self.is_right_dom(item['temp_title_dom'],title_sorted_list[0][0]):
                        print 'final title',item['temp_title'].encode('utf8')
                        item['title'] = item['temp_title']
                    else:
                        print item['temp_title'].encode('utf8')
                        print 'bad title',item['temp_title'].encode('utf8')
                        continue
                if self.have_desc:
                    if 'temp_desc' in item:
                        if self.is_right_dom(item['temp_desc_dom'],desc_sorted_list[0][0]):
                            print 'final desc',item['temp_desc'].encode('utf8')
                            item['desc'] = item['temp_desc']
                        else:
                            print item['temp_desc'].encode('utf8')
                            print 'bad desc',item['temp_desc'].encode('utf8')
                            continue
                if 'desc_img' in item:
                    print 'final img:',item['desc_img']
                if 'price' in item:
                    print 'final price',item['price']
                if 'go_link' in item:
                    print 'final go link',item['go_link']
                print '****************************************'
                final_result.append(item)
        return final_result

    def is_content(self,desc_content,text_content):
        if not self.have_desc:
            return True
        cmp_dict = {}
        same_num = 0
        text_len = 0
        for i_str in desc_content:
            cmp_dict[i_str] = 1

        for item in text_content:
            if item[0] == '1':
                text_len += len(item[1])
                for i_str in item[1]:
                    if i_str in cmp_dict:
                        same_num += 1
                #print item[1].encode('utf8')
        #print same_num,text_len,float(same_num)/text_len,float(same_num)/len(desc_content)
        if text_len > 50 and (float(same_num)/text_len > 0.3 or float(same_num)/len(desc_content)>0.6):
            return True
        return False

    def is_title(self,maybe_title,content_title):
        print 'maybe title','\t',maybe_title.encode('utf8')
        print 'content title','\t',content_title.encode('utf8')

        title_dict = {}
        same_num = 0
        for i_str in maybe_title:
            title_dict[i_str] = 1
        for i_str in content_title:
            if i_str in title_dict:
                same_num += 1
                #if cur_title == title or title in cur_title or cur_title in title:
        #print same_num,len(maybe_title),len(content_title),float(same_num)/len(maybe_title),float(same_num)/len(content_title)
        if float(same_num)/len(maybe_title) > 0.6 or float(same_num)/len(content_title) > 0.6:
            title_match = True
        else:
            title_match = False
        return title_match

    def process_item(self,cur_dom):
        #process title
        rt_dict = {}
        if self.have_desc:
            (desc_len,desc,desc_dom) = self.get_desc(cur_dom)
            #print desc.encode('utf8')
        else:
            desc = ''
            desc_dom = None
        find_title = ''
        find_url = ''
        find_content = None
        if self.have_title:
            is_find_title = False
            (title_dict,max_title,max_title_len,max_title_dom) = self.get_title(cur_dom)
            if self.have_content:
                if len(title_dict['title']) > 0:
                    for value in title_dict['title']:
                        #print 'title',value[0].replace(' ','').encode('utf8'),value[1].encode('utf8')
                        (cur_title,text_result) = self.get_content(value[1])
                        if self.is_title(value[0],cur_title):
                            is_find_title = True
                            find_title = value[0]
                            find_content = text_result
                            find_url = value[1]
                            break
                elif len(title_dict['other']) > 0:
                    for value in title_dict['other']:
                        #print 'other',value[0].strip().encode('utf8'),value[1].strip().encode('utf8')
                        (cur_title,text_result) = self.get_content(value[1])
                        if self.is_title(value[0],cur_title):
                            is_find_title = True
                            find_title = value[0]
                            find_url = value[1]
                            find_content = text_result
                            break
                else:
                    print 'no title'
            if self.have_content:
                if is_find_title:
                    rt_dict['title'] = find_title
                    rt_dict['url'] = find_url
                else:
                    return rt_dict
            else:
                rt_dict['temp_title'] = max_title
                rt_dict['temp_title_dom'] = max_title_dom

        if self.have_content:
            if self.is_content(desc,find_content):
                rt_dict['text'] = find_content
            else:
                print 'find content fail'
        else:
            if self.have_desc:
                rt_dict['temp_desc'] = desc
                rt_dict['temp_desc_dom'] = desc_dom

        if self.have_desc_img:
            temp_result = self.get_desc_img(cur_dom,find_url)
            #print 'lalala',temp_result
            if len(temp_result):
                rt_dict['desc_img'] = temp_result
        if self.have_price:
            temp_price_list = []
            self.get_price(cur_dom,temp_price_list)
            rt_dict['price'] = temp_price_list
        if self.have_go_link:
            rt_dict['go_link'] = self.get_all_click_url(cur_dom,desc_dom,find_url)


        return rt_dict

    def get_desc(self,cur_dom):
        return self.compute_max_len(cur_dom)
    def is_neg_tag(self,cur_dom):
        if cur_dom.name not in self.neg_tag_dict:
            return False
        item = self.neg_tag_dict[cur_dom.name]
        for (dom_att,att_value) in cur_dom.attrs.items():
            temp_str = ''

            if isinstance(att_value,list):
                for cur_temp_str in att_value:
                    temp_str = temp_str + cur_temp_str + ' '
                temp_str = temp_str[:-1]
            else:
                temp_str = att_value
            if dom_att in item and (item[dom_att] == temp_str):
                return True
        return False

    def compute_max_len(self,cur_dom):
        max_len = 0
        max_text = ''
        max_tag = None
        my_len = 0
        for item in cur_dom.contents:
            if isinstance(item,bs4.element.Tag):
                if self.is_neg_tag(item):
                    continue
                if item.name == 'p' or item.name == 'a' or item.name == 'span':
                    temp_str = item.get_text().replace(' ','').replace(u'\u3000','')
                    for neg_item in self.neg_word_list:
                        temp_str = temp_str.replace(neg_item,'')
                    #my_len += len(item.get_text().replace(' ','').replace(u'\u3000',''))
                    my_len += len(temp_str)
                    continue
                (cur_len,cur_text,cur_tag) = self.compute_max_len(item)
                if cur_len > max_len:
                    max_len = cur_len
                    max_text = cur_text
                    max_tag = cur_tag
        if max_len == 0 or my_len > max_len:
            rt = cur_dom.get_text()
            rt = rt.replace(' ','').replace(u'\u3000','')
            for neg_item in self.neg_word_list:
                rt = rt.replace(neg_item,'')
            #print rt.encode('utf8'),cur_dom.name
            return len(rt),rt,cur_dom
        else:
            return max_len,max_text,max_tag
    def get_desc_img(self,cur_dom,url):
        find_result = cur_dom.findAll('img')
        #print len(find_result)
        if len(find_result) == 0:
            print 'find nothing for img'
            return []

        if len(find_result) == 1:
            if not find_result[0].attrs or 'src' not in find_result[0].attrs:
                return []
            else:
                return [find_result[0].attrs['src']]
        else:
            if not self.have_content:
                temp_result = []
                for item in find_result:
                    if not item.attrs or 'src' not in item.attrs:
                        continue
                    temp_result.append(item.attrs['src'])
                return temp_result
            for item in find_result:
                #print item,isinstance(item,bs4.element.Tag),item.name,item.attrs
                if not item.attrs or 'src' not in item.attrs:
                    continue
                item_parent = item.parent

                if item_parent.name == 'a' and 'href' in item_parent.attrs and item_parent.attrs['href'] == url:
                    #print 'get it',item.attrs['src']
                    return [item.attrs['src']]
            for item in find_result:
                if not item.attrs or 'src' not in item.attrs:
                    continue
                item_parent = item.parent
                if item_parent.name == 'a' and 'href' in item_parent.attrs:
                    return [item.attrs['src']]

            return []
    def get_price(self,cur_dom,price_list):
        for item in cur_dom.contents:
            if not isinstance(item,bs4.element.Tag):
                if len(item.string)<10 and (u'元' in item.string or u'￥' in item.string or u'¥' in item.string):
                    #print 'find price',item.string.encode('utf8')
                    price_list.append(item.string)
            else:
                self.get_price(item,price_list)
    def get_max_len_title(self,cur_dom):
        max_len = 0
        max_text = ''

        for item in cur_dom.contents:
            if isinstance(item,bs4.element.Tag):
                (cur_len,cur_text) = self.get_max_len_title(item)
                if cur_len > max_len:
                    max_len = cur_len
                    max_text = cur_text
            else:
                if len(item.string) > max_len:
                    max_len = len(item.string)
                    max_text = item.string
        return max_len,max_text
    def is_in_desc_dom(self,cur_dom,desc_dom):
        if not desc_dom:
            return False
        now_dom = cur_dom.parent
        while now_dom:
            if now_dom is desc_dom:
                print 'find dom in desc_dom',now_dom.contents,cur_dom.attrs['href']
                return True
            now_dom = now_dom.parent
        return False

    def get_all_click_url(self,cur_dom,desc_dom,find_url):
        rt_result = []
        find_result = cur_dom.findAll('a')
        for item in find_result:
            if not isinstance(item,bs4.element.Tag):
                continue
            if self.is_in_desc_dom(item,desc_dom):
                continue
            url = ''
            if 'href' in item.attrs:
                url = item.attrs['href']
            if 'javascript' in url or '#' in url:
                continue
            if 'http://' not in url:
                url = self.pre_url + url
            if url == find_url:
                continue
            rt_result.append(url)
        return rt_result

    def get_title(self,cur_dom):
        title_dict = {'title':[],'other':[]}
        find_result = cur_dom.findAll('a')
        if len(find_result) == 0:
            print 'find nothing for cur html'
            return title_dict
        max_title_len = 0
        max_title = ''
        max_title_dom = None

        for item in find_result:
            if not isinstance(item,bs4.element.Tag):
                continue

            if 'href' in item.attrs:
                url = item.attrs['href']
            else:
                continue
            if 'javascript' in url or '#' in url:
                continue
            if 'http://' not in url:
                url = self.pre_url + url
            is_hz = False
            for ch in url:
                if ch >= u'\u4e00' and ch <= u'\u9fa5':
                    is_hz = True
                    break
            if is_hz:
                print url.encode('utf8'),'need jump'
                continue
                #self.process_go_link(url)
            #print item.get_text().encode('utf8')
            if self.have_title == 2:
                (text_len,text) = self.get_max_len_title(item)
                print text.encode('utf8')
                text = text.replace(u'\t',' ').replace(u' ','').replace(u'\u3000','').replace(u'\n',' ')
            else:
                text = item.get_text().replace(u' ','').replace(u'\u3000','').replace(u'\n',' ').replace(u'\t',' ')
            print text.encode('utf8')
            if len(text) < 10:
                continue

            if 'title' in item.attrs:
                temp_text = item.attrs['title'].replace(u' ','').replace(u'\u3000','').replace(u'\n','').replace(u'\t','')
                title_dict['title'].append([temp_text,url,item.name])
                if len(temp_text) > max_title_len:
                    max_title_len = len(temp_text)
                    max_title = temp_text
                    max_title_dom = item
            else:
                title_dict['other'].append([text,url,item.name])
                if len(text) > max_title_len:
                    max_title_len = len(text)
                    max_title = text
                    max_title_dom = item
        return title_dict,max_title,max_title_len,max_title_dom

    def get_content(self,url):
        rt_result = []
        dr = re.compile(r'<[^>]+>',re.S)
        html = urllib.urlopen(url).read()
        cur_title = Document(html).short_title().replace(' ','')
        readable_article = Document(html).summary()
        print readable_article.encode('utf8')
        readable_article = readable_article.replace('&#13;','')
        cur_list = readable_article.replace('</p>','\n').split('\n')
        for item in cur_list:
            if '<img' in item and 'src=' in item:
                #print item.split('src=')[1].split('"')[1]
                dom = soupparser.fromstring(item)
                if len(dom) > 0:
                    img_path = dom[0].xpath('.//img')
                    for img in img_path:
                        rt_result.append(['0',img.get('src')])
            else:
                use_item = dr.sub('',item).replace(' ','')
                if len(use_item) > 10:
                    rt_result.append(['1',use_item])
        return cur_title,rt_result

if __name__ == '__main__':
    from scrapy.selector import HtmlXPathSelector
    eh = ExtractHtml()
    attr_dict = {
            'have_title':1,
            'have_desc':1,
            'have_content':1,
            'have_desc_img':1,
            'have_price':1,
            'have_go_link':1,
            } 
    neg_word_list = []
    neg_tag_dict = {}
    url = 'http://www.7y7.com/shoushen/mxjf/'
    html = urllib.urlopen(url).read()
    hxs = HtmlXPathSelector(text=html)
    html_list = hxs.select('//div[@class="list_txt"]/dl').extract()
    pre_url = url
    final_result = eh.process(html_list,attr_dict,pre_url,neg_word_list,neg_tag_dict)
