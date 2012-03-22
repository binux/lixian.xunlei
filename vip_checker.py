# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from sys import argv
from libs.lixian_api import LiXianAPI

if len(argv) != 3:
    print "usage: vip_check.py user_list test_task"

fp = open(argv[1], "r")
for line in fp:
    line = line.strip()
    username, password = line.split()
    xunlei = LiXianAPI()
    if not xunlei.login(username, password):
        print username, "login error"
    #tasks = xunlei.get_task_list(10, 2)
    tasks = None
    if not tasks:
        xunlei.add(argv[2])
        tasks = xunlei.get_task_list(10, 0)
    if not tasks:
        print username, "add task error"
    tid = 0
    for task in tasks:
        if task['task_type'] == 'normal':
            if not tid and task['lixian_url']:
                #tid = task['task_id']
                pass
        elif task['task_type'] in ['bt', 'magenet']:
            for file in xunlei.get_bt_list(task['task_id'], task['cid']):
                if not tid and file['lixian_url']:
                    tid = file['task_id']
    print "%s:%s:%s" % (xunlei.uid, xunlei.gdriveid, tid)
