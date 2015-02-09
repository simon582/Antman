import pymongo
from pymongo import Connection
from pymongo.errors import AutoReconnect
try:
    host_url = '%s:%i,%s:%i'%('localhost',27017,'localhost',27018)
    mongoConn = pymongo.MongoReplicaSetClient(host=host_url, replicaSet='zhs_replset', read_preference=pymongo.ReadPreference.PRIMARY_PREFERRED)
except AutoReconnect,e:
    print "init mongo connection failed.... "
    mongoConn = None
import sys

if __name__ == '__main__':
    write_dict = {}
    print sys.argv[1]
    fd = open(sys.argv[1],'r')
    for line in fd:
	line = line[:-1]
        #info = line.split('\t')
        info = line.split()
	if info[0] not in write_dict:
            write_dict[info[0]] = {}
            write_dict[info[0]]['id'] = info[0]
            write_dict[info[0]]['name'] = info[1]
            write_dict[info[0]]['parent'] = sys.argv[2]
        if info[2] not in write_dict:
            write_dict[info[2]] = {}
            write_dict[info[2]]['id'] = info[2]
            write_dict[info[2]]['name'] = info[3]
            write_dict[info[2]]['parent'] = info[0]
    _dbtable = mongoConn['baseinfo']['cats']
    for(key,value) in write_dict.items():
    	_dbtable.insert(dict(value))
    fd.close()
