#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# binux<17175297.hk@gmail.com>

import os
import time
import urllib
import logging
from sys import argv
from libs import lixian_api, tools
from pprint import pprint

#logging.getLogger().setLevel(logging.DEBUG)
tid_dic = {}
if os.path.exists("tid.dict"):
    for line in open("tid.dict", "r"):
        line = line.strip()
        size, tid = line.split(" ", 1)
        tid_dic[int(size)] = tid

if len(argv) != 4:
    print "usage: upload_local_file.py username passwd filepath"
    exit()

cid = tools.cid_hash_file(argv[3])
gcid = tools.gcid_hash_file(argv[3])
size = os.path.getsize(argv[3])
fid = tools.gen_fid(cid, size, gcid)
fake_url = "http://sendfile.vip.xunlei.com/filename?fid=%s&mid=666&threshold=150&tid=%s" % (fid, tid_dic.get(size, 0))
print "cid: %s" % cid
print "gcid: %s" % gcid
print "size: %s" % size
print "fid: %s" % fid
print "fake_url: %s" % fake_url

lx = lixian_api.LiXianAPI()
print "login...",
if lx.login(argv[1], argv[2]):
    print "ok"
else:
    print "error"
    exit()
print "checking file exist...",
ret = lx.webfilemail_url_analysis(fake_url)
if ret['result'] != 0:
    print "no"
    exit()
else:
    print "yes!"
print "adding task to lixian..."
lx.task_check(fake_url)
lx.add_task_with_dict(fake_url, {
    "cid": gcid,
    "gcid": gcid,
    "size": size,
    "title": os.path.split(argv[3]),
    })
print "wating for 3 seconds..."
time.sleep(3)
print "fetch tasks..."
for task in lx.get_task_list(pagenum=10):
    if task['cid'] == cid:
        if "lixian_url" in task and task['lixian_url']:
            print task['lixian_url']
        else:
            print "this file may not exist on lixian.xunlei.com"
        break
