# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
import thread
import random
import re
import db
from time import time
from db.util import *
from libs.lixian_api import LiXianAPI
from libs.util import determin_url_type
from libs.cache import mem_cache
from tornado.options import options

ui_re = re.compile(r"ui=\d+")
ti_re = re.compile(r"ti=\d+")
def fix_lixian_url(url):
    url = ui_re.sub("ui=%(uid)d", url)
    url = ti_re.sub("ti=%(tid)d", url)
    return url

class DBTaskManager(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._last_check_login = 0
        self._last_update_task = 0
        self._last_update_downloading_task = 0
        self._last_get_task_list = 0
        #fix for _last_get_task_list
        self.time = time

        self.session = db.Session()

        self._xunlei = LiXianAPI()
        self.last_task_id = 0
        self.islogin = self._xunlei.login(self.username, self.password)
        self._last_check_login = time()

    @property
    def xunlei(self):
        if self._last_check_login + options.check_interval < time():
            if not self._xunlei.check_login():
                self._xunlei.logout()
                self.islogin = self._xunlei.login(self.username, self.password)
            self._last_check_login = time()
        return self._xunlei

    @property
    def gdriveid(self):
        return self._xunlei.gdriveid

    @property
    def uid(self):
        return self._xunlei.uid

    @sqlalchemy_rollback
    def _update_tasks(self, tasks):
        nm_list = []
        bt_list = []
        for task in tasks:
            if task.task_type in ("bt", "magnet"):
                bt_list.append(task.id)
            else:
                nm_list.append(task.id)

        for res in self.xunlei.get_task_process(nm_list, bt_list):
            task = self.get_task(res['task_id'])
            task.status = res['status']
            task.process = res['process']
            if res['cid'] and res['lixian_url']:
                task.cid = res['cid']
                task.lixian_url = res['lixian_url']

            task = self.session.merge(task)
            if not self._update_file_list(task):
                task.status = "failed"
                self.session.add(task)
        self.session.commit()

    @sqlalchemy_rollback
    def _update_task_list(self, limit=10, st=0, ignore=False):
        tasks = self.xunlei.get_task_list(limit, st)
        for task in tasks[::-1]:
            if task['status'] == "finished":
                self.last_task_id = task['task_id']
            db_task_status = self.session.query(db.Task.status).filter(
                    db.Task.id == task['task_id']).first()
            if db_task_status and db_task_status[0] == "finished":
                continue

            db_task = db.Task()
            db_task.id = task['task_id']
            db_task.create_uid = self.uid
            db_task.cid = task['cid']
            db_task.url = task['url']
            db_task.lixian_url = task['lixian_url']
            db_task.taskname = task['taskname']
            db_task.task_type = task['task_type']
            db_task.status = task['status']
            db_task.process = task['process']
            db_task.size = task['size']
            db_task.format = task['format']

            db_task = self.session.merge(db_task)
            if not self._update_file_list(db_task):
                db_task.status = "failed"
                self.session.add(db_task)
            
        self.session.commit()

    @sqlalchemy_rollback
    def _update_file_list(self, task):
        if task.task_type == "normal":
            tmp_file = dict(
                    task_id = task.id,
                    cid = task.cid,
                    url = task.url,
                    lixian_url = task.lixian_url,
                    title = task.taskname,
                    status = task.status,
                    dirtitle = task.taskname,
                    process = task.process,
                    size = task.size,
                    format = task.format
                    )
            files = [tmp_file, ]
        elif task.task_type in ("bt", "magnet"):
            try:
                files = self.xunlei.get_bt_list(task.id, task.cid)
            except Exception, e:
                logging.error(repr(e))
                return False

        for file in files:
            if file['lixian_url']:
                self.last_task_id = file['task_id']
            db_file = db.File()
            db_file.id = file['task_id']
            db_file.task_id = task.id
            db_file.cid = file['cid']
            db_file.url = file['url']
            db_file._lixian_url = fix_lixian_url(file['lixian_url'])
            db_file.title = file['title']
            db_file.dirtitle = file['dirtitle']
            db_file.status = file['status']
            db_file.process = file['process']
            db_file.size = file['size']
            db_file.format = file['format']

            self.session.merge(db_file)
        return True

    @sqlalchemy_rollback
    def get_task(self, task_id):
        return self.session.query(db.Task).get(task_id)

    @sqlalchemy_rollback
    def get_task_by_cid(self, cid):
        return self.session.query(db.Task).filter(db.Task.cid == cid)

    @sqlalchemy_rollback
    def get_task_by_title(self, title):
        return self.session.query(db.Task).filter(db.Task.taskname == title)
    
    @sqlalchemy_rollback
    def get_task_list(self, start_task_id=0, limit=30, q="", t="", a="", order=db.Task.createtime, dis=db.desc):
        self._last_get_task_list = self.time()
        # base query
        query = self.session.query(db.Task)
        # query or tags
        if q:
            query = query.filter(db.or_(db.Task.taskname.like("%%%s%%" % q),
                db.Task.tags.like("%%%s%%" % q)))
        elif t:
            query = query.filter(db.Task.tags.like("%%|%s|%%" % t));
        # author query
        if a:
            query = query.filter(db.Task.creator == a)
        # next page offset
        if start_task_id:
            value = self.session.query(order).filter(db.Task.id == start_task_id).first()
            if not value:
                return []
            if dis == db.desc:
                query = query.filter(order < value[0])
            else:
                query = query.filter(order > value[0])
            query = query.filter(db.Task.id < start_task_id)
        # order or limit
        query = query.filter(db.Task.invalid == False)\
                     .order_by(dis(order), dis(db.Task.id)).limit(limit)
        return query.all()
    
    @sqlalchemy_rollback
    def get_file_list(self, task_id):
        task = self.get_task(task_id)
        if not task: return []

        #fix lixian url
        if not self.last_task_id:
            raise Exception, "add a task and refresh task list first!"
        for file in task.files:
            file.lixian_url = file._lixian_url % {"uid": self.uid, "tid": self.last_task_id}
        return task.files
    
    @sqlalchemy_rollback
    def get_tag_list(self):
        from collections import defaultdict
        tags_count = defaultdict(int)
        for tags, in self.session.query(db.Task.tags).filter(db.Task.invalid == False):
            for tag in tags:
                tags_count[tag] += 1
        return sorted(tags_count.iteritems(), key=lambda x: x[1], reverse=True)

    @sqlite_fix
    def add_task(self, url, title=None, tags=set(), creator="", anonymous=False, need_cid=True):
        def update_task(task, title=title, tags=tags, creator=creator, anonymous=anonymous):
            if not task:
                return task
            if task.invalid and not anonymous:
                task.taskname = title
                task.tags = tags
                task.creator = creator
                task.invalid = False
                self.session.add(task)
                self.session.commit()
                _ = task.id
            return task

        task = self.session.query(db.Task).filter(db.Task.url == url).first()
        if task:
            return (1, update_task(task))

        def _random():
            return random.randint(100, 999)

        # step 1: determin type
        url_type = determin_url_type(url)
        if url_type in ("bt", "magnet"):
            check = self.xunlei.bt_task_check
            add_task = self.xunlei.add_bt_task_with_dict
        elif url_type in ("normal", "ed2k", "thunder"):
            check = self.xunlei.task_check
            add_task = self.xunlei.add_task_with_dict
        else:
            return (-3, "space error")
            #result = self.xunlei.add_batch_task([url, ])

        # step 2: get info
        info = check(url)

        # step 3: check info
        # check info
        if not info: return (-1, "check task error")
        # check cid
        if need_cid and not info['cid']:
            return (-2, "can't find cid")
        if info['cid']:
            task = self.get_task_by_cid(info['cid'])
            if task.count() > 0:
                return (1, update_task(task[0]))
        # check title
        if title:
            info['title'] = title
        else:
            title = info['title']
        if not info['cid'] and \
                self.get_task_by_title(info['title']).count() > 0:
            info['title'] = "#%s %s" % (_random(), info['title'])
        # for bt
        if "valid_list" in info:
            info["valid_list"] = ["1", ]*len(info["valid_list"])

        # step 4: commit & fetch result
        result = add_task(url, info)
        if not result:
            return (0, "error")
        self._update_task_list(5)

        # step 5: checkout task&fix
        if info['cid']:
            task = self.get_task_by_cid(info['cid']).first()
        elif info['title']:
            task = self.get_task_by_title(info['title']).first()
        else:
            task = None

        if task:
            task.taskname = title
            task.tags = tags
            task.invalid = anonymous
            self.session.add(task)
            self.session.commit()
            _ = task.id
        return (1, task)

    @sqlite_fix
    def update(self):
        if self._last_update_task + options.finished_task_check_interval < time():
            self._last_update_task = time()
            self._update_task_list(options.task_list_limit)

        if self._last_update_downloading_task + \
                options.downloading_task_check_interval < self._last_get_task_list or \
           self._last_update_downloading_task + \
                options.finished_task_check_interval < time():
            self._last_update_downloading_task = time()
            need_update = self.session.query(db.Task).filter(db.Task.status != "finished").all()
            if need_update:
                self._update_tasks(need_update)

    def async_update(self):
        thread.start_new_thread(DBTaskManager.update, (self, ))
