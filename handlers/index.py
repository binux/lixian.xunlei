# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
import json
from functools import partial
from tornado.web import HTTPError, UIModule, asynchronous
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado import gen
from libs.lixian_api import LiXianAPI
from libs.util import AsyncProcessMixin
from .base import BaseHandler

class IndexHandler(BaseHandler, AsyncProcessMixin):
    def get(self):
        tasks = self.xunlei.get_task_list(limit=30)
        self.render("index.html", tasks=tasks)

class GetNextTasks(BaseHandler, AsyncProcessMixin):
    def get(self):
        start_task_id = int(self.get_argument("s"))
        tasks = self.xunlei.get_task_list(start_task_id, limit = 30)
        self.render("task_list.html", tasks=tasks)

class GetLiXianURL(BaseHandler, AsyncProcessMixin):
    def get(self):
        task_id = int(self.get_argument("task_id"))
        task = self.xunlei.get_task(task_id)
        if task is None:
            raise HTTPError(404)

        files = self.xunlei.get_file_list(task_id)
        if files is None:
            raise HTTPError(500)

        cookie = options.cookie_str % self.xunlei.gdriveid
        self.render("lixian.html", task=task, files=files, cookie=cookie)

class AddTaskHandler(BaseHandler, AsyncProcessMixin):
    @asynchronous
    @gen.engine
    def post(self):
        url = self.get_argument("url")
        
        result = yield gen.Task(self.call_subprocess,
                partial(self.xunlei.add_task, url))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"result": result}))
        self.finish()

class ShareHandler(BaseHandler, AsyncProcessMixin):
    def get(self, task_id):
        task_id = int(task_id)

        task = self.xunlei.get_task(task_id)
        if task is None:
            raise HTTPError(404)

        files = self.xunlei.get_file_list(task_id)
        if files is None:
            raise HTTPError(500)

        cookie = options.cookie_str % self.xunlei.gdriveid
        self.render("share.html", task=task, files=files, cookie=cookie)

class TaskItems(UIModule):
    def render(self, tasks):
        return self.render_string("task_list.html", tasks=tasks)

handlers = [
        (r"/", IndexHandler),
        (r"/get_lixian_url", GetLiXianURL),
        (r"/add_task", AddTaskHandler),
        (r"/next", GetNextTasks),
        (r"/share/(\d+)", ShareHandler),
]
ui_modules = {
        "TaskItems": TaskItems
}
