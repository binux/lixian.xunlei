# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import time
from sys import argv, stderr
from libs.lixian_api import LiXianAPI

CID = "9AD622F6EE572E367A37A166D7BD5AA8279A68D4"
URL = "magnet:?xt=urn:btih:9ad622f6ee572e367a37a166d7bd5aa8279a68d4"

if len(argv) != 2:
    print "usage: vip_check.py user_list"

fp = open(argv[1], "r")
for line in fp:
  try:
    line = line.strip()
    if not line:
        continue
    username, password = line.split()
    xunlei = LiXianAPI()
    if not xunlei.login(username, password):
        print >> stderr, username, "login error"
        continue
    else:
        info = xunlei.get_vip_info()
        print >> stderr, username, "expiredate:", info.get("expiredate", "unknow"), "level:", info.get("level", "0")
    tasks = xunlei.get_task_list(10, 2)
    tid = 0
    lixian_url = ""
    for task in tasks:
        if task['cid'] == CID:
            for file in xunlei.get_bt_list(task['task_id'], task['cid']):
                tid = file['task_id']
                lixian_url = file['lixian_url']
    if not tid:
        xunlei.add(URL)
        tasks = xunlei.get_task_list(10, 2)
        #time.sleep(1)
        for task in tasks:
            if task['cid'] == CID:
                for file in xunlei.get_bt_list(task['task_id'], task['cid']):
                    tid = file['task_id']
                    lixian_url = file['lixian_url']
    if not tid:
        print >> stderr, username, "add task error"
        continue
    r = xunlei.session.get(lixian_url, cookies={"gdriveid": xunlei.gdriveid})
    print "%s|%s|%s|%s" % (xunlei.uid, xunlei.gdriveid, tid, lixian_url)
  except Exception, e:
    print e
    continue
