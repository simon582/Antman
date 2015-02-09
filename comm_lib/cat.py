

def async_get_cats_info(type):
    op = OpenTaobao('12651461','80a15051c411f9ca52d664ebde46a9da')
    params = {
        'method':'taobao.topats.itemcats.get',
        'output_format':'json',
        'cids': '0',
        'type': type,
    }
    dict_str = op.get_result(params)
    ret_dict = json.loads(dict_str)
    return ret_dict

def async_get_result(taskid):
    op = OpenTaobao('12651461','80a15051c411f9ca52d664ebde46a9da')
    params = {
        'method':'taobao.topats.result.get',
        'task_id': taskid,
    }
    dict_str = op.get_result(params)
    ret_dict = json.loads(dict_str)
    return ret_dict

def download_result(taskid, path, download_file_name = 'download_cat.txt'):
    download_file = path + '/' + download_file_name
    while True:
        ret_dict = async_get_result(taskid)
        if ret_dict.has_key('topats_result_get_response') and ret_dict['topats_result_get_response']['task']['status'] == 'done':
            url = ret_dict['topats_result_get_response']['task']['download_url']
            lock_file = path + '/download_lock'
            if os.path.exists(lock_file):
                break
            open(lock_file, 'w').close()

            form_data = urllib.urlencode({})
            buffer = urllib2.urlopen(url, form_data).read()
            file = open(download_file, 'w')
            file.write(buffer)
            file.close()

            os.remove(lock_file)

def get_cats_info(type):
    ret_dict = async_get_cats_info(type)
    print 'ret_dict ' + str(ret_dict)
    debug=True
    if ret_dict.has_key('topats_itemcats_get_response'):
        taskid = ret_dict['topats_itemcats_get_response']['task']['task_id']
        async_ret_dict = async_get_result(taskid)
        print 'async_ret_dict ' + str(async_ret_dict)
    elif debug:
        taskid = 203302719
        async_ret_dict = async_get_result(taskid)
        print 'async_ret_dict ' + str(async_ret_dict)
    elif ret_dict.has_key('error_response'):
        print ret_dict['error_response']['sub_msg'].encode('utf8')

def build_root_leave_dict(origin_cat_dict, root_leave_dict, level = 0):
    if not origin_cat_dict.has_key('cid'):
        return
    if not origin_cat_dict['cid']:
        return
    cid = origin_cat_dict['cid']
    if not root_leave_dict.has_key(cid):
        root_leave_dict[cid] = {}

    if not origin_cat_dict.has_key('childCategoryList'):
        return
    if not origin_cat_dict['childCategoryList']:
        return
    print 'origin_cat_dict.__class__.__name__ ' + origin_cat_dict.__class__.__name__ + " " + str(root_leave_dict)
    try:
        print 'level ' + str(level) + ' ' + str(len(origin_cat_dict['childCategoryList']))
        for item in origin_cat_dict['childCategoryList']:
            sub_cid = item['cid']
            root_leave_dict[cid][sub_cid] = {}
            build_root_leave_dict(item, root_leave_dict[cid], level + 1)
    except:
        return 

def build_cat_tree(dir):
    files = os.listdir(dir)
    print 'files : ' + str(files)
    root_leave_dict = {}
    i = 0
    for file in files:
        #if file != '99':
        #    continue
        path=dir + file
        f = open(path, 'r')
        print 'open ' + path
        buffer = f.read()
        ret_dict = json.loads(buffer)
        #print 'ret_dict ' + str(ret_dict)
        build_root_leave_dict(ret_dict, root_leave_dict)
        i = i + 1
        #if i > 2:
        #    break

    print 'root_leave_dict ' + str(root_leave_dict)
    return root_leave_dict

def build_cat_map(root_leave_dict, root_cid, map_dict):

    for cid in root_leave_dict:
        if len(root_leave_dict[cid]) == 0:
            map_dict[cid] = root_cid
        else:
            build_cat_map(root_leave_dict[cid], root_cid, map_dict)

def build_cat_total_map(root_leave_dict):
    map_dict = {}
    for cid in root_leave_dict:
        build_cat_map(root_leave_dict[cid], cid, map_dict)

    return map_dict

if __name__ == '__main__':
    get_cats_info('1')
