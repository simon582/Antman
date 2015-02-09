#! /usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import XmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy import log
from scrapy.http import FormRequest
import json as simplejson
import httplib, urllib, urllib2
import sys
sys.path.append('../comm_lib')
import time
import utils
import re
import pdb
from BeautifulSoup import BeautifulSoup
#import bs4
#from bs4 import BeautifulSoup
from readability.readability import Document
import lxml.html.soupparser as soupparser
import lxml.etree as etree
from uniform.items import UniformItem
import hashlib
import datetime
import traceback
import socket
from gencategory import GenCat
from table import Table
import os

def get_attr_list(node, name_list = ['div'], attr_list = ['class', 'id']):
    info = node.name
    if name_list:
        for name in name_list:
            for attr in attr_list:
                if node.has_key(attr) and node.name == name:
                    info = info + '[@' + attr + '=\"' + node[attr] + '\"]'
                    return info
    else:
        for attr in attr_list:
            if node.has_key(attr):
                info = info + '[@' + attr + '=\"' + node[attr] + '\"]'
                return info
    return info

def get_last_tag(xpath):
    index = xpath.rfind('/')
    index_end = xpath[index + 1:].find('[')
    if index_end == -1:
        return xpath[index + 1:]
    else:
        return xpath[index + 1: index + 1 + index_end]
def remove_xpath_head(xpath):
    if xpath[0] == '/':
        xpath = xpath[1:]
    index = xpath.find('/')
    if index != -1:
        return xpath[index + 1:]
    else:
        return ''
    
def valid_main_xpath(hxs, xpath):
    if utils.has_suffix(xpath, 'a') or utils.has_suffix(xpath, 'li') or utils.has_suffix(xpath, 'ul'):
        contents = hxs.select(xpath).extract()
        if len(contents) > 0 and utils.get_content(contents[0], 4):
            return True
        else:
            return False
    return True

def get_xpath(node, xpath_infos, tag_info_list):
    list = []
    for tag_info in tag_info_list:
        tag = tag_info[0]
        attr = tag_info[1]
        if tag:
            sub_node = node.find(tag)
        else:
            sub_node = node
        if sub_node and sub_node.has_key(attr):
            #if not xpath_infos:
            #    list.append({'xpath' : tag + '/@' + attr})
            if tag:
                xpath = xpath_infos + '/' + tag + '/@' + attr
            else:
                xpath = xpath_infos + '/@' + attr
            list.append({'xpath' : xpath})
    return list

def compare_text_len(item1, item2):
    return item1['text_len'] - item2['text_len']

def compare_text_len2(string1, string2):
    return len(string1) - len(string2)

def is_date(string):
    if string.find(u'月') != -1 or string.find(u'日') != -1:
        p = re.compile(r'[0-9]+')
        if p.match(string.strip(u'月').strip(u'日').strip('-')):
            return True
        elif string.find(u'年') != -1 and string.find(u'月') != -1 and string.find(u'日') != -1:
            return True
        else:
            return False
    elif string.find(u':') != -1 or string.find(u'/') != -1 or string.find(u'-') != -1:
        p = re.compile(r'[0-9]+')
        if p.match(string.strip(u':').strip(u'/').strip(u'-').strip(u' ')):
            return True
        else:
            return False
    return False

def parser_content_from_buffer(html):
    rt_result = []
    dr = re.compile(r'<[^>]+>',re.S)
    readable_article = Document(html).summary().encode('utf8')
    #print readable_article
    readable_article = readable_article.replace('&#13;','')
    cur_list = readable_article.split('\n')
    count = 0
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
                text = utils.decode(use_item, 'utf8')
                if not text:
                    text = use_item
                rt_result.append(['1',text])
    return rt_result


def parser_content(url):
    rt_result = []
    dr = re.compile(r'<[^>]+>',re.S)
    html = urllib.urlopen(url).read()
    readable_article = Document(html).summary().encode('utf8')
    #print readable_article
    readable_article = readable_article.replace('&#13;','')
    cur_list = readable_article.split('\n')
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
                text = utils.decode(use_item, 'utf8')
                if not text:
                    text = use_item
                rt_result.append(['1',text])
    return rt_result

def is_content_webpage(buffer):
    rt_result = parser_content_from_buffer(buffer)
    for item in rt_result:
        if item[0] == '1' and len(item[1]) > 50:
            return True, rt_result
    return False, rt_result


class TreeNode:
    def __init__(self, node, children, parent):
        self.node = node
        self.children = children
        self.parent = parent
        self.name = node.name

    def get_text_xpath(self, list, xpath_infos, xpath_dict, level_info):
        item = {}
        item['xpath'] = xpath_infos
        if hasattr(self.node, 'text'):
            text = self.node.text.strip()
            text_len = len(text)
            item['text_len'] = text_len
            item['text'] = text

            #if xpath_infos:
            item['xpath'] = item['xpath'] + '/text()'
            #else:
            #    item['xpath'] = ''
        list.append(item)
        for item in list:
            item['xpath'] = remove_xpath_head(item['xpath'])
            if not xpath_dict.has_key(item['xpath']):
                xpath_dict[item['xpath']] = 0
            item['index'] = xpath_dict[item['xpath']]
            xpath_dict[item['xpath']] += 1
            print level_info + item['xpath'] + ' index ' + str(item['index'])
            #print level_info + xpath_infos
        return list

    def is_valid(self):
        if self.node.name == 'a':
            if self.node.has_key('href'):
                if utils.has_prefix(self.node['href'], 'javascript'):
                    return False
        return True

    def get_first_tag(self, indexpath):
        if not indexpath:
            return None, None, None, None
        if len(indexpath) >= 1 and indexpath[0] == '/':
            indexpath = indexpath[1:]
        index = indexpath.find('/')
        if index == -1:
            if indexpath[0] == '@':
                attr = indexpath[1:]
            elif indexpath == 'text()':
                attr = 'text()'
            else:
                attr = None
                log.msg('get_first_tag : failed to get attr', level = log.ERROR)
            return None, None, attr, None
        subpath= indexpath[0:index]
        index2 = subpath.find('(')
        if index2 == -1:
            tag = subpath
            tag_idx = 0
            attr = None
            return tag, tag_idx, attr, indexpath[index:]
        index3 = subpath.find(')')
        if index3 == -1:
            log.msg('no match ) for [' + indexpath + ']', level = log.ERROR)
            return None, None, None, None
        tag_idx = int(subpath[index2 + 1:index3])
        tag = subpath[:index2]
        attr = None
        return tag, tag_idx, attr, indexpath[index:]

    def select(self, indexpath):
        tag_list = []
        tag_attr = None
        sub_indexpath = indexpath
        while True:
            tag, index, attr, sub_indexpath = self.get_first_tag(sub_indexpath)
            if tag and index != None:
                tag_list.append({'tag':tag, 'index':index})
            elif attr:
                tag_attr = attr
            else:
                break
        tree = self
        for tag_info in tag_list:
            tag = tag_info['tag']
            index = tag_info['index']
            count = 0
            found = False
            for child in tree.children:
                if not child.is_valid() or found:
                    continue
                if child.node.name == tag:
                    if index == count:
                        tree = child
                        found = True
                    count += 1
            if not found:
                if utils.has_suffix(indexpath, 'img/@src'):
                    img_node = tree.node.findAll('img')
                    if img_node and len(img_node) > 0 and img_node[0].has_key('src'):
                        return img_node[0]['src']
                #print 'inxpath'
                return ''
                #return 'not found'
        if tag_attr == 'text()' and hasattr(tree.node, 'text'):
            return tree.node.text
        elif tree.node.has_key(tag_attr):
            return tree.node[tag_attr]
        return ''

    
    def get_sub_indexpath(self, xpath = '', level = 0, xpath_dict = {}, node_index = 0):
        level_info = ''
        for i in xrange(level):
            level_info += '\t'
        xpath_infos = xpath + '/' + self.node.name + '(' + str(node_index) + ')'
        if not self.children or len(self.children) == 0:
            if not self.is_valid():
                return []
            list = get_xpath(self.node, xpath_infos, [['img', 'src'], ['', 'href'], ['', 'title']])
            if self.node.name == 'img':
                for attr_pair in self.node.attrs:
                    attr = attr_pair[0]
                    list.append({'xpath' : xpath_infos + '/@' + attr})
            list = self.get_text_xpath(list, xpath_infos, xpath_dict, level_info)
            return list

        list = []
        if self.node.name == 'p' or self.node.name == 'div':
            list = self.get_text_xpath(list, xpath_infos, xpath_dict, level_info)
        elif self.node.name == 'a':
            list = get_xpath(self.node, xpath_infos, [['img', 'src'], ['', 'href'], ['', 'title']])
            list = self.get_text_xpath(list, xpath_infos, xpath_dict, level_info)
        tag_dict = {}
        for child in self.children:
            if not child.is_valid():
                continue
            if not tag_dict.has_key(child.node.name):
                tag_dict[child.node.name] = 0

            sub_list = child.get_sub_indexpath(xpath_infos, level + 1, xpath_dict, tag_dict[child.node.name])
            tag_dict[child.node.name] += 1
            list.extend(sub_list)
        return list

    def get_sub_xpath(self, xpath = '', level = 0, xpath_dict = {}):
        level_info = ''
        for i in xrange(level):
            level_info += '\t'
        xpath_infos = xpath + '/' + get_attr_list(node = self.node, name_list = None)
        if not self.children or len(self.children) == 0:
            if not self.is_valid():
                return []
            #xpath_infos = remove_xpath_head(xpath_infos)
            list = get_xpath(self.node, xpath_infos, [['img', 'src'], ['', 'href'], ['', 'title']])
            list = self.get_text_xpath(list, xpath_infos, xpath_dict, level_info)
            return list

        list = []
        if self.node.name == 'p' or self.node.name == 'div':
            list = self.get_text_xpath(list, xpath_infos, xpath_dict, level_info)
        elif self.node.name == 'a':
            list = get_xpath(self.node, xpath_infos, [['img', 'src'], ['', 'href'], ['', 'title']])
            list = self.get_text_xpath(list, xpath_infos, xpath_dict, level_info)
        for child in self.children:
            sub_list = child.get_sub_xpath(xpath_infos, level + 1, xpath_dict)
            list.extend(sub_list)
        return list

    def is_valid_xpath(self, h, xpath, attr_name, item):
        if xpath:
            if len(h.select(xpath)) == 0:
                print 'no ' + attr_name + '_xpath for ' + attr_name + '_xpath ' + xpath
                value = ''
                xpath = ''
                item = None
                return value, xpath, item
            else:
                value = utils.get_one(h.select(xpath).extract()).strip()
                print attr_name + ' ' + value.encode('utf8')
        else:
            value = ''
            item = None
        return value, xpath, item

    def get_main_attr_indexpath_from_file(self, list, file_name, first_tag, response, tree):
        list = tree.get_sub_indexpath('', 0, {}, 0)
        xpath_dict = {}
        for item in list:
            #if not xpath_dict.has_key('img') and (utils.has_suffix(item['xpath'], 'img/@src') or utils.has_suffix(item['xpath'], 'img(0)/@src')):
            #    item['attr_name'] = 'img'
            #    xpath_dict['img'] = item
            #if utils.has_suffix(item['xpath'], 'text()') or utils.has_suffix(item['xpath'], '@title') or utils.has_suffix(item['xpath'], '@href'):
            item['text'] = tree.select(item['xpath'])
            #if not utils.get_one(h.select(item['xpath']), item['index']):
            #    item['text'] = ''
            #else:
            #    item['text'] = utils.get_one(h.select(item['xpath']), item['index']).extract().strip()
            print ('xpath ' + item['xpath'] + ' text [' + item['text'] + ']').encode('utf8')
            attr_list = ['@title', '@url', '@img', '@title2', '@desc', '@date', '@go_link', '@current_price', '@origin_price', '@discount', '@img2', '@express']
            xpath_index = utils.get_index(attr_list, item['text'])
            if xpath_index != -1:
                attr = attr_list[xpath_index][1:]
                item['attr_name'] = attr
                xpath_dict[attr] = item
        return xpath_dict

    def get_main_attr_xpath_from_file(self, list, file_name, first_tag, response):
        file = open(file_name, 'r')
        buffer = file.read()
        #hxs = get_xpath_selector(text=buffer)
        hxs = utils.get_xpath_selector_from_response(buffer, response)
        utils.write_file('hxs.html', hxs.extract().encode('utf8'))
        if utils.has_prefix(response.body, '<?xml'):
            h = hxs.select('//' + first_tag)
        else:
            h = hxs.select('//body/' + first_tag)
        xpath_dict = {}
        for item in list:
            if not xpath_dict.has_key('img') and utils.has_suffix(item['xpath'], 'img/@src'):
                item['attr_name'] = 'img'
                xpath_dict['img'] = item
            elif utils.has_suffix(item['xpath'], 'text()') or utils.has_suffix(item['xpath'], '@title') or utils.has_suffix(item['xpath'], '@href'):
                if not utils.get_one(h.select(item['xpath']), item['index']):
                    item['text'] = ''
                else:
                    item['text'] = utils.get_one(h.select(item['xpath']), item['index']).extract().strip()
                print ('xpath ' + item['xpath'] + ' text [' + item['text'] + ']').encode('utf8')
                attr_list = ['@title', '@url', '@img', '@title2', '@desc', '@date', '@go_link', '@current_price', '@origin_price', '@discount', '@img2']
                xpath_index = utils.get_index(attr_list, item['text'])
                if xpath_index != -1:
                    attr = attr_list[xpath_index][1:]
                    item['attr_name'] = attr
                    xpath_dict[attr] = item
        return xpath_dict

    def get_main_attr_xpath(self, list, h):
        desc_xpath = ''
        title_xpath = ''
        img_xpath = ''
        url_xpath = ''
        date_xpath = ''
        desc_item = None
        title_item = None
        img_item = None
        url_item = None
        date_item = None
        text_len_list = []
        for item in list:
            if utils.has_suffix(item['xpath'], 'text()'):
                if not utils.get_one(h.select(item['xpath']), item['index']):
                    item['text'] = ''
                else:
                    item['text'] = utils.get_one(h.select(item['xpath']), item['index']).extract().strip()
                item['text_len'] = len(item['text'])
            if not img_xpath and utils.has_suffix(item['xpath'], 'img/@src'):
                img_xpath = item['xpath']
                item['attr_name'] = 'img'
                img_item = item
            if not url_xpath and utils.has_suffix(item['xpath'], '@href'):
                url_xpath = item['xpath']
                item['attr_name'] = 'url'
                url_item = item
            if not title_xpath and utils.has_suffix(item['xpath'], '@title'):
                h_title = utils.get_one(h.select(item['xpath']), item['index'])
                if h_title:
                    text = h_title.extract()
                    text_len = len(text)
                    item['text_len'] = text_len
                    item['text'] = text
                    #text_len = item['text_len']
                    text_len_list.append(item)
            if utils.has_suffix(item['xpath'], 'text()'):
                if not date_xpath and is_date(item['text']):
                    date_xpath = item['xpath']
                    item['attr_name'] = 'date'
                    date_item = item
                elif not is_date(item['text']):
                    text_len = item['text_len']
                    text_len_list.append(item)
        print 'before sort'
        for item in text_len_list:
            print ('xpath ' + item['xpath'] + ' text_len ' + str(item['text_len']) + ' text [' + item['text'] + ']').encode('utf8')
        res_text_len_list_sorted = sorted(text_len_list, cmp=compare_text_len, reverse=True)
        print 'after sort'
        for item in res_text_len_list_sorted:
            print ('xpath ' + item['xpath'] + ' text_len ' + str(item['text_len']) + ' text [' + item['text'] + ']').encode('utf8')

        res_text_len_list = []
        prev_text = ''
        for item in res_text_len_list_sorted:
            if item['text_len'] <= 3:
                continue
            if item['text'].find(u'点击') != -1:
                continue
            if len(prev_text) == len(item['text']) and prev_text == item['text']:
                continue
            prev_text = item['text']
            res_text_len_list.append(item)
        if len(res_text_len_list) >= 2:
            desc_xpath = res_text_len_list[0]['xpath']
            desc_text = res_text_len_list[0]['text']
            res_text_len_list[0]['attr_name'] = 'desc'
            desc_item = res_text_len_list[0]
            print ('desc_xpath ' + desc_xpath + ' text_len ' + str(res_text_len_list[0]['text_len']) + ' index ' + str(res_text_len_list[0]['index']) + ' text [' + desc_text + ']').encode('utf8')
            if not title_xpath:
                title_xpath = res_text_len_list[1]['xpath']
                title_text = res_text_len_list[1]['text']
                res_text_len_list[1]['attr_name'] = 'title'
                title_item = res_text_len_list[1]
                print ('title_xpath ' + title_xpath + ' text_len ' + str(res_text_len_list[1]['text_len']) + ' index ' + str(res_text_len_list[1]['index']) + ' text [' + title_text + ']').encode('utf8')
        elif len(res_text_len_list) == 1:
            if not title_xpath:
                title_xpath = res_text_len_list[0]['xpath']
                title_text = res_text_len_list[0]['text']
                res_text_len_list[0]['attr_name'] = 'title'
                title_item = res_text_len_list[0]
                print ('title_xpath ' + title_xpath + ' text_len ' + str(res_text_len_list[0]['text_len']) + ' index ' + str(res_text_len_list[0]['index']) + ' text [' + title_text + ']').encode('utf8')
        title, title_xpath, title_item = self.is_valid_xpath(h, title_xpath, 'title', title_item)
        desc, desc_xpath, desc_item = self.is_valid_xpath(h, desc_xpath, 'desc', desc_item)
        if title and (desc == title):
            desc_xpath = ''
            desc_item = None
        if date_xpath and len(h.select(date_xpath)) > 0 and not is_date(utils.get_one(h.select(date_xpath), date_item['index']).extract()):
            date_xpath = ''
            date_item = None
        #return [url_xpath, img_xpath, title_xpath, desc_xpath, date_xpath]
        #return [url_xpath, img_xpath, title_xpath, desc_xpath, date_xpath], [url_item, img_item, title_item, desc_item, date_item]
        return [url_item, img_item, title_item, desc_item, date_item]

    def get_max_tag(self, hxs, level = 0):
        tag_to_num = {}
        for child in self.children:
            name = get_attr_list(child.node)
            if not tag_to_num.has_key(name):
                tag_to_num[name] = 0
            tag_to_num[name] += 1
        max = 0
        max_tag = ""
        cur_tag = ""
        max_xpath = ""
        for name in tag_to_num:
            if max < tag_to_num[name]:
                max = tag_to_num[name]
                max_tag = name
                cur_tag = name
                max_xpath = name
        level_info = ''
        for i in xrange(level):
            level_info += '\t'
        #infos = level_info + ' name = ' + str(self.name)
        infos = level_info + get_attr_list(self.node)
        for tag in tag_to_num:
            infos = infos + ' ' + tag + ' ' + str(tag_to_num[tag])
        log.msg(infos, level = log.DEBUG)
        for child in self.children:
            max_child, max_child_tag, max_child_xpath = child.get_max_tag(hxs, level + 1)
            if max < max_child and valid_main_xpath(hxs, '//' + get_attr_list(child.node) + '/' + max_child_xpath):
                max = max_child
                max_tag = max_child_tag
                max_xpath = get_attr_list(child.node) + '/' + max_child_xpath
                #print 'max ' + str(max) + ' max_tag ' + str(max_tag) + ' max_xpath ' + max_xpath
                #return max_child, max_child_tag, max_tag + '/' + max_child_xpath
        return max, max_tag, max_xpath

    def get_text(self, xpath_tags, img_tag, start_url_info):
        filter_html = None
        if start_url_info.has_key('crawl_text_filter_html'):
            filter_html = start_url_info['crawl_text_filter_html']
        rt_result = []
        for child_node in self.node.contents:
            if not hasattr(child_node, 'name'):
                if len(str(child_node).strip()) > 0:
                    log.msg('child : noname text [' + str(child_node) + ']', level = log.DEBUG)
                    rt_result.append(['1', utils.html_to_text(str(child_node).decode('utf8'))])
                continue
            if child_node.name == 'script' or child_node.name == 'style' or child_node.name == 'iframe':
                continue
            if xpath_tags and utils.get_index(xpath_tags, child_node.name) == -1:
                continue
        #for child in self.children:
            log.msg('child : ' + child_node.name.encode('utf8') + ' html [' + str(child_node) + ']', level = log.DEBUG)
            if hasattr(child_node, 'text') and len(child_node.text.strip()) > 0:
                html_item = str(child_node)
                text = utils.html_to_text(child_node.text)
                if filter_html and html_item.find(filter_html) != -1:
                    log.msg('skip because of having filter_html [' + text + ']', level = log.WARNING)
                    continue
                log.msg('child : ' + child_node.name.encode('utf8') + ' text [' + str(child_node.text.encode('utf8')) + ']', level = log.DEBUG)
                rt_result.append(['1', text])
            #if child.name == 'div':
            imgs = self.get_imgs(child_node, img_tag)
            if len(imgs) > 0:
                log.msg('imgs ' + str(imgs), level = log.DEBUG)
                for img in imgs:
                    rt_result.append(['0', img])
        return rt_result

    def get_attr_candidates(self, node):
        candidates = {
                '@url': [],
                '@title': [],
                '@date': [],
                '@desc': [],
                '@img': [],
                'time_format': [],
                }
        if not hasattr(node, 'contents'):
            return candidates
        for child_node in node.contents:
            if not hasattr(child_node, 'name'):
                continue
            if child_node.name == 'a' and child_node.has_key('href'):
                candidates['@url'].append(child_node['href'].encode('utf8'))
                #candidates['@title'].append(child_node.text)
            if hasattr(child_node, 'text'):
                time_format = utils.get_time_format(child_node.text)
                if time_format:
                    candidates['@date'].append(child_node.text.encode('utf8'))
                    candidates['time_format'] = [time_format]
                elif len(child_node.text) >= 6:
                    candidates['@desc'].append(child_node.text.encode('utf8'))
            if child_node.has_key('title'):
                candidates['@title'].append(child_node['title'].encode('utf8'))
            if child_node.name == 'img':
                for attr in child_node.attrs:
                    candidates['@img'].append(child_node[attr[0]].encode('utf8'))
            sub_candidates = self.get_attr_candidates(child_node)
            for key in sub_candidates:
                candidates[key].extend(sub_candidates[key])
        return candidates


    def get_imgs(self, node, img_tag):
        if not node:
            return []
        if hasattr(node, 'name') and node.name == u'img':
            if img_tag and node.has_key(img_tag):
                return [node[img_tag]]
            elif node.has_key('src'):
                return [node['src']]
        if not hasattr(node, 'contents') or not node.contents:
            return []
        imgs = []
        for child in node.contents:
            imgs.extend(self.get_imgs(child, img_tag))
        return imgs

class UniformSpider(BaseSpider):
    name = "uniform"
    max_item = 500
    max_pages = 30
    allowed_domains = [
            ]
    start_urls = [
    ]
    start_url_info = {
            }
    COOKIE_DICT = {
        'SINAGLOBAL' : '4971205717884.004.1393911779672', 
        'YF-Ugrow-G0' : '57484c7c1ded49566c905773d5d00f82', 
        'YF-V5-G0' : '447063a9cae10ef9825e823f864999b0', 
        '_s_tentry' : 'login.sina.com.cn', 
        'Apache' : '6261490194592.625.1402967861121', 
        'ULV' : '1402967861127:168:30:6:6261490194592.625.1402967861121:1402881185085', 
        'YF-Page-G0' : '8fee13afa53da91ff99fc89cc7829b07', 
        'WBStore' : 'bb2de5c433b2dd4b|undefined', 
        'myuid' : '1931476475', 
        'login_sid_t' : '5926d2e3d0714222630b5c043419ec52', 
        'UOR' : ',,login.sina.com.cn', 
        'SUS' : 'SID-1931476475-1402997032-GZ-5wi2c-66b0ca6efde606467d64af6973e15954', 
        'SUE' : 'es%3D9b5cb293ecd8c3aafdf76db8329a8aba%26ev%3Dv1%26es2%3Dfef8abfcd4bab5abaca42511966a3415%26rs0%3Dw8JuyCSkDsqpJ%252BfG%252FWIsxIu7XW0Q45XcV7TVB3iUleON1pHay2J3JZDHmZZh5LNVaC0lO5rnfbjx6cLNvOmBs%252F4cf0EPhHbbY3HPsD2uvg7oEy%252FraXeKn64u97OEuSvuL6CRCniuTcjwzNJl0R%252FQRWbZ3I%252BtmF%252BKjZzwGGcA8bU%253D%26rv%3D0', 
        'SUP' : 'cv%3D1%26bt%3D1402997032%26et%3D1403083432%26d%3Dc909%26i%3D5954%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D0%26st%3D0%26uid%3D1931476475%26name%3Dsimon582%2540163.com%26nick%3Dsimon582%26fmp%3D%26lcp%3D2012-11-08%252022%253A23%253A09', 
        'SUB' : 'AU4G%2BvUMIHaUWAQHc7ROpic5A4vFNvzoBVSutS%2FXgkQNcTyCeRfHrPrP4ijP4E0Urwu7JKC0IO5SXEvFr69RnUF3GTrrVHrQGAW1MkMa0kiDIXjxdAuAi1jLjgZ7yHCv7DeiJJI44iLP8W3KsFmP%2FMM%3D',
        'SUBP' : '002A2c-gVlwEm1uAWxfgXELuuu1xVxBxAALnC_eF-N3Wup5vj9pylEwuHY-u_1%3D', 
        'ALF' : '1434533032', 
        'SSOLoginState' : '1402997032', 
        'un' : 'simon582@163.com'
    }
    show_info = False
    show_help = False
    gen_part_html = False
    
    def make_requests_from_url(self,url):
        if url.find('weibo') != -1:
            request = Request(url,cookies=self.COOKIE_DICT,callback=self.parse)
        else:
            request = Request(url, callback=self.parse)
        return request

    def set_default_conf(self, start_url_info):
        if not start_url_info.has_key('type'):
            start_url_info['type'] = u'其它'

    def load_conf(self, file_name):
        start_url_info_dict = {}
        file = open(file_name)
        start_url_info = {}
        while True:
            buffer = file.readline()
            if not buffer:
                break
            if buffer[0] == '#':
                continue
            if utils.has_prefix(buffer, 'start_url') and start_url_info.has_key('start_url'):
                start_url = start_url_info['start_url']
                self.set_default_conf(start_url_info)
                start_url_info_dict[start_url] = start_url_info
                start_url_info = {}

            content = buffer.strip()
            equal = content.find('=')
            if equal == -1:
                continue
            key = content[:equal]
            value = content[equal + 1:]
            #log.msg(('key = ' + key + ' value = ' + value), level = log.DEBUG)
            if value.strip() == '':
                value = None
            elif value == 'True':
                value = True
            elif value == 'False':
                value = False
            elif key == 'cat' or key == 'display_name' or key == 'type' or key == 'b2c_source' or key == 'crawl_location':
                value = value.decode('utf8')
            elif key == 'jump_count' or key == 'score' or key == 'crawl_priority' or key == 'reserve_days' or key == 'scroll_down_times':
                value = int(value)
            elif key == 'stat':
                value = int(value)
            elif key == 'xml_suffix' or key == 'filter_urls' or key == 'crawl_text_xpath_tags' or key == 'content_next_page_url_match':
                value = value.split(',')
            elif key == 'xpath_file':
                value = 'html/' + value
            if value != None:
                start_url_info[key] = value
        if start_url_info.has_key('start_url'):
            start_url = start_url_info['start_url']
            start_url_info_dict[start_url] = start_url_info
            self.set_default_conf(start_url_info)
        return start_url_info_dict

    def load_start_urls(self, file_name):
        start_urls = []
        file = open(file_name)
        while True:
            buffer = file.readline()
            if not buffer:
                break
            if buffer[0] == '#':
                continue
            else:
                start_url = buffer.strip()
                start_urls.append(start_url)
        return start_urls

    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        conf_name = 'start_url_info_new.conf'
        self.not_access_table = Table('content_db', 'not_access')
        if kwargs.get('conf'):
            conf_name = kwargs.get('conf')
        start_url_info_dict = self.load_conf(conf_name)
        if kwargs.get('start_url'):
            self.start_urls = [kwargs.get('start_url')]
        if kwargs.get('start_urls_file'):
            start_urls_file = kwargs.get('start_urls_file')
            self.start_urls = self.load_start_urls(start_urls_file)
        if kwargs.get('max_item'):
            self.max_item = int(kwargs.get('max_item'))
        if kwargs.get('max_pages'):
            self.max_pages = int(kwargs.get('max_pages'))
        if kwargs.get('show_info'):
            self.show_info = True
        if kwargs.get('show_help'):
            self.show_help = True
        if kwargs.get('gen_part_html'):
            self.gen_part_html = True
        for start_url in start_url_info_dict:
            self.start_url_info[start_url] = start_url_info_dict[start_url]
            if start_url_info_dict[start_url].has_key('domain_name'):
                self.allowed_domains.append(start_url_info_dict[start_url]['domain_name'])
        self.driver = None
        if self.show_info:
            for start_url in self.start_urls:
                if not self.start_url_info.has_key(start_url):
                    print 'start_url ' + start_url + ' :  not exist'
                else:
                    print 'start_url=' + start_url
                    for key in self.start_url_info[start_url]:
                        value = self.start_url_info[start_url][key]
                        if value.__class__.__name__ == 'bool' or value.__class__.__name__ == 'int':
                            value = str(value)
                        print (key + '=' + value).encode('utf8')
            sys.exit(-1)
        if self.show_help:
            self.usage()
            sys.exit(-1)
        self.gencat = GenCat()

    def usage(self):
        print 'scrapy crawl uniform'
        print '-a conf=start_url_info.conf'
        print '-a start_url=http://www.smzdm.com'
        print '-a start_urls_file=start_urls'
        print '-a max_item=500'
        print '-a max_pages=500'
        print '-a show_info=True'
        print '-a show_help=True'
        print '-a gen_part_html=True'

    def init_firefox(self):
        self.driver = utils.create_firefox()
        self.driver.set_page_load_timeout(60)
        self.driver.set_script_timeout(60)
        socket.setdefaulttimeout(60)

    def get_next_page_domain_name(self, url):
        index = url.rfind('/')
        return url[0:index]

    def get_domain_name(self, url):
        index = url.find('/', len('http://'))
        if index == -1:
            return url
        return url[0:index]

    def get_site_name(self, domain_name):
        if utils.has_prefix(domain_name, 'http://'):
            return domain_name[len('http://'):]
        return domain_name
    #return domain_name.strip('http://')

    def get_start_url_title(self, hxs, start_url):
        title = utils.get_one(hxs.select('//head/title/text()').extract())
        if title:
            print 'start_url display_name ' + str(start_url) + title.encode('utf8')
        return title.strip()

    def get_tree_attr(self, xpath_list, h, first_tag, is_xml):
        buffer = h.extract()
        tree = self.build_html_tree(buffer, first_tag, is_xml)
        attr_dict = {}
        for attr_info in xpath_list:
            attr_name = attr_info[0]
            xpath = attr_info[1]
            func = attr_info[2]
            default_value = attr_info[3]
            value = tree.select(xpath)
            if value:
                if func == 'strip':
                    value = value.strip()
                attr_dict[attr_name] = value
                log.msg(attr_name + ' [' + value.encode('utf8') + ']', level = log.DEBUG)
            else:
                log.msg(attr_name + ' [None]', level = log.DEBUG)
        return attr_dict

    def get_main_attr_xpath(self, start_url, hxs, response):
        #buffer = open('a.xml', 'r').read()
        #hxs = HtmlXPathSelector(text=buffer)
        use_indexpath = True
        if self.start_url_info[start_url].has_key('use_xpath') and self.start_url_info[start_url]['use_xpath']:
            use_indexpath = False
        main_xpath = self.start_url_info[start_url]['main_xpath']
        h_array = hxs.select(main_xpath)
        if len(h_array) > 0:
            html_code = h_array[0].extract()
            print 'start_url ' + start_url + ' html_code [' + html_code.encode('utf8') + ']'
            tree = self.build_html_tree(html_code, get_last_tag(main_xpath), utils.is_xml(response))
            xpath_dict = {}
            sub_xpath_list = tree.get_sub_xpath('', 0, xpath_dict)
            for key in xpath_dict:
                print 'xpath_dict ' + str(key) + ' ' + str(xpath_dict[key])
            sub_indexpath_list = tree.get_sub_indexpath('', 0, {}, 0)
            for item in sub_indexpath_list:
                print ('indexpath ' + item['xpath'] + ' [' + tree.select(item['xpath']) + ']').encode('utf8')

            if not self.start_url_info[start_url].has_key('xpath_file'):
                xpath_items = tree.get_main_attr_xpath(sub_xpath_list, h_array[0])
                attr_list = ['url', 'img', 'title', 'desc', 'date', 'express']
                type_list = ['string', 'string', 'strip', 'strip', 'strip', 'strip']
                for i in xrange(len(xpath_items)):
                    if not xpath_items[i]:
                        print 'start_url ' + start_url + ' '+ attr_list[i] + '_xpath ' + ''
                        if attr_list[i] == 'url' or attr_list[i] == 'title':
                            log.msg('failed to get_main_attr_xpath h_array no ' + attr_list[i], level = log.ERROR)
                            return None
                    elif xpath_items[i].has_key('text'):
                        print ('start_url ' + start_url + ' '+ attr_list[i] + '_xpath ' + xpath_items[i]['xpath'] + ' index ' + str(xpath_items[i]['index']) + ' text [' + xpath_items[i]['text'] + ']').encode('utf8')
                    else:
                        print 'start_url ' + start_url + ' '+ attr_list[i] + '_xpath ' + xpath_items[i]['xpath'] + ' index ' + str(xpath_items[i]['index'])
                xpath_list = []
                for i in xrange(len(xpath_items)):
                    if xpath_items[i]:
                        xpath_list_item = [attr_list[i], xpath_items[i]['xpath'], type_list[i], None, xpath_items[i]['index']]
                        xpath_list.append(xpath_list_item)
            elif use_indexpath :
                xpath_file = self.start_url_info[start_url]['xpath_file']
                file = open(xpath_file, 'r')
                buffer = file.read()
                last_tag = get_last_tag(main_xpath)
                tree_from_file = self.build_html_tree(buffer, last_tag, utils.is_xml(response))
                xpath_dict = tree.get_main_attr_indexpath_from_file(sub_xpath_list, xpath_file, last_tag, response, tree_from_file)
                xpath_list = []
                type_dict = {
                        'url' : 'string',
                        'img' : 'string',
                        'img2' : 'string',
                        'title' : 'strip',
                        'title2' : 'strip',
                        'desc' : 'strip',
                        'date' : 'strip',
                        'go_link' : 'strip',
                        'current_price' : 'strip',
                        'origin_price' : 'strip',
                        'discount' : 'strip',
                        'express' : 'strip'
                        }
                for attr in xpath_dict:
                    print 'start_url ' + start_url + ' attr ' + attr + ' xpath ' + xpath_dict[attr]['xpath']
                    type = type_dict[attr]
                    xpath_list_item = [attr, xpath_dict[attr]['xpath'], type, None]
                    xpath_list.append(xpath_list_item)
                
                attr_dict = self.get_tree_attr(xpath_list, h_array[0], last_tag, utils.is_xml(response))
                #if not attr_dict:
                #    log.msg('failed to get_main_attr_xpath attr_dict is None ', level = log.ERROR)
                #    return None

                self.start_url_info[start_url]['xpath_list'] =  xpath_list
                return self.start_url_info
            else:
                xpath_file = self.start_url_info[start_url]['xpath_file']
                xpath_dict = tree.get_main_attr_xpath_from_file(sub_xpath_list, xpath_file, get_last_tag(main_xpath), response)
                xpath_list = []
                type_dict = {
                        'url' : 'string',
                        'img' : 'string',
                        'img2' : 'string',
                        'title' : 'strip',
                        'title2' : 'strip',
                        'desc' : 'strip',
                        'date' : 'strip',
                        'go_link' : 'strip',
                        'current_price' : 'strip',
                        'origin_price' : 'strip',
                        'discount' : 'strip',
                        'express' : 'strip'
                        }
                for attr in xpath_dict:
                    print 'start_url ' + start_url + ' attr ' + attr + ' xpath ' + xpath_dict[attr]['xpath'] + ' index ' + str(xpath_dict[attr]['index'])
                    type = type_dict[attr]
                    xpath_list_item = [attr, xpath_dict[attr]['xpath'], type, None, xpath_dict[attr]['index']]
                    xpath_list.append(xpath_list_item)
                #return

            attr_dict = utils.get_attr(xpath_list, h_array[0])
            #if not attr_dict:
            #    log.msg('failed to get_main_attr_xpath attr_dict is None ', level = log.ERROR)
                #return None

            self.start_url_info[start_url]['xpath_list'] =  xpath_list
            return self.start_url_info

    def add_allow_domains(self, site_name):
        for domain in self.allowed_domains:
            if domain == site_name:
                return
        self.allowed_domains.append(site_name)
    
    def gen_start_url_info(self, start_url):
        if not self.start_url_info.has_key(start_url):
            self.start_url_info[start_url] = {}
        self.start_url_info[start_url]['next_page_domain_name'] = self.get_next_page_domain_name(start_url)
        self.start_url_info[start_url]['domain_name'] = self.get_domain_name(start_url)
        self.start_url_info[start_url]['site_name'] = self.get_site_name(self.start_url_info[start_url]['domain_name'])
        self.start_url_info[start_url]['start_url'] = start_url
        cat = self.start_url_info[start_url]['cat']
        #self.start_url_info[start_url]['main_category'] = utils.g_pingce_category[cat]
        self.start_url_info[start_url]['crawl_num'] = 0
        self.add_allow_domains(self.start_url_info[start_url]['site_name'])
        #self.start_url_info[start_url]['display_name'] = self.get_start_url_title(hxs, start_url)
    
    def next_page_by_content(self, response, next_page_xpath, next_page_content):
        hxs = HtmlXPathSelector(response)
        h_array = hxs.select(next_page_xpath)
        for h in h_array:
            text = utils.get_one(h.select('text()').extract())
            if text and text.strip() == next_page_content:
                log.msg('next_page text hit [' + text.encode('utf8') + ']', level = log.DEBUG)
                url = utils.get_one(h.select('@href').extract())
                return url
        return None

    def next_page_by_contents(self, response, next_page_xpath, next_page_content_list):
        for next_page_content in next_page_content_list:
            url = self.next_page_by_content(response, next_page_xpath, next_page_content)
            if url:
                return url
        return None

    def get_content_page_url(self, response, origin_url, start_url_info):
            if not utils.valid_url(origin_url):
                return None
            #if origin_url.find('#') != -1:
                #return None
            if start_url_info.has_key('url_prefix'):
                url_prefix = start_url_info['url_prefix']
            elif origin_url[0] == '/':
                url_prefix = start_url_info['domain_name']
            else:
                url_prefix = self.get_next_page_domain_name(response.url)
            content_url = utils.get_url_by_domain(origin_url.strip(), url_prefix)
            return content_url
                
    def get_next_page_url(self, response, next_page, start_url_info):
        if start_url_info.has_key('content_next_page_url_match'):
            content_next_page_url_match = [str(next_page)]
            for item in start_url_info['content_next_page_url_match']:
                content_next_page_url_match.append(item.decode('utf8'))
        else:
            content_next_page_url_match = [u'下一页', u'>', str(next_page)]
        next_url = self.next_page_by_contents(response, '//a', content_next_page_url_match)
        return self.get_content_page_url(response, next_url, start_url_info)
        '''
        if next_url:
            if not utils.valid_url(next_url):
                return None
            if next_url.find('#') != -1:
                return None
            if next_url[0] == '/':
                next_url = utils.get_url_by_domain(next_url, start_url_info['domain_name'])
            else:
                next_page_domain_name = self.get_next_page_domain_name(response.url)
                next_url = utils.get_url_by_domain(next_url, next_page_domain_name)
        return next_url
        '''

    def get_complete_url(self, start_url, url):
        domain_name = self.start_url_info[start_url]['domain_name']
        return utils.get_url_by_domain(url, domain_name)

    def build_html_tree(self, html_code, root_tag = 'body', is_xml = False):
        if is_xml:
            #soup = BeautifulSoup(html_code, 'xml')
            soup = BeautifulSoup(html_code)
        else:
            soup = BeautifulSoup(html_code)
        if root_tag:
            body = soup.find(root_tag)
        else:
            body = soup
        return self.build_sub_tree(body)

    def build_sub_tree(self, node):
        if not node or node == '\n' or not hasattr(node, 'contents'):
            return None
        if not hasattr(node, 'contents'):
            return TreeNode(node, [], None)
        children = []
        if node.contents == None:
            return None
        print 'node name ' + node.name + ' contents ' + str(len(node.contents))
        for child in node.contents:
            sub_tree = self.build_sub_tree(child)
            if sub_tree:
                children.append(sub_tree)
        tree = TreeNode(node, children, None)
        for child in tree.children:
            child.parent = tree
        return tree

    def get_main_xpath(self, response):
        if utils.has_prefix(response.body, '<?xml'):
            tree = self.build_html_tree(response.body, '//rss', is_xml = True)
        else:
            tree = self.build_html_tree(response.body)
        hxs = utils.get_xpath_selector(response)
        max, max_tag, max_xpath = tree.get_max_tag(hxs)
        max_xpath = '//' + max_xpath
        print 'max ' + str(max) + ' max_tag ' + str(max_tag) + ' max_xpath ' + max_xpath + ' start_url ' + response.url

    def is_xml_url(self, url, xml_suffix_list):
        for suffix in xml_suffix_list:
            if utils.has_suffix(url, suffix):
                return True
        return False

    def get_urls(self, response, start_url):
        hxs = utils.get_xpath_selector(response)
        urls = hxs.select('//a/@href').extract()
        ret_urls = []
        for url in urls:
            if self.start_url_info[start_url].has_key('xml_suffix') and not self.is_xml_url(url, self.start_url_info[start_url]['xml_suffix']):
                continue
            if not self.start_url_info[start_url].has_key('xml_suffix') and not utils.has_suffix(url, u'.xml') and not utils.has_suffix(url, u'.shtml'):
                continue
            log.msg(('source_url ' + response.url + ' url ' + url).encode('utf8'), level = log.DEBUG)
            ret_urls.append(url)
        return ret_urls

    def is_content_page(self, response):

        text_list = parser_content(response.url)
        for i in xrange(len(text_list)):
            print ('url ' + response.url + ' p ' + str(i) + ' ' + str(len(text_list[i][1])) + ' ' + text_list[i][1]).encode('utf8')
        is_content_webpage(response.body)

    def remove_article_header(self, cur_str):
        dr = re.compile(r'【[^】]+\]',re.S)
        desc_str = dr.sub('',cur_str)
        change = False
        if len(desc_str) != len(cur_str):
            infos = 'content after remove expression [' + str(desc_str.encode('utf8')) + '] origin [' + str(cur_str.encode('utf8')) + ']'
            log.msg(infos, level = log.DEBUG)
            print infos
            change = True
        return desc_str

    def gen_new_title(self, prod, current_price, origin_price, start_url_info):
        if current_price and prod.has_key('title'):
            title = prod['title']
            if title.find(u'【') != -1 and title.find(u'】') != -1:
                title = title.split(u'【')[1].split(u'】')[1]
            flush_str = u' 现价 ' + "%.2f"%(float(current_price)/float(100)) + u'元'
            if origin_price:
                flush_str = flush_str + u'  原价' + "%.2f"%(float(origin_price)/float(100)) + u'元'
            flush_str = flush_str.replace(' ', '')
            new_title = self.remove_article_header(title) + flush_str
            new_title = new_title.replace(' ', '')
            #if start_url_info.has_key('b2c_source'):
                #new_title = start_url_info['b2c_source'] + u' ' + new_title
            prod['title'] = new_title
            prod['flush'] = [flush_str]

    def match_string(self, date_str, i, total_len):
        time_str = [ u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9',
                u'-', u' ', u':', u'/', u',',
                u'秒钟前', u'分钟前', u'小时前',u'天前', u'周前', u'个月前', u'年前',  
                u'年', u'月', u'日', u'上午', u'下午',
                u'今天', u'昨天', u'前天',
                ]
        end = False
        for sub_time_str in time_str:
            if i + len(sub_time_str) <= total_len:
                sub_str = date_str[i:i + len(sub_time_str)]
            else:
                continue
            if sub_str != sub_time_str:
                continue
            else:
                if sub_time_str == u'秒钟前' or sub_time_str == u'分钟前' or sub_time_str == u'小时前' or sub_time_str == u'天前' or sub_time_str == u'周前' or sub_time_str == u'个月前' or sub_time_str == u'年前':
                    end = True
                return len(sub_time_str), end
        return 0, end

    def get_valid_date_str(self, date_str):
        i = 0
        start = -1
        end = 0
        total_len = len(date_str)
        prev_match_len = 0
        max_match_len = 0
        max_match_string = None
        while i < total_len:
            match_len, is_end = self.match_string(date_str, i, total_len)
            if match_len > 0:
                if prev_match_len == 0:
                    start = -1
                if start < 0:
                    start = i
                end = i + match_len
                i = i + match_len
                prev_match_len = match_len
                if is_end:
                    break
            else:
                if prev_match_len > 0:
                    if max_match_len < end - start:
                        max_match_len = end - start
                        max_match_string = date_str[start:end]
                i = i + 1
                prev_match_len = match_len
        if start == -1:
            return None
        if max_match_len < end - start:
            max_match_len = end - start
            max_match_string = date_str[start:end]
        return max_match_string.strip()

    def general_gen_time(self, date_str, time_format):
        if utils.has_prefix(time_format, 'noyear_format_'):
            now_year = datetime.datetime.now().year
            new_date_str = str(now_year) + ' ' + date_str
            new_time_format = "%Y " + time_format[len('noyear_format_'):]
            return self.general_gen_time(new_date_str, new_time_format)
        elif utils.has_prefix(time_format, 'text_format_'):
            new_date_str = self.get_valid_date_str(date_str)
            new_time_format = time_format[len('text_format_'):]
            log.msg('text_format_ new_date_str [' + new_date_str.encode('utf8') + ']', level = log.DEBUG)
            return self.general_gen_time(new_date_str, new_time_format)
        elif utils.has_prefix(time_format, 'before_format_'):
            info_dict = {
                    u'秒钟前' : 60,
                    u'分钟前' : 60,
                    u'小时前' : 3600,
                    u'天前' : 86400,
                    u'周前' : 604800,
                    u'个月前' : 2592000,
                    u'年前' : 31536000,
                    }
            for key in info_dict:
                before_seconds = info_dict[key]
                index = date_str.find(key)
                if index >= 0:
                    seconds = int(date_str.replace(key, '')) * before_seconds
                    return int(time.time()) - seconds
            new_date_str = date_str
            new_time_format = time_format[len('before_format_'):]
            return self.general_gen_time(new_date_str, new_time_format)
        elif utils.has_prefix(time_format, 'today_format_'):
            info_dict = {
                    u'今天' : 0,
                    u'昨天' : 1,
                    u'前天' : 2,
                    }
            for key in info_dict:
                index = date_str.find(key)
                before_days = info_dict[key]
                if index >= 0:
                    new_date_str = str(((datetime.datetime.now()) - datetime.timedelta(days=before_days)).date()) + ' ' + date_str[index + len(key):]
                    new_time_format = "%Y-%m-%d %H:%M"
                    return self.general_gen_time(new_date_str, new_time_format)
            new_date_str = date_str
            new_time_format = time_format[len('today_format_'):]
            return self.general_gen_time(new_date_str, new_time_format)
        else:
            #date_str=date_str.replace(u'')
            return self.gen_time(date_str, time_format)

    def gen_time(self, date_str, time_format):
        zh_to_en = [
                ['星期一' , 'Mon'],
                ['星期二' , 'Tue'],
                ['星期三' , 'Wed'],
                ['星期四' , 'Thu'],
                ['星期五' , 'Fri'],
                ['星期六' , 'Sat'],
                ['星期日' , 'Sun'],
                ['十一月' , 'Nov'],
                ['十二月' , 'Dec'],
                ['一月' , 'Jan'],
                ['二月' , 'Feb'],
                ['三月' , 'Mar'],
                ['四月' , 'Apr'],
                ['五月' , 'May'],
                ['六月' , 'Jun'],
                ['七月' , 'Jul'],
                ['八月' , 'Aug'],
                ['九月' , 'Sep'],
                ['十月' , 'Oct'],
                ['年' , '-'],
                ['月' , '-'],
                ['日' , ' '],
                ['点' , ':'],
                ['分' , ' '],
                ['上午' , 'AM'],
                ['下午' , 'PM'],
                ['　', ' '],
                ['：', ':'],
                ]
        for key_value in zh_to_en:
            key = key_value[0]
            value = key_value[1]
            date_str = date_str.replace(key.decode('utf8'), value.decode('utf8'))
        try:
            date_str = date_str.replace(u'\xa0', u' ')
            gen_time = int(datetime.datetime.strptime(date_str.strip(), time_format).strftime("%s"))
        except:
            exstr = traceback.format_exc()
            log.msg('failed to format time_str [' + date_str.encode('utf8') + '] time_format [' + time_format + '] '+ exstr, level = log.WARNING)
            return None
        return gen_time

    def get_id_crawl_url(self, attr_dict, start_url):
        if self.start_url_info[start_url].has_key('no_url') and self.start_url_info[start_url]['no_url']:
            if attr_dict.has_key('desc'):
                id = hashlib.md5(attr_dict['desc'].encode('utf8')).hexdigest().upper()
            else:
                return None, None
            crawl_url = start_url
        elif not attr_dict.has_key('url'):
            return None, None
        elif attr_dict['url'] == None:
            return None, None
        else:
            id = hashlib.md5(attr_dict['url']).hexdigest().upper()
            crawl_url = attr_dict['url']
        return id, crawl_url

    def is_not_access(self, attr_dict, start_url):
        id, crawl_url = self.get_id_crawl_url(attr_dict, start_url)
        if not id:
            log.msg('skip in not access no id ', level = log.DEBUG)
            return True
        if self.not_access_table.query(id):
            log.msg('skip in not access id ' + id, level = log.DEBUG)
            return True
        return False

    def gen_desc(self, prod):
        if prod.has_key('crawl_text') and not prod.has_key('desc'):
            desc = None
            for text_item in prod['crawl_text']:
                if text_item[0] == '1':
                    if not desc:
                        desc = text_item[1]
                    else:
                        desc = desc + text_item[1]
                    if len(desc) > 70:
                        break
            if desc:
                prod['desc'] = desc
                log.msg('gen desc ' + desc.encode('utf8'), level = log.DEBUG)

    def gen_desc_img(self, prod):
        if prod.has_key('crawl_text') and not prod.has_key('crawl_desc_img'):
            desc_img = None
            for text_item in prod['crawl_text']:
                if text_item[0] == '0':
                    desc_img = text_item[1]
                    break
            if desc_img:
                prod['crawl_desc_img'] = desc_img
                log.msg('gen crawl_desc_img ' + desc_img.encode('utf8'), level = log.DEBUG)

    def get_prod(self, start_url, attr_dict, text_list):
        prod = UniformItem()
        id, crawl_url = self.get_id_crawl_url(attr_dict, start_url)
        if not id:
            return None
        prod['id'] = id
        prod['crawl_url'] = crawl_url
        
        if self.start_url_info[start_url].has_key('b2c_source') and self.start_url_info[start_url]['b2c_source'] == u'amazon':
            prod['intro_list'] = attr_dict['intro_list']
            prod['img'] = attr_dict['img']
            prod['desc_text'] = attr_dict['desc_text']
            prod['asin'] = attr_dict['asin']
        
        if self.start_url_info[start_url].has_key('b2c_source') and self.start_url_info[start_url]['b2c_source'] == u'shikee':
            prod['crawl_text'] = attr_dict['crawl_text']
            prod['source_price'] = attr_dict['origin_price']
            prod['sample_cnt'] = attr_dict['sample_cnt']
            prod['apply_cnt'] = attr_dict['apply_cnt']
            prod['quality_cnt'] = attr_dict['quality_cnt']
            prod['obtain_cnt'] = attr_dict['obtain_cnt'] 
        
        if self.start_url_info[start_url].has_key('b2c_source') and self.start_url_info[start_url]['b2c_source'] == u'taobao':
            try:
                tot_url = crawl_url
                if attr_dict.has_key('go_link'):
                    tot_url += attr_dict['go_link']
                if attr_dict.has_key('url'):
                    tot_url += attr_dict['url']
                if tot_url.find('taobao') == -1:
                    log.msg('This is not a taobao url: ' + tot_url, level = log.DEBUG)
                    return
                match = re.search("\d{11}", tot_url)
                good_id = match.group()
                prod['good_id'] = good_id
            except:
                log.msg('Cannot get good_id in taobao: ' + tot_url, level = log.WARNING)
                #prod['good_id'] = id
            if attr_dict.has_key('express') and (attr_dict['express'] == u'包邮' or attr_dict['express'] == u'0' or attr_dict['express'] == 1):
                prod['express_status'] = 1
            elif attr_dict.has_key('title') and attr_dict['title'].find(u'包邮') != -1:
                prod['express_status'] = 1
            else:
                prod['express_status'] = 0
            if attr_dict.has_key('desc_score'):
                prod['desc_score'] = attr_dict['desc_score']
            if attr_dict.has_key('service_score'):
                prod['service_score'] = attr_dict['service_score']
            if attr_dict.has_key('deliver_score'):
                prod['deliver_score'] = attr_dict['deliver_score']
        prod['crawl_source'] = self.start_url_info[start_url]['display_name']
        if self.start_url_info[start_url].has_key('title'):
            title = self.start_url_info[start_url]['title']
        elif not attr_dict.has_key('title'):
            url = 'None'
            if attr_dict.has_key('url'):
                url = attr_dict['url']
            log.msg('url ' + url + ' no title', level = log.WARNING)
            #return None
            title = None
        else:
            title = attr_dict['title']
        if title:
            prod['title'] = title
        if attr_dict.has_key('title2'):
            prod['title'] += ' ' + attr_dict['title2']
        elif self.start_url_info[start_url]['type'] == u'微博' and attr_dict.has_key('desc'):
            title_from_desc, content = utils.get_title_from_weibo(attr_dict['desc'], id)
            if title_from_desc:
                prod['title'] = title_from_desc
        if attr_dict.has_key('desc'):
            if self.start_url_info[start_url].has_key('add_desc_in_title') and self.start_url_info[start_url]['add_desc_in_title']:
                prod['title'] = u'【' + attr_dict['desc'] + u'】' + prod['title']
            else:
                prod['desc'] = attr_dict['desc'].replace('\n',' ').replace('\r',' ')
        #prod['cat'] = self.start_url_info[start_url]['cat']
        self.gencat.handle(prod, self.start_url_info[start_url])
        log.msg('gencat ' + prod['cat'], level = log.DEBUG)
        if attr_dict.has_key('img'):
            img = attr_dict['img']
        elif attr_dict.has_key('img2'):
            img = attr_dict['img2']
        else:
            img = None
        if img:
            prod['crawl_desc_img'] = img
            if self.start_url_info[start_url].has_key('img_rgexp') and self.start_url_info[start_url].has_key('img_rptext'):
                prod['crawl_desc_img'] = prod['crawl_desc_img'].replace(self.start_url_info[start_url]['img_rgexp'], self.start_url_info[start_url]['img_rptext'])
            if self.start_url_info[start_url]['type'] == u'微博':
                prod['crawl_desc_img'] = prod['crawl_desc_img'].replace('thumbnail','bmiddle')
        if self.start_url_info[start_url].has_key('taobao_item_id_regex'):
            taobao_item_id_regex = self.start_url_info[start_url]['taobao_item_id_regex']
            taobao_item_id = utils.get_regex_value(crawl_url, taobao_item_id_regex)
            pic_url = utils.get_pic_url(taobao_item_id)
            if pic_url:
                prod['crawl_desc_img'] = pic_url
                log.msg("taobao pic url " + pic_url, level = log.DEBUG)

        #prod['main_category'] = self.start_url_info[start_url]['main_category']
        #prod['pub_time'] =  str(datetime.datetime.now())[:19]
        if attr_dict.has_key('pub_time_int'):
            prod['pub_time'] = attr_dict['pub_time_int']
        else:
            prod['pub_time'] =  int(time.time())
        if text_list:
            prod['crawl_text'] = text_list
        else:
            if prod.has_key('desc'):
                prod['crawl_text'] = []
                prod['crawl_text'].append(['1', prod['desc']])
            if prod.has_key('crawl_desc_img'):
                if not prod.has_key('crawl_text'): 
                    prod['crawl_text'] = []
                prod['crawl_text'].append(['0', prod['crawl_desc_img']])

        current_price = None
        origin_price = None
        discount = None
        if attr_dict.has_key('current_price'):
            current_price = utils.get_float_str_to_fen(attr_dict['current_price'])
            if attr_dict.has_key('origin_price'):
                origin_price = utils.get_float_str_to_fen(attr_dict['origin_price'])
                if origin_price:
                    discount = utils.get_discount(current_price, origin_price)
        if current_price:
            prod['cur_price'] = current_price
            log.msg('current price ' + str(current_price), level = log.DEBUG)
        if origin_price:
            prod['source_price'] = origin_price
            log.msg('origin price ' + str(origin_price), level = log.DEBUG)
        if discount:
            #prod['discount'] = discount
            log.msg('discount ' + str(discount), level = log.DEBUG)
        if self.start_url_info[start_url].has_key('stat'):
            prod['stat'] = self.start_url_info[start_url]['stat']
        else:
            prod['stat'] = utils.STAT_NEW
        if attr_dict.has_key('go_link') and self.start_url_info[start_url]['type'] == u'商品':
            prod['crawl_go_link'] = utils.get_url_by_domain(attr_dict['go_link'], self.start_url_info[start_url]['domain_name'])
        elif (self.start_url_info[start_url].has_key('same_url') and self.start_url_info[start_url]['type'] == u'商品') or self.start_url_info[start_url].has_key('b2c_source'):
            prod['crawl_go_link'] = prod['crawl_url']
        if self.start_url_info[start_url].has_key('score'):
            prod['score'] = self.start_url_info[start_url]['score']
        else:
            prod['score'] = 1
        #prod['type'] = 1
        self.gen_new_title(prod, current_price, origin_price, self.start_url_info[start_url])
        type = utils.TYPE_OTHER
        if self.start_url_info[start_url].has_key('type'):
            type_str = self.start_url_info[start_url]['type']
            if utils.type_to_id.has_key(type_str):
                type = utils.type_to_id[type_str]
            else:
                log.msg(('unknown type [' + type_str + ']').encode('utf8'), level = log.ERROR)
        prod['type'] = type
        if self.start_url_info[start_url].has_key('crawl_location'):
            prod['crawl_location'] = self.start_url_info[start_url]['crawl_location']
        self.gen_desc(prod)
        #self.gen_desc_img(prod)
        log.msg('get_prod id ' + str(id) + ' ' + prod['crawl_source'].encode('utf8'), level = log.INFO)
        return prod

    def filtered_urls(self, url, start_url):
        if self.start_url_info[start_url].has_key('filter_urls'):
            for pattern in self.start_url_info[start_url]['filter_urls']:
                if url.find(pattern) != -1:
                    return True
        return False

    def parser_content_with_xpath(self, html, main_xpath, start_url):
        hxs = HtmlXPathSelector(text=html)
        html_item_array = hxs.select(main_xpath).extract()
        rt_result = []
        xpath_tags = None
        if self.start_url_info[start_url].has_key('crawl_text_xpath_tags'):
            xpath_tags = self.start_url_info[start_url]['crawl_text_xpath_tags']
        for html_item in html_item_array:
            if self.start_url_info[start_url].has_key('crawl_table_in_text') and self.start_url_info[start_url]['crawl_table_in_text']:
                crawl_table = True
            else:
                crawl_table = False
            if not crawl_table and html_item.find('<table') != -1:
                log.msg('skip because of having table', level = log.WARNING)
                return None
            tree = self.build_html_tree(html_item, get_last_tag(main_xpath), is_xml = False)
            if self.start_url_info[start_url].has_key('img_tag'):
                img_tag = self.start_url_info[start_url]['img_tag']
            else:
                img_tag = None
            rt_result.extend(tree.get_text(xpath_tags, img_tag, self.start_url_info[start_url]))
        return rt_result
        #rt_result = parser_content_from_buffer(u'<html><body>' + html_item + u'</body></html>')
        #return rt_result

    def same_content(self, rt_result1, rt_result2):
        if len(rt_result1) != len(rt_result2):
            return False
        for i in xrange(len(rt_result1)):
            if rt_result1[i][0] != rt_result2[i][0]:
                return False
            if rt_result1[i][1] != rt_result2[i][1]:
                return False
        return True

    def parse_all_pages_with_xpath(self, response, main_xpath, start_url, next_xpath):
        if not utils.get_url_by_browser(self.driver, response.url):
            return
        prev_rt_result = []
        total_rt_result = []
        while True:
            html_source = self.driver.page_source
            rt_result = self.parser_content_with_xpath(html_source, main_xpath, start_url)
            response = response.replace(body = html_source)
            next_obj = self.driver.find_element_by_xpath(next_xpath)
            utils.click_a_obj(self.driver, next_obj)
            if self.same_content(prev_rt_result, rt_result):
                break
            total_rt_result.extend(rt_result)
            prev_rt_result = rt_result
        return total_rt_result

    def jump_url(self, start_url, attr_dict):
        curr_jump = 0
        while curr_jump < self.start_url_info[start_url]['jump_count']:
            curr_jump += 1
            try:
                f = urllib2.urlopen(attr_dict['url'], timeout=15)
                #html = unicode(f.read(), "gb2312")
                temp_file = open('temp.html','w')
                html = f.read()
                print >> temp_file, html
                f.close()
            except:
                log.msg("Cannot open url:"+attr_dict['url'], level = log.ERROR)
                return
            
            hxs = HtmlXPathSelector(text=html)
            url_list = hxs.select(self.start_url_info[start_url]['jump_xpath']).extract()
            if url_list:
                attr_dict['url'] = url_list[0].strip()
            else:
                try:
                    request = urllib2.Request(attr_dict['url'])
                    request.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6')
                    opener = urllib2.build_opener()
                    f = opener.open(request)
                    attr_dict['url'] = f.url
                    html = f.read()
                    print >> temp_file, html
                    f.close()
                    hxs = HtmlXPathSelector(text=html)
                    url_list = hxs.select(self.start_url_info[start_url]['jump_xpath']).extract()
                    if url_list:
                        attr_dict['url'] = url_list[0].strip()
                except:
                    return
                    
        
        if attr_dict['url'].find('redirect.simba.taobao.com') != -1:
            try:
                request = urllib2.Request(attr_dict['url'])
                request.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6')
                opener = urllib2.build_opener()
                f = opener.open(request)
                attr_dict['url'] = f.url
            except:
                log.msg("Cannot convert the url:" + attr_dict['url'], level = log.ERROR)
                return
        return
 
    def parse_taobao_dsr_content(self, response):
        start_url = response.meta['start_url']
        attr_dict = response.meta['attr_dict']
        hxs = HtmlXpathSelector(text=response.body)
        return

    def parse_amazon_content(self, response, start_url_info, start_url, attr_dict):
        hxs = HtmlXPathSelector(text=response.body)
        intro_xpath = '//ul[@class="a-vertical a-spacing-none"]/li/span/text()'
        intro_list = hxs.select(intro_xpath).extract()
 
        asin = ''
        eq = response.url.find('dp/')
        if eq == -1:
            eq = response.url.find('ws/')
        if eq != -1:
            asin = response.url[eq+3:eq+13]

        text = ''
        text_xpath = '//*[@class="productDescriptionWrapper"]/text()'
        text_list = hxs.select(text_xpath).extract()
        if text_list:
            text = text_list[0].strip()
        text_xpath = '//*[@class="productDescriptionWrapper"]/p/text()'
        text_list = hxs.select(text_xpath).extract()
        if text_list:
            for elem in text_list:
                text += elem.strip()
        text = text.replace('\n', '<br>')
        text = text.replace(r'<[^>]+>', '')
 
        img1 = img2 = img3 = ''
        equal = response.body.find('hiRes')
        if equal != -1:
            img_text = response.body[equal+8:equal+2000]
            ed = img_text.find('"')
            if ed != -1:
                img1 = img_text[:ed]
                if img1 == 'ull,':
                    equal = img_text.find('large')
                    if equal != -1:
                        img_text = img_text[equal+8:]
                    ed = img_text.find('"')
                    if ed != -1:
                        img1 = img_text[:ed]

        try:        
            equal = img_text.find('hiRes')
            if equal != -1:
                img_text = img_text[equal+8:]
                ed = img_text.find('"')
                if ed != -1:
                    img2 = img_text[:ed]
                    if img2 == 'ull,':
                        equal = img_text.find('large')
                        if equal != -1:
                            img_text = img_text[equal+8:]
                        ed = img_text.find('"')
                        if ed != -1:
                            img2 = img_text[:ed]
        
            equal = img_text.find('hiRes')
            if equal != -1:
                img_text = img_text[equal+8:]
                ed = img_text.find('"')
                if ed != -1:
                    img3 = img_text[:ed]
                    if img3 == 'ull,':
                        equal = img_text.find('large')
                        if equal != -1:
                            img_text = img_text[equal+8:]
                        ed = img_text.find('"')
                        if ed != -1:
                            img3 = img_text[:ed]
        except:
            print 'Cannot get img'
        
        attr_dict['intro_list'] = intro_list
        attr_dict['asin'] = asin
        attr_dict['img'] = [img1, img2, img3]
        attr_dict['desc_text'] = text       

    def parse_shikee_content(self, response, start_url_info, start_url, attr_dict):
        attr_dict['url'] = response.url
        # get hxs object
        hxs = HtmlXPathSelector(text=response.body)
        
        price_xpath = '//li[@class="tryGuaranteeMoney"]/em[@class="specialFont"]/text()'
        price_list = hxs.select(price_xpath).extract()
        if price_list:
            attr_dict['origin_price'] = price_list[0]

        sample_cnt_xpath = '//li[@class="tryGoodsNum"]/em[@class="specialFont"]/text()'
        sample_cnt_list = hxs.select(sample_cnt_xpath).extract()
        if sample_cnt_list:
            attr_dict['sample_cnt'] = sample_cnt_list[0]
        
        go_link_xpath = '//a[@class="tb-shop"]/@href'
        go_link_list = hxs.select(go_link_xpath).extract()
        if go_link_list:
            attr_dict['go_link'] = go_link_list[0]

        people_cnt_xpath = '//ul[@class="tshow-info-cont-info-list"]/li[5]/em/text()'
        people_cnt_list = hxs.select(people_cnt_xpath).extract()
        if people_cnt_list:
            attr_dict['apply_cnt'] = people_cnt_list[0]
            attr_dict['quality_cnt'] = people_cnt_list[1]
            attr_dict['obtain_cnt'] = people_cnt_list[2]
 
        rt_result = self.parser_content_with_xpath(response.body, self.start_url_info[start_url]['crawl_text_xpath'], start_url)
        text_list = []
        text_list.extend(rt_result)
        attr_dict['crawl_text'] = text_list

    def parse_taobao_content(self, response, start_url_info, start_url, attr_dict):
        # judge the response url illegal
        if response.url.find('alisec') != -1 or response.url.find('s.click.taobao') != -1:
            return
        attr_dict['url'] = response.url
        # get hxs object
        hxs = HtmlXPathSelector(text=response.body)
        
        origin_price_xpath = '//em[@class="tb-rmb-num"]/text()|//strong[@class="J_originalPrice"]/text()'
        origin_price_list = hxs.select(origin_price_xpath).extract()
        if origin_price_list:
            attr_dict['origin_price'] = origin_price_list[0]
        
        promotion_xpath = '//div[@id="J_PointTxt"]/em'
        promotion_list = hxs.select(promotion_xpath).extract()
        if promotion_list:
            promotion = promotion_list[0]
            attr_dict['promotion'] = promotion_list[0]

        score_xpath = '//em[@class="count"]/text()|//div[@class="tb-shop-rate"]/dl/dd/a/text()'
        score_list = hxs.select(score_xpath).extract()
        if score_list and len(score_list) > 2:
            attr_dict['desc_score'] = int(float(score_list[0])*10)    
            attr_dict['service_score'] = int(float(score_list[1])*10)    
            attr_dict['deliver_score'] = int(float(score_list[2])*10)    
            
        #express_xpath = '//span[@class="tb-carriage"]/span/text()|//div[@class="tb-postAge-info"]/p/span/text()'
        #express_list = hxs.select(express_xpath).extract()
        #if express_list:
        #    if express_list[0].find('免运费') != -1 or express_list[0].find('0.00') != -1:
        #        attr_dict['express'] = 1

        dsr_xpath = '//div[@class="shop-rate"]/ul/li/a'
        dsr_url_list = hxs.select(dsr_xpath).extract()
        if dsr_url_list:
            dsr_url = dsr_url_list[0]
            match = re.search('http[^"]+', dsr_url)
            dsr_url = match.group()
            #yield Request(url = dsr_url, callback=self.parse_taobao_dsr_content, meta={'start_url' : start_url, 'attr_dict' : attr_dict})
        return

    def parse_content_page(self, response):
        start_url = response.meta['start_url']
        first_page_url = response.meta['first_page_url']
        if self.start_url_info[start_url].has_key('browser_content') and self.start_url_info[start_url]['browser_content']:
            if not self.driver:
                self.init_firefox()
            if not utils.get_url_by_browser(self.driver, response.url):
                return
            main_xpath = self.start_url_info[start_url]['main_xpath']
            li_obj_array = self.driver.find_elements_by_xpath(main_xpath)
            print 'li_obj_array ' + str(len(li_obj_array))
            html_source = self.driver.page_source
            #response._body = html_source
            response = response.replace(body = html_source)
            utils.write_file(self.start_url_info[start_url]['site_name'] + ".1.firefox.html", response._body)
        #self.is_content_page(response)
        page = response.meta['page']
        attr_dict = response.meta['attr_dict']
        if self.start_url_info[start_url].has_key('crawl_text_encoding'):
            encoding = self.start_url_info[start_url]['crawl_text_encoding']
            response._body = response._body.decode(encoding).encode('utf8')
        utils.write_file(self.start_url_info[start_url]['site_name'] + '.' + str(page) + ".html", response._body)
        if response.meta.has_key('text_list'):
            text_list = response.meta['text_list']
        else:
            text_list = []
        parse_all_pages = False
        if self.start_url_info[start_url].has_key('crawl_text_content'):
            if self.start_url_info[start_url]['crawl_text_content'] == 'crawl_text_by_xpath':
                if self.start_url_info[start_url].has_key('crawl_text_js_next_button'):
                    next_xpath = self.start_url_info[start_url]['crawl_text_js_next_button']
                    parse_all_pages = True
                    rt_result = self.parse_all_pages_with_xpath(response, self.start_url_info[start_url]['crawl_text_xpath'], start_url, next_xpath)
                else:
                    rt_result = self.parser_content_with_xpath(response.body, self.start_url_info[start_url]['crawl_text_xpath'], start_url)
                if not rt_result:
                    return
                text_list.extend(rt_result)
                #text_list.extend(self.parser_content_with_xpath(response.body, self.start_url_info[start_url]['crawl_text_xpath'], start_url))
            elif self.start_url_info[start_url]['crawl_text_content'] == 'crawl_taobao_feature':
                self.parse_taobao_content(response, self.start_url_info[start_url], start_url, attr_dict)
            elif self.start_url_info[start_url]['crawl_text_content'] == 'crawl_shikee_feature':
                self.parse_shikee_content(response, self.start_url_info[start_url], start_url, attr_dict)
            elif self.start_url_info[start_url]['crawl_text_content'] == 'crawl_amazon_feature':
                self.parse_amazon_content(response, self.start_url_info[start_url], start_url, attr_dict)
            else:
                log.msg('wrong crawl_text option', level = log.ERROR)
        else:
            text_list.extend(parser_content(response.url))
        next_url = self.get_next_page_url(response, page + 1, self.start_url_info[start_url])
        ret_items = []
        if next_url and next_url != start_url and next_url != first_page_url and not parse_all_pages:
            log.msg('content_page next_url ' + next_url.encode('utf8') + ' start url ' + start_url + ' current_url ' + response.url, level = log.DEBUG)
            ret_items.append(Request(url = next_url, callback=self.parse_content_page, meta={'start_url' : start_url, 'attr_dict' : attr_dict, 'page': page + 1, 'text_list' : text_list, 'first_page_url' : first_page_url}))
        else:
            log.msg('content_page next_url None for start url ' + start_url)
            if len(text_list) == 0:
                log.msg('text_list len == 0', level = log.DEBUG)
            para_count = 0
            pre_content = ""
            new_text_list = []
            for item in text_list:
                try:
                    if not item:
                        log.msg('not item', level = log.DEBUG)
                        continue
                    if len(item) < 2:
                        log.msg('text_list item < 2 ' + str(item), level = log.DEBUG)
                    elif item[1] == pre_content:
                        log.msg('detect duplicated content', level = log.DEBUG)
                        continue
                    elif item[0] == '1' and utils.need_filter(item[1], utils.filter_content_list):
                        log.msg('filter by content info', level = log.WARNING)
                        return None
                    elif item[0] == '1' and (item[1].find(u'推荐阅读') != -1 or item[1].find(u'更多精彩推荐') != -1):
                        break
                    elif item[0] == '1' and not utils.need_filter(item[1], utils.filter_common_list):
                        item[1] = item[1].strip()
                        new_text_list.append(item)
                    elif item[0] == '0':
                        item[1] = item[1].strip()
                        if self.start_url_info[start_url].has_key('img_rgexp') and self.start_url_info[start_url].has_key('img_rptext'):
                            item[1] = item[1].replace(self.start_url_info[start_url]['img_rgexp'], self.start_url_info[start_url]['img_rptext'])
                        item[1] = utils.get_url_by_domain(item[1], self.start_url_info[start_url]['domain_name'])
                        new_text_list.append(item)
                    else:
                        log.msg(('filtered text_list ' + str(para_count) + ' ' + item[0] + ' ' + item[1]).encode('utf8'), level = log.DEBUG)
                        para_count += 1
                    pre_content = item[1]
                except:
                    exstr = traceback.format_exc()
                    log.msg('failed to encode ' + exstr, level = log.WARNING)
            para_count = 0
            for item in new_text_list:
                log.msg(('new_text_list ' + str(para_count) + ' ' + item[0] + ' ' + item[1]).encode('utf8'), level = log.DEBUG)
                para_count += 1
            prod = self.get_prod(start_url, attr_dict, new_text_list)
            if prod:
                ret_items.append(prod)
        return ret_items

    def get_pub_time(self, start_url, attr_dict):
        if self.start_url_info[start_url].has_key('time_format') and attr_dict.has_key('date'):
            date_str = attr_dict['date']
            time_format = self.start_url_info[start_url]['time_format']
            #gen_time = int(datetime.datetime.strptime(date_str, time_format).strftime("%s"))
            gen_time = self.general_gen_time(date_str, time_format)
            if not gen_time:
                return False
            now_time = int(time.time())
            if gen_time > now_time:
                log.msg('gen_time is too new than now', level = log.WARNING)
                return False
            attr_dict['pub_time_int'] = gen_time
            log.msg(date_str + ' -> ' + str(gen_time), level = log.DEBUG)
        return True

    def is_too_old(self, attr_dict, start_url, type_str, seconds):
        if self.start_url_info[start_url].has_key('time_format') and ((self.start_url_info[start_url].has_key('type') and self.start_url_info[start_url]['type'] == type_str) or not type_str) and not attr_dict.has_key('date'):
            log.msg('skip because no date', level = log.DEBUG)
            return True

        if self.start_url_info[start_url].has_key('time_format') and ((self.start_url_info[start_url].has_key('type') and self.start_url_info[start_url]['type'] == type_str) or not type_str) and attr_dict.has_key('date'):
            if not attr_dict.has_key('pub_time_int'):
                return True
            now_time = int(time.time())
            gen_time = attr_dict['pub_time_int']
            date_str = attr_dict['date']
            if now_time - gen_time > seconds or now_time - gen_time <= 0:
                log.msg('skip too old record gen_time ' + str(gen_time) + ' date ' + date_str, level = log.DEBUG)
                return True
            log.msg('gen_time ' + str(gen_time) + ' date ' + date_str, level = log.DEBUG)
        return False

    def auto_gen_part_html(self, start_url_info, part_html_content, response):
        try:
            main_xpath = start_url_info['main_xpath']
            tree = self.build_html_tree(part_html_content, get_last_tag(main_xpath), is_xml = False)
            candidates = tree.get_attr_candidates(tree.node)
            #part_html_content = utils.html_to_text(part_html_content.decode('utf8')).encode('utf8')
            if len(candidates['time_format']) > 0:
                time_format = candidates['time_format'][0]
            else:
                time_format = None
            for key in candidates:
                candidates_list = []
                for candidate in candidates[key]:
                    if part_html_content.find(candidate) == -1:
                        log.msg("skip key " + key + " : " + candidate, level = log.DEBUG)
                        continue
                    log.msg('before handle : ' + key + " : " + candidate, level = log.DEBUG)
                    candidates_list.append(candidate)
                candidates[key] = utils.get_uniq_list(candidates_list)

            for key in candidates:
                if key != '@desc':
                    candidates[key] = utils.get_uniq_list_from_base(candidates[key], candidates['@desc'])
            for key in ['@img']:
                candidates_list = []
                for candidate in candidates[key]:
                    if utils.has_suffix(candidate, 'jpg') or utils.has_suffix(candidate, 'png') or utils.has_suffix(candidate, 'gif') or utils.has_prefix(candidate, 'http'):
                        candidates_list.append(candidate)
                    else:
                        log.msg("skip img url because of suffix " + candidate, level = log.DEBUG)
                candidates[key] = candidates_list
            for key in ['@title', '@desc']:
                candidates_list = []
                for candidate in candidates[key]:
                    if utils.has_prefix(candidate, '分享到') or utils.has_prefix(candidate, '当前等级'):
                        log.msg("skip candidate because of prefix " + candidate, level = log.DEBUG)
                    else:
                        candidates_list.append(candidate)
                candidates[key] = candidates_list

            candidates['@title'] = sorted(candidates['@title'], cmp=compare_text_len2, reverse=True)
            candidates['@desc'] = sorted(candidates['@desc'], cmp=compare_text_len2, reverse=True)
            for key in candidates:
                for candidate in candidates[key]:
                    log.msg(key + " : " + candidate, level = log.DEBUG)
            choose = {}
            #max_url = utils.get_longest_string(candidates['@url'])
            #if max_url:
            #    choose['@url'] = max_url
            
            max_size = 0
            for candidate in candidates['@img']:
                img_url = self.get_content_page_url(response, candidate, start_url_info)
                if not img_url:
                    log.msg('failed to get img url from ' + candidate, level = log.WARNING)
                    continue
                img_size = utils.get_size_of_img_url(img_url)
                if not img_size:
                    log.msg('failed to get img size from ' + img_url, level = log.WARNING)
                    continue

                size = img_size[0] * img_size[1]
                log.msg('x = ' + str(img_size[0]) + ' y = ' + str(img_size[1]) + ' img_url ' + img_url, level = log.DEBUG)
                if max_size < size:
                    max_size = size
                    choose['@img'] = candidate

            for key in ['@date', '@title', '@desc']:
                if len(candidates[key]) > 0:
                    choose[key] = candidates[key][0]
            # has title has desc
            if len(candidates['@title']) == 0 and len(candidates['@desc']) == 0:
                log.msg('no title and desc', level = log.WARNING)
                return None
            
            if len(candidates['@img']) == 0:
                log.msg('no img', level = log.WARNING)

            if len(candidates['@title']) == 0 and len(candidates['@desc']) == 1:
                choose['@title'] = choose['@desc']
                del choose['@desc']
            elif len(candidates['@title']) == 0 and len(candidates['@desc']) >= 2:
                choose['@title'] = candidates['@desc'][1]
                choose['@desc'] = candidates['@desc'][0]

            for candidate in candidates['@url']:
                url = self.get_content_page_url(response, candidate, start_url_info)
                if not url:
                    log.msg('invalid url ' + candidate, level = log.DEBUG)
                    continue
                title, content = utils.ExtractLib.get_content(url)
                if title:
                    log.msg('url ' + candidate + ' title ' + title.encode('utf8'), level = log.DEBUG)
                    log.msg('compare [' + title.encode('utf8') + '] [' + choose['@title'] + ']', level = log.DEBUG)
                    if utils.ExtractLib.is_title(title, choose['@title'].decode('utf8')):
                        choose['@url'] = candidate

            for key in choose:
                log.msg('key ' + key + ' : ' + choose[key], level = log.DEBUG)
                part_html_content = part_html_content.replace(choose[key], key, 1)
            if time_format > 0:
                log.msg('key time_format : ' + time_format, level = log.DEBUG)
            return part_html_content
        except:
            exstr = traceback.format_exc()
            log.msg('failed to gen_part_html [' + exstr, level = log.WARNING)
            return None

    def parse(self, response):
        #print 'start_url ' + response.url.encode('utf8')
        #start_url = response.url
        #self.is_content_page(response)
        #hxs = HtmlXPathSelector(response)
        #if start_url_info.has_key('browser') and start_url_info['browser']:
        #    return self.parse_by_browser(response)
        #print ('body [' + response.body + ']')
        #print ('select [' + hxs.extract().encode('utf8') + ']')
        #if response.url.find('&_escaped_fragment_='):
        #    response.url = response.url.replace('&_escaped_fragment_=','#!')
            #response = response.replace(url=new_url)
        if self.start_url_info.has_key(response.url):
            start_url = response.url
            #site_name = self.url_to_name[start_url]
            self.gen_start_url_info(start_url)
            start_url_info = self.start_url_info[start_url]
            page = 1
            depth = 0
            #self.get_main_xpath(response)
            site_name = self.start_url_info[start_url]['site_name']
            first_page = True
        else:
            start_url = response.meta['start_url']
            start_url_info = self.start_url_info[start_url]
            if response.meta.has_key('page'):
                page = response.meta['page']
            else:
                page = 0
            depth = response.meta['depth']
            site_name = self.start_url_info[start_url]['site_name']
            first_page = False

        if response.url.find('weibo') != -1:
            response._body = response.body = response._body.replace('\\','')
            response._body = response.body = response._body.replace('>n','>')
        if first_page:
            utils.write_file(site_name + ".html", response._body)

        if start_url_info.has_key('browser') and start_url_info['browser']:
            if not self.driver:
                self.init_firefox()
            #time.sleep(5)
            if not utils.get_url_by_browser(self.driver, response.url):
                return
            if start_url_info.has_key('scroll_down_times'):
                scroll_times = start_url_info['scroll_down_times']
                utils.scroll_down(self.driver, scroll_times, 5)
                self.driver.save_screenshot('page_' + str(page) + '_' + site_name + '.png')
            #if start_url_info.has_key('scroll_down_times'):
            #    scroll_times = start_url_info['scroll_down_times']
            #    utils.scroll_down(self.driver, scroll_times, 5)
            #xpath='//body/div[@id="container"]/div[@class="page_nm"]/div[@class="mod mod_sp"]/div[@class="mod_sp_inner"]/div[@class="bd"]/ul[@id="red_pro_list"]/li'
            main_xpath = start_url_info['main_xpath']
            li_obj_array = self.driver.find_elements_by_xpath(main_xpath)
            print 'li_obj_array ' + str(len(li_obj_array))
            html_source = self.driver.page_source
            #response._body = html_source
            response = response.replace(body = html_source)
            utils.write_file(site_name + ".firefox.html", response._body)
            self.driver.save_screenshot('page_' + str(page) + '_' + site_name + '.png')
        response._body = response._body.replace('<link>', '<xml_link>').replace('</link>', '</xml_link>')
        log.msg('url ' + response.url + ' is_xml ' + str(utils.is_xml(response)), level = log.DEBUG)
        main_xpath = start_url_info['main_xpath']
        if start_url_info.has_key('selector_from_text'):
            selector_from_text = start_url_info['selector_from_text']
            if selector_from_text == 'xml':
                hxs = XmlXPathSelector(text=response.body)
            else:
                hxs = HtmlXPathSelector(text=response.body)
        else:
            hxs = utils.get_xpath_selector(response)
        if start_url_info.has_key('browser') and start_url_info['browser']:
            utils.write_file(site_name + ".firefox.extract.html", hxs.extract().encode('utf8'))
        h_li = hxs.select(main_xpath)
        log.msg('main_xpath array len ' + str(len(h_li)) + ' start_url ' + start_url + ' ' + response.url.encode('utf8'), level=log.DEBUG)
        if self.gen_part_html:
            if len(h_li) > 0:
                if start_url_info.has_key('xpath_file'):
                    file_name = start_url_info['xpath_file']
                else:
                    file_name = 'html/' + site_name + '.part.html'
                file_name_bak = file_name + '.bak'
                #part_html_content = self.auto_gen_part_html(start_url_info, h_li[0].extract().encode('utf8'))
                origin_part_html_content = h_li[0].extract().encode('utf8')
                part_html_content = utils.html_to_text(origin_part_html_content.decode('utf8')).encode('utf8')
                if not os.path.exists(file_name):
                    part_html_content = self.auto_gen_part_html(start_url_info, part_html_content, response)
                    if not part_html_content:
                        part_html_content = origin_part_html_content
                    utils.write_file(file_name, part_html_content)
                if not os.path.exists(file_name_bak):
                    utils.write_file(file_name_bak, origin_part_html_content)
            return
        if len(h_li) == 0 and self.start_url_info[start_url]['type'] == u'新闻':
            #is_content, text_list = is_content_webpage(response.body)
            #if is_content:
            #    log.msg('h_array is 0 and is content page url ' + response.url.encode('utf8'), level = log.WARNING)
            #    return 
            if self.start_url_info[start_url].has_key('max_depth'):
                if depth > self.start_url_info[start_url]['max_depth']:
                    return

            urls = self.get_urls(response, start_url)
            list = []
            count = 0
            for url in urls:
                try:
                    url = utils.get_url_by_domain(url, self.start_url_info[start_url]['domain_name'])
                    if self.filtered_urls(url, start_url):
                        log.msg('skip filter urls ' + url, level = log.DEBUG)
                        continue
                    log.msg('sending url ' + url, level = log.DEBUG)
                    list.append(Request(url = url, callback=self.parse, meta={'start_url' : start_url, 'depth' : depth + 1}))
                    count+=1
                    if count >= self.max_item:
                        return list
                except:
                    exstr = traceback.format_exc()
                    log.msg('failed to parse url ' + url + ' error ' + exstr, level = log.WARNING)
            return list
        if not self.start_url_info[start_url].has_key('xpath_list') and not self.get_main_attr_xpath(start_url, hxs, response):
            log.msg('failed to get start_url_info for url ' + response.url.encode('utf8'), level = log.ERROR)
            return
        xpath_list = self.start_url_info[start_url]['xpath_list']
        ret_requests = []
        if self.start_url_info[start_url].has_key('auto_parse') and self.start_url_info[start_url]['auto_parse']:
            return self.auto_parse(response, h_li)
        for h in h_li:
            if not self.start_url_info[start_url].has_key('xpath_file') or self.start_url_info[start_url].has_key('use_xpath'):
                attr_dict = utils.get_attr(xpath_list, h)
            else:
                attr_dict = self.get_tree_attr(xpath_list, h, get_last_tag(main_xpath), utils.is_xml(response))
            if not attr_dict:
                continue
            if not self.get_pub_time(start_url, attr_dict):
                continue
            if self.is_too_old(attr_dict, start_url, u'新闻', 3600 * 24 * 2):
                continue
            if self.is_too_old(attr_dict, start_url, u'商品', 3600 * 24 * 3):
                continue
            if self.start_url_info[start_url].has_key('reserve_days') and self.is_too_old(attr_dict, start_url, None, 3600 * 24 * self.start_url_info[start_url]['reserve_days']):
                continue
            if self.is_not_access(attr_dict, start_url):
                continue
            if self.start_url_info[start_url].has_key('crawl_text_content') and self.start_url_info[start_url]['crawl_text_content'] == 'crawl_taobao_feature':
                if not attr_dict.has_key('title'):
                    continue
            if attr_dict.has_key('url'):
                attr_dict['url'] = self.get_content_page_url(response, attr_dict['url'], start_url_info)
                if self.filtered_urls(attr_dict['url'], start_url):
                    continue 
            if attr_dict.has_key('img'):
                attr_dict['img'] = utils.get_url_by_domain(attr_dict['img'].strip(), self.start_url_info[start_url]['domain_name'])
            if attr_dict.has_key('title') and utils.need_filter(attr_dict['title'], utils.filter_jieqi_list):
                log.msg('skip because title about jieqi url ' + attr_dict['url'], level = log.WARNING)
                continue
            if attr_dict.has_key('desc') and utils.need_filter(attr_dict['desc'], utils.filter_invalid_desc):
                log.msg('skip because invalid desc [' + attr_dict['desc'].encode('utf8') + ']', level = log.WARNING)
                continue
            # jump the unneccessary page to content page
            if (self.start_url_info[start_url].has_key('jump_count') and self.start_url_info[start_url].has_key('jump_xpath')):
                self.jump_url(start_url, attr_dict)
            # crawl content page
            if (self.start_url_info[start_url].has_key('no_content') and self.start_url_info[start_url]['no_content'] == False or self.start_url_info[start_url]['type'] != u'商品'):
                if (self.start_url_info[start_url]['display_name'] == u'试客联盟'):
                    equal = attr_dict['url'].find('%20')
                    attr_dict['url'] = attr_dict['url'][:equal]
                ret_requests.append(Request(url = attr_dict['url'].strip(), callback=self.parse_content_page, meta={'start_url' : start_url, 'attr_dict' : attr_dict, 'page' : 1, 'depth' : depth + 1, 'first_page_url' : attr_dict['url']}))
            else:
                prod = self.get_prod(start_url, attr_dict, None)
                if prod:
                    ret_requests.append(prod)

            self.start_url_info[start_url]['crawl_num'] += 1
            log.msg('start_url ' + start_url + ' crawl_num ' + str(self.start_url_info[start_url]['crawl_num']), level = log.DEBUG)
                
            if self.max_item > 0 and self.start_url_info[start_url]['crawl_num'] >= self.max_item:
                log.msg('reach max_item limit item num is ' + str(self.start_url_info[start_url]['crawl_num']), level = log.DEBUG)
                return ret_requests
        
        #if not self.start_url_info[start_url].has_key('get_link'):
        next_url = self.get_next_page_url(response, page + 1, start_url_info)
        if start_url.find('amazon') != -1:
            next_url = 'http://www.amazon.com/' + hxs.select('//a[@id="pagnNextLink"]/@href').extract()[0]
        if self.max_pages > 0 and page >= self.max_pages:
            log.msg('reach page limit page num is ' + str(page), level = log.DEBUG)
            return ret_requests
        if next_url:
            log.msg('next_url ' + next_url.encode('utf8') + ' start url ' + start_url + ' ' + response.url.encode('utf8'))
            ret_requests.append(Request(url = next_url, callback=self.parse, meta={'start_url' : start_url, 'page': page + 1, 'depth' : depth}))
        else:
            log.msg('next_url None for start url ' + start_url)
        #else:
            #urls = self.get_urls(response)
            #for url in urls:
            #   yield Request(url = url, callback=self.parse, meta={'start_url' : start_url})
        return ret_requests

def auto_parse(self, response, h_li):
    pass
    #utils.process(self,html_list,attr_dict,pre_url,neg_word_list,neg_tag_dict):
