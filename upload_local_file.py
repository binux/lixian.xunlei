#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# binux<17175297.hk@gmail.com>

import os
import time
import logging
from sys import argv
from libs import lixian_api, tools
from pprint import pprint

#logging.getLogger().setLevel(logging.DEBUG)

if len(argv) != 4:
    print "usage: upload_local_file.py username passwd filepath"
    exit()

lx = lixian_api.LiXianAPI()
print "login...",
if lx.login(argv[1], argv[2]):
    print "ok"
else:
    print "error"
    exit()
lx.task_check("http://www.baidu.com/")
gcid = tools.dcid_hash_file(argv[3])
print "cid: %s" % gcid
size = os.path.getsize(argv[3])
fid = tools.gen_fid(gcid, size, gcid)
#print "fid: %s" % fid
#print "checking file exist...",
#ret = lx.webfilemail_url_analysis("http://sendfile.vip.xunlei.com/filename?tid=0&fid=%s" % fid)
#if ret['result'] != 0:
    #print "no"
#else:
    #print "yes!"
print "adding task to lixian..."
lx.add_task_with_dict("http://www.baidu.com/", {
    "cid": gcid,
    "gcid": "",
    "size": size,
    "title": os.path.split(argv[3]),
    })
print "wating for 3 seconds..."
time.sleep(3)
print "fetch tasks..."
for task in lx.get_task_list(pagenum=100):
    if task['cid'] == gcid:
        if "lixian_url" in task and task['lixian_url']:
            print task['lixian_url']
        else:
            print "this file may not exist on lixian.xunlei.com"
        break
