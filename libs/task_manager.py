# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from time import time
from datetime import datetime
from collections import deque
from libs.lixian_api import LiXianAPI, determin_url_type
from tornado.options import options

class TaskManager(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._last_check_login = 0

        self._tasks = dict()
        self._task_list = deque()
        self._task_urls = set()
        self._last_update_task_list = 0

        self._file_list = dict()

        self._xunlei = LiXianAPI()
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
        return self.xunlei.gdriveid

    def _update_task_list(self, limit=10, st=0, ignore=False):
        tasks = self.xunlei.get_task_list(limit, st)
        for task in tasks[::-1]:
            task['last_update_time'] = datetime.now()
            if task['task_id'] not in self._tasks:
                if ignore: continue
                task['first_seen'] = datetime.now()
                self._task_list.appendleft(task)
                self._tasks[task['task_id']] = task
                self._task_urls.add(task['url'])
            else:
                self._tasks[task['task_id']].update(task)

    def get_task(self, task_id):
        if task_id in self._tasks:
            return self._tasks[task_id]
        else:
            return None

    def get_task_list(self, start_task_id=0, limit=30):
        if self._last_update_task_list + options.finished_task_check_interval < time():
            self._update_task_list(options.task_list_limit)
            self._last_update_task_list = time()

        # skip
        pos = iter(self._task_list)
        if start_task_id:
            for task in pos:
                if task['task_id'] == start_task_id:
                    break

        result = []
        count = 0
        need_update = set()
        for task in pos:
            if count >= limit: break
            result.append(task)
            count += 1

            if task['status'] != "finished" and task['last_update_time'] \
                    + options.downloading_task_check_interval < datetime.now():
                need_update.add(task['task_id'])

        if need_update:
            self._update_task_list(options.task_list_limit, "downloading")

        # if updated downloading list and hadn't find task which is
        # needed to update, maybe it's finished.
        # FIXME: try to get info of a specified task
        for task_id in need_update:
            task = self.get_task(task_id)
            if task['last_update_time'] + options.downloading_task_check_interval < datetime.now():
                task['status'] = "finished"
                task['process'] = 100
                if task['task_id'] in self._file_list:
                    del self._file_list[task['task_id']]

        return result

    def get_file_list(self, task_id):
        task = self.get_task(task_id)
        if not task: return {}

        if task_id in self._file_list:
            file_list = self._file_list[task_id]
            if file_list["last_update_time"] \
                    + self._get_check_interval(task['status']) > datetime.now():
                return file_list["files"]

        if task['task_type'] == "normal":
            files = []
            tmp_file = dict(
                    task_id = task['task_id'],
                    url = task['url'],
                    lixian_url = task['lixian_url'],
                    title = task['taskname'],
                    status = task['status'],
                    dirtitle = task['taskname'],
                    process = task['process'],
                    size = task['size'],
                    format = task['format']
                    )
            files.append(tmp_file)
        elif task['task_type'] in ("bt", "magnet"):
            files = self.xunlei.get_bt_list(task['task_id'], task['cid'])

        self._file_list[task_id] = {"last_update_time": datetime.now(), "files": files}
        return files

    def add_task(self, url):
        if url in self._task_urls:
            return False
        url_type = determin_url_type(url)

        if url_type in ("bt", "magnet"):
            result = self.xunlei.add_bt_task(url)
        elif url_type in ("normal", "ed2k", "thunder"):
            result = self.xunlei.add_task(url)
        else:
            result = self.xunlei.add_batch_task([url, ])

        if result:
            self._update_task_list(5)
        return result

    def _get_check_interval(self, status):
        if status == "finished":
            return options.finished_task_check_interval
        else:
            return options.downloading_task_check_interval
