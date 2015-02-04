#-*- coding:utf-8 -*-
import sys
import urllib, urllib2, cookielib, hashlib
reload(sys)
sys.setdefaultencoding('utf-8')
from scrapy import Selector
import json

conf_dict = {}
with open('dict.conf','r') as conf_file:
    lines = conf_file.readlines()
    for line in lines:
        res = line.split(':')
        conf_dict[res[0]] = res[1].strip()

def get_html_by_data(url, use_cookie=False):
    data = {}
    post_data = urllib.urlencode(data)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    req = urllib2.Request(url)
    if use_cookie:
        cookie_file = open('cookie')
        cookie = cookie_file.read()
        req.add_header("Cookie", cookie)
    req.add_header("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36")
    f = opener.open(req)
    html = f.read()
    html_file = open('test.html','w')
    print >> html_file, html
    f.close()
    return html

def get_imgs(prod, hxs):
    prod['img_urls'] = [] 
    bh = get_content(hxs, '//input[@id="hidbh"]/@value')
    clggbh = get_content(hxs, '//input[@id="hidclggbh"]/@value')
    request_url = 'http://www.jdcsww.com/getimgs?bh=' + bh + '8&clggbh=' + clggbh
    ret = urllib2.urlopen(request_url)
    json_dict = json.loads(ret.read())
    print json_dict
    for key,value in json_dict.items():
        if key.find('IMG') != -1 and value != None and value != u"":
            prod['img_urls'].append('http://www.jdcsww.com/photo/' + json_dict[u'PC'] + '/' + value + '.jpg')
    handle_img(prod)

def handle_img(prod):
    urls = prod['img_urls']
    file_path = './img/'
    prod['img'] = []
    for url in urls:
        file_name = hashlib.md5(url.encode('utf8')).hexdigest().upper() + '.jpg'
        data = urllib2.urlopen(url).read()
        prod['img'].append(file_name)
        f = file(file_path + file_name, 'wb')
        f.write(data)
        f.close()

def get_js(key):
    if key in conf_dict:
        return conf_dict[key]
    return ''

def get_content(hxs, xpath):
    res = hxs.xpath(xpath)
    if len(res) == 0:
        return ''
    return res[0].extract().strip()

def crawl_content(prod):
    hxs = Selector(text=get_html_by_data(prod['url']))
    
    # 生产企业信息
    prod['clmc'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[2]/td[1]/span/text()')
    prod['clmc'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[2]/td[1]/span/text()')
    prod['cllx'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[2]/td[2]/span/script/text()')
    prod['cllx'] = get_js(prod['cllx'].split('\'')[1].split('\'')[0])
    prod['zzg'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[3]/td[1]/script/text()')
    prod['zzg'] = get_js(prod['zzg'].split('\'')[1].split('\'')[0])
    prod['ggpc'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[4]/td[1]/span/text()')
    prod['fbrq'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[4]/td[2]/text()')
    prod['cph'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[5]/td[1]/text()')
    prod['mlxh'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[5]/td[2]/text()')
    prod['zwpp'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[6]/td[1]/text()')
    prod['ywpp'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[6]/td[2]/text()')
    prod['ggxh'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[7]/td[1]/text()')
    prod['cpid'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[7]/td[2]/text()')
    prod['qymc'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[8]/td[1]/text()')
    prod['scdz'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[9]/td[1]/text()')
    prod['zcdz'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[10]/td[1]/text()')
    prod['txdz'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[11]/td[1]/text()')
    prod['dh'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[12]/td[1]/text()')
    prod['frdb'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[12]/td[2]/text()')
    prod['yb'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[13]/td[1]/text()')
    prod['cz'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[13]/td[2]/text()')
    prod['dzyx'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[14]/td[1]/text()')
    prod['lxr'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[14]/td[2]/text()')
    
    # 免检说明
    prod['mjts'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[16]/td[1]/span/text()')
    prod['mjyxqz'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[16]/td[2]/text()')
    
    # 公告状态
    prod['ggzt'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[18]/td[1]/span/text()')
    prod['ggsxrq'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[18]/td[2]/span/text()')
    prod['tzscrq'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[19]/td[1]/span/text()')
    prod['tzxsrq'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[19]/td[2]/span/text()')
    prod['cxggpc'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[20]/td[1]/span/text()')
    prod['cxfbrq'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[20]/td[2]/span/text()')
    prod['ggztms'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[21]/td[1]/text()')
    #tres = hxs.xpath('//td[@id="tdbgkz"]/a/text()')
    prod['bgkzjl'] = ''
    #for res in tres:
    #    prod['bgkzjl'] += res.extract() + ' '  
    
    # 主要技术参数
    prod['clzzl'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[24]/td[1]/span/text()')
    prod['clzxxs'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[24]/td[2]/span/text()')
    prod['edzzl'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[25]/td[1]/span/text()')
    prod['clzzs'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[25]/td[2]/text()')
    prod['clzbzl'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[26]/td[1]/span/text()')
    prod['zgcs'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[26]/td[2]/text()')
    prod['clzh'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[27]/td[1]/text()')
    prod['edzk'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[27]/td[2]/text()')
    prod['clzj'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[28]/td[1]/span/text()')
    prod['qpyxzk'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[28]/td[2]/span/text()')
    prod['clqlj'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[29]/td[1]/span/text()')
    prod['hpyxzk'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[29]/td[2]/text()')
    prod['clhlj'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[30]/td[1]/span/text()')
    prod['clcdxs'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[30]/td[2]/text()')
    prod['gbthps'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[31]/td[1]/text()')
    prod['cllts'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[31]/td[2]/text()')
    prod['bgcazzdzzl'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[32]/td[1]/text()')
    prod['ztgczzl'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[32]/td[2]/text()')
    prod['jjj'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[33]/td[1]/text()')
    prod['zzllyxs'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[33]/td[2]/text()')
    prod['clqx'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[34]/td[1]/span/text()')
    prod['clltggxh'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[35]/td[1]/span/text()')
    prod['wxcc'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[36]/td[1]/span/text()')
    prod['hxlbc'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[37]/td[1]/span/text()')
    prod['clsbdm'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[38]/td[1]/span/text()')
    
    # 车辆燃料参数
    prod['clrlzl'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[40]/td[1]/script/text()')
    prod['clrlzl'] = get_js(prod['clrlzl'].split('\'')[1].split('\'')[0])
    prod['clhy'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[41]/td[1]/span/text()')
    prod['pfyjbz'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[42]/td[1]/span/span/text()')

    # 车辆制动参数
    prod['zdczfs'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[45]/td[1]/text()')
    prod['clfbsxt'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[45]/td[2]/text()')

    # 车辆底盘参数
    prod['xzdp'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[47]/td[1]/text()')
    
    # 发动机参数
    prod['fdjxh'] = get_content(hxs, '//input[@id="hidfdjxh"]/@value').replace(',','|')
    prod['fdjqy'] = get_content(hxs, '//input[@id="hidzzcmc"]/@value').replace(',','|')
    prod['fdjsb'] = get_content(hxs, '//input[@id="hidfdjsb"]/@value').replace(',','|')
    prod['fdjpl'] = get_content(hxs, '//input[@id="hidpl"]/@value').replace(',','|')
    prod['fdjgl'] = get_content(hxs, '//input[@id="hidgl"]/@value').replace(',','|')
    # 其他
    prod['qt'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[52]/td[1]/p/text()')
    
    # 图片
    get_imgs(prod, hxs)

    # 公告变更原因
    prod['ggbgyy'] = get_content(hxs, '//div[@class="tableBox"]/table/tr[60]/th/text()')
    prod['ggbgyy'] = prod['ggbgyy'].split('(')[1].split(')')[0]
    print prod
    write_csv(prod)

def add(key, prod):
    if prod.has_key(key):
        return prod[key].replace('\n','').replace('\r','').replace(',',' ').strip() + ','
    else:
        print 'Cannot find key: ' + key
        return ','

def write_csv(prod):
    file = open('csv/' + prod['code'] + '.csv','a')
    resline = ""
    resline += add('clmc', prod)
    resline += add('cllx', prod)
    resline += add('zzg', prod)
    resline += add('ggpc', prod)
    resline += add('fbrq', prod)
    resline += add('cph', prod)
    resline += add('mlxh', prod)
    resline += add('zwpp', prod)
    resline += add('ywpp', prod)
    resline += add('ggxh', prod)
    resline += add('cpid', prod)
    resline += add('qymc', prod)
    resline += add('scdz', prod)
    resline += add('zcdz', prod)
    resline += add('txdz', prod)
    resline += add('dh', prod)
    resline += add('frdb', prod)
    resline += add('yb', prod)
    resline += add('cz', prod)
    resline += add('dzyx', prod)
    resline += add('lxr', prod)
    resline += add('mjts', prod)
    resline += add('mjyxqz', prod)
    resline += add('ggzt', prod)
    resline += add('ggsxrq', prod)
    resline += add('tzscrq', prod)
    resline += add('tzxsrq', prod)
    resline += add('cxggpc', prod)
    resline += add('cxfbrq', prod)
    resline += add('ggztms', prod)
    resline += add('bgkzjl', prod)
    resline += add('clzzl', prod)
    resline += add('clzxxs', prod)
    resline += add('edzzl', prod)
    resline += add('clzzs', prod)
    resline += add('clzbzl', prod)
    resline += add('zgcs', prod)
    resline += add('clzh', prod)
    resline += add('edzk', prod)
    resline += add('clzj', prod)
    resline += add('qpyxzk', prod)
    resline += add('clqlj', prod)
    resline += add('hpyxzk', prod)
    resline += add('clhlj', prod)
    resline += add('clcdxs', prod)
    resline += add('gbthps', prod)
    resline += add('cllts', prod)
    resline += add('bgcazzdzzl', prod)
    resline += add('ztgczzl', prod)
    resline += add('jjj', prod)
    resline += add('zzllyxs', prod)
    resline += add('clqx', prod)
    resline += add('clltggxh', prod)
    resline += add('wxcc', prod)
    resline += add('hxlbc', prod)
    resline += add('clsbdm', prod)
    resline += add('clrlzl', prod)
    resline += add('clhy', prod)
    resline += add('pfyjbz', prod)
    resline += add('zdczfs', prod)
    resline += add('clfbsxt', prod)
    resline += add('xzdp', prod)
    resline += add('fdjxh', prod)
    resline += add('fdjqy', prod)
    resline += add('fdjsb', prod)
    resline += add('fdjpl', prod)
    resline += add('fdjgl', prod)
    resline += add('qt', prod)
    resline += add('ggbgyy', prod)
    first = True
    for url in prod['img']:
        if first:
            resline += url
            first = False
        else:
            resline += '|' + url
    print >> file, resline.encode('utf-8')    

def work(code, list_url):
    hxs = Selector(text=get_html_by_data(list_url))
    item_list = hxs.xpath('//table[@id="frmcontent"]/tbody/tr')
    for item in item_list:
        try:
            prod = {}
            prod['code'] = code
            prod['url'] = 'http://www.jdcsww.com' + item.xpath('.//td[2]/a/@href')[0].extract()
            crawl_content(prod)
        except Exception as e:
            print e
   
    next_url = '' 
    a_items = hxs.xpath('//div[@class="AspNetPager"]/a')
    for a_item in a_items:
        if a_item.xpath('.//text()')[0].extract() == '下一页':
            next_url = a_item.xpath('.//@href')
            if len(next_url) == 0:
                print code + ' finished.'
                return
            next_url = next_url[0].extract()
            break
    
    if next_url != '':
        work(code, next_url)
    else:
        print 'No information in ' + code
            

if __name__ == "__main__":
    total_part = 20
    part = int(sys.argv[1])
    with open('code.conf','r') as code_file:
        code_list = code_file.readlines()
    block_size = int(len(code_list) / total_part) + 1
    print 'block size: ' + str(block_size)
    start = block_size * part
    end = min(block_size * (part + 1), len(code_list))
    print 'range: ' + str(start) + ' ' + str(end)
    for i in range(start, end):
        code = code_list[i].strip()
        start_url = 'http://www.jdcsww.com/qcgglist?ggxh=&clmc=&ggpc=&zwpp=&cllx=&rylx=&qymc=&zs=&sbdm=' + code + '&fdjzzs=&fdjxh=&fdjgl=&hxlbc=&hdzzl=&wxccc=&hxlbk=&hdzl=&wcxxk=&hxlbg=&hdzbzl=&wcxxg=&page=1'
        print 'url: ' + start_url
        with open('csv/' + code + '.csv', 'a') as new_file:
            pass
        work(code, start_url)
