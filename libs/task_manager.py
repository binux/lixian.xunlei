# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from time import time
from collections import deque
from libs.lixian_api import LiXianAPI
from libs.util import determin_url_type

FINISHED_CHECK_INTERVAL = 24*60*60
DOWNLOADING_CHECK_INTERVAL = 60*60
UPDATE_TASK_LIMIT = 9000

class TaskManager(object):
    def __init__(self, username, password, check_interval = 60*60):
        self.username = username
        self.password = password
        self.check_interval = check_interval
        self.islogin = False
        self._last_check_login = 0

        self._xunlei = LiXianAPI()

        self._tasks = dict()
        self._task_list = deque()
        self._task_urls = set()
        self._last_update_task_list = 0

        self._file_list = dict()

        self.login()

    @property
    def xunlei(self):
        if self._last_check_login + self.check_interval < time():
            if not self.xunlei.check_login():
                self._xunlei.logout()
                self.islogin = self.login()
        return self._xunlei

    @property
    def gdriveid(self):
        return self.xunlei.gdriveid

    def login(self):
        self.islogin = self._xunlei.login(self.username, self.password)
        self._last_check_login = time()
        return self.islogin

    def _update_task_list(self, limit=10, st=0, ignore=False):
        tasks = self.xunlei.get_task_list(limit, st)
        for task in tasks[::-1]:
            task['last_update_time'] = time()
            if task['task_id'] not in self._tasks:
                if ignore: continue
                self._task_list.appendleft(task)
            self._tasks[task['task_id']] = task
            self._task_urls.add(task['url'])

    def get_task(self, task_id):
        if task_id in self._tasks:
            return self._tasks[task_id]
        else:
            return None

    def get_task_list(self, start_task_id=0, limit=50):
        if self._last_update_task_list + FINISHED_CHECK_INTERVAL < time():
            self._update_task_list(UPDATE_TASK_LIMIT)
            self._last_update_task_list = time()

        result = []
        count = 0
        need_update = False
        pos = 0

        for task in self._task_list:
            pos += 1
            if start_task_id and task['task_id'] > start_task_id: continue
            if count >= limit: break
            result.append(task)
            count += 1

            if task['status'] != "finished" and task['last_update_time'] \
                    + self._get_check_interval(task['status']) < time():
                need_update = True

        if need_update:
            self._update_task_list(UPDATE_TASK_LIMIT, "downloading")

        return result

    def get_file_list(self, task_id):
        task = self.get_task(task_id)
        if not task: return {}

        if task_id in self._file_list:
            file_list = self._file_list[task_id]
            if file_list["last_update_time"] \
                    + self._get_check_interval(task['status']) > time():
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

        self._file_list[task_id] = {"last_update_time": time(), "files": files}
        return files

    def add_task(self, url):
        if url in self._task_urls:
            return False
        url_type = determin_url_type(url)

        if url_type in ("bt", "magnet"):
            return self.xunlei.add_bt_task(url)
        elif url_type in ("normal", "ed2k", "thunder"):
            return self.xunlei.add_task(url)
        else:
            return self.xunlei.add_batch_task([url, ])

    def _get_check_interval(self, status):
        if status == "finished":
            return FINISHED_CHECK_INTERVAL
        else:
            return DOWNLOADING_CHECK_INTERVAL
