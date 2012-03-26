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

if len(argv) != 2:
    print "usage:", __file__, "filepath"
    exit()

cid = tools.cid_hash_file(argv[1])
gcid = tools.gcid_hash_file(argv[1])
size = os.path.getsize(argv[1])
fid = tools.gen_fid(cid, size, gcid)
fake_url = "http://sendfile.vip.xunlei.com/download?fid=%s&mid=666&threshold=150&tid=%s" % (fid, tid_dic.get(size, 0))
print "cid: %s" % cid
print "gcid: %s" % gcid
print "size: %s" % size
print "fid: %s" % fid
print "fake_url: %s" % fake_url
print "thunder_url: %s" % tools.encode_thunder(fake_url)

lx = lixian_api.LiXianAPI()
print "checking file exist...",
ret = lx.webfilemail_url_analysis(fake_url)
if ret['result'] != 0:
    print "no"
    exit()
else:
    print "yes!"
