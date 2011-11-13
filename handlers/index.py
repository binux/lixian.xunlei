# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
import json
from tornado.web import HTTPError
from libs.util import determin_url_type
from .base import BaseHandler

task_list = []
class IndexHandler(BaseHandler):
    def get(self):
        global task_list
        tasks = self.xunlei.get_task_list(1000)
        task_list = tasks
        self.render("index.html", tasks=tasks)

class GetLiXianURL(BaseHandler):
    def get(self):
        global task_list
        task_id = int(self.get_argument("task_id"))

        if not task_list:
            task_list = self.xunlei.get_task_list()
        task = None
        for each in task_list:
            if each['task_id'] == task_id:
                task = each
        if task is None:
            raise HTTPError(404)

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
        self.render("lixian.html", task=task, files=files)

class AddTaskHandler(BaseHandler):
    def post(self):
        global task_list
        url = self.get_argument("url")
        url_type = determin_url_type(url)

        result = False
        if url_type in ("bt", "magnet"):
            result = self.xunlei.add_bt_task(url)
        elif url_type in ("normal", "ed2k", "thunder"):
            result = self.xunlei.add_task(url)
        else:
            result = self.xunlei.add_batch_task([url, ])

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"result": result}))

handlers = [
        (r"/", IndexHandler),
        (r"/get_lixian_url", GetLiXianURL),
        (r"/add_task", AddTaskHandler),
        ]
ui_modules = {}
