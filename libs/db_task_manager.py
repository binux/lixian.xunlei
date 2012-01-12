# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
import thread
import random
import socket
import re

import db
from StringIO import StringIO
from db import Session
from time import time
from db.util import *
from libs.lixian_api import LiXianAPI, determin_url_type
from libs.cache import mem_cache
from tornado.options import options
from requests import RequestException

ui_re = re.compile(r"ui=\d+")
ti_re = re.compile(r"ti=\d+")
def fix_lixian_url(url):
    url = ui_re.sub("ui=%(uid)d", url)
    url = ti_re.sub("ti=%(tid)d", url)
    return url

def catch_connect_error(default_return):
    def warp(func):
        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RequestException:
                return default_return
            except socket.timeout:
                return default_return
        return new_func
    return warp

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
        session = Session()
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
            if task.status == "failed":
                task.invalid = True
            task.process = res['process']
            if res['cid'] and res['lixian_url']:
                task.cid = res['cid']
                task.lixian_url = res['lixian_url']

            task = session.merge(task)
            if task.status in ("downloading", "finished"):
                if not self._update_file_list(task):
                    task.status = "downloading"
                    session.add(task)
        session.commit()

    @sqlalchemy_rollback
    def _update_task_list(self, limit=10, st=0, ignore=False):
        session = Session()
        tasks = self.xunlei.get_task_list(limit, st)
        for task in tasks[::-1]:
            if task['status'] == "finished":
                self.last_task_id = task['task_id']
            db_task_status = session.query(db.Task.status).filter(
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
            if db_task.status == "failed":
                db_task.invalid = True
            db_task.process = task['process']
            db_task.size = task['size']
            db_task.format = task['format']

            db_task = session.merge(db_task)
            if not self._update_file_list(db_task):
                db_task.status = "failed"
                db_task.invalid = True
                session.add(db_task)
            
        session.commit()

    @sqlalchemy_rollback
    def _update_file_list(self, task):
        session = Session()
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

            session.merge(db_file)
        return True

    def _restart_all_paused_task(self):
        task_ids = []
        for task in self.xunlei.get_task_list(pagenum=100, st=1):
            if task['status'] == "paused":
                task_ids.append(task['task_id'])
        if task_ids:
            self.xunlei.redownload(task_ids)

    @sqlalchemy_rollback
    def get_task(self, task_id):
        return Session().query(db.Task).get(task_id)

    @sqlalchemy_rollback
    def merge_task(self, task):
        session = Session()
        session.merge(task)
        session.commit()

    @sqlalchemy_rollback
    def get_task_by_cid(self, cid):
        return Session().query(db.Task).filter(db.Task.cid == cid)

    @sqlalchemy_rollback
    def get_task_by_title(self, title):
        return Session().query(db.Task).filter(db.Task.taskname == title)
    
    @sqlalchemy_rollback
    def get_task_list(self, start_task_id=0, limit=30, q="", t="", a="", order=db.Task.createtime, dis=db.desc, all=False):
        session = Session()
        self._last_get_task_list = self.time()
        # base query
        query = session.query(db.Task)
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
            value = session.query(order).filter(db.Task.id == start_task_id).first()
            if not value:
                return []
            if dis == db.desc:
                query = query.filter(order < value[0])
            else:
                query = query.filter(order > value[0])
            query = query.filter(db.Task.id < start_task_id)
        # order or limit
        if not all:
            query = query.filter(db.Task.invalid == False)
        query = query.order_by(dis(order), dis(db.Task.id)).limit(limit)
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
    
    @mem_cache(2*60*60)
    @sqlalchemy_rollback
    def get_tag_list(self):
        from collections import defaultdict
        tags_count = defaultdict(lambda: defaultdict(int))
        for tags, in Session().query(db.Task.tags).filter(db.Task.invalid == False):
            for tag in tags:
                tags_count[tag.lower()][tag] += 1
        result = dict()
        for key, value in tags_count.iteritems():
            items = value.items()
            key = max(items, key=lambda x: x[1])[0]
            result[key] = sum([x[1] for x in items])
        return sorted(result.iteritems(), key=lambda x: x[1], reverse=True)

    @mem_cache(expire=5*60*60)
    @sqlalchemy_rollback
    def get_task_ids(self):
        result = []
        for taskid, in Session().query(db.Task.id):
            result.append(taskid)
        return result

    @catch_connect_error((-99, "connection error"))
    def add_task(self, url, title=None, tags=set(), creator="", anonymous=False, need_miaoxia=True):
        session = Session()
        def update_task(task, title=title, tags=tags, creator=creator, anonymous=anonymous):
            if not task:
                return task
            if task.invalid and not anonymous:
                if title: task.taskname = title
                if tags: task.tags = tags
                task.creator = creator
                task.invalid = False
                session.add(task)
                session.commit()
                _ = task.id
            return task

        def _random():
            return random.randint(100, 999)

        # step 1: determin type
        if isinstance(url, basestring):
            task = session.query(db.Task).filter(db.Task.url == url).first()
            if task:
                return (1, update_task(task))

            url_type = determin_url_type(url)
            if url_type in ("bt", "magnet"):
                check = self.xunlei.bt_task_check
                add_task_with_info = self.xunlei.add_bt_task_with_dict
            elif url_type in ("normal", "ed2k", "thunder"):
                check = self.xunlei.task_check
                add_task_with_info = self.xunlei.add_task_with_dict
            else:
                return (-3, "space error")
                #result = self.xunlei.add_batch_task([url, ])
        else:
            url_type = "torrent"
            check = self.xunlei.torrent_upload
            add_task_with_info = self.xunlei.add_bt_task_with_dict
            url = (url['filename'], StringIO(url['body']))
         
        # get info
        if url_type in ("bt", "torrent", "magnet"):
            if isinstance(url, tuple):
                info = check(*url)
            else:
                info = check(url)
            if not info: return (-1, "check task error")
            if need_miaoxia and not info.get('cid'):
                return (-2, "need miaoxia")
            if need_miaoxia and not self.xunlei.is_miaoxia(info['cid'],
                    [x['index'] for x in info['filelist'] if x['valid']]):
                return (-2, "need miaoxia")
        else:
            if need_miaoxia and not self.xunlei.is_miaoxia(url):
                return (-2, "need miaoxia")
            info = check(url)

        # step 3: check info
        # for bt
        if 'filelist' in info:
            for each in info['filelist']:
                each['valid'] = 1
        # check cid
        if info['cid']:
            task = self.get_task_by_cid(info['cid'])
            if task.count() > 0:
                return (1, update_task(task[0]))
        # check is miaoxia

        # check title
        if title:
            info['title'] = title
        else:
            title = info['title']
        if not info['cid'] and \
                self.get_task_by_title(info['title']).count() > 0:
            info['title'] = "#%s %s" % (_random(), info['title'])

        # step 4: commit & fetch result
        result = add_task_with_info(url, info)
        if not result:
            return (0, "error")
        self._update_task_list(5)

        # step 5: checkout task&fix
        if info['cid']:
            task = self.get_task_by_cid(info['cid']).first()
        elif info['title']:
            task = self.get_task_by_title(info['title']).first()
        else:
            return (-5, "match task error")

        if task:
            if title: task.taskname = title
            if tags: task.tags = tags
            task.creator = creator
            task.invalid = anonymous
            session.add(task)
            session.commit()
            _ = task.id
        return (1, task)

    @sqlalchemy_rollback
    def update(self):
        if self._last_update_task + options.finished_task_check_interval < time():
            self._last_update_task = time()
            self._update_task_list(options.task_list_limit)

        if self._last_update_downloading_task + \
                options.downloading_task_check_interval < self._last_get_task_list or \
           self._last_update_downloading_task + \
                options.finished_task_check_interval < time():
            self._last_update_downloading_task = time()
            need_update = Session().query(db.Task).filter(db.or_(db.Task.status == "waiting", db.Task.status == "downloading")).all()
            if need_update:
                self._update_tasks(need_update)

            # as we can't get real status of a task when it's status is waiting, stop the task with lowest
            # speed. when all task is stoped, restart them.
            nm_list = []
            bt_list = []
            for task_id, task_type in Session().query(db.Task.id, db.Task.task_type).filter(db.Task.status == "downloading"):
                if task_type in ("bt", "magnet"):
                    bt_list.append(task_id)
                else:
                    nm_list.append(task_id)
            if bt_list or nm_list:
                downloading_tasks, summery = self.xunlei.get_task_process(nm_list, bt_list, with_summary=True)
                if int(summery['waiting_num']) == 0:
                    self._restart_all_paused_task()
                if len(downloading_tasks) >= 2:
                    need_stop_task = min(downloading_tasks, key=lambda x: x['speed'])
                    self.xunlei.task_pause([need_stop_task['task_id'], ])
            else:
                self._restart_all_paused_task()

    def async_update(self):
        thread.start_new_thread(DBTaskManager.update, (self, ))
