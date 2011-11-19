# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
import json
from functools import partial
from tornado.auth import GoogleMixin
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

add_task_info_map = {
     0: "添加任务失败",
    -1: "获取任务信息失败",
    -2: "不允许添加无法秒传的资源",
    -3: "未知的链接类型"
}
class AddTaskHandler(BaseHandler, AsyncProcessMixin):
    def get(self):
        self.render("add_task.html", message=None)

    @asynchronous
    @gen.engine
    def post(self):
        url = self.get_argument("url", None)
        title = self.get_argument("title", None)
        tags = self.get_argument("tags", None)
        if url is None:
          self.render("add_task.html", message="任务下载地址不能为空")
        
        result, info = yield gen.Task(self.call_subprocess,
                partial(self.xunlei.add_task, url, title, tags))
        if result == 1:
          self.write("<script>top.location='/'</script>")
          self.finish()
        else:
          self.render("add_task.html", message=add_task_info_map.get(result, "未知错误"))

class LoginHandler(BaseHandler, GoogleMixin):
    @asynchronous
    def get(self):
       if self.get_argument("openid.mode", None):
           self.get_authenticated_user(self.async_callback(self._on_auth))
           return
       self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            raise HTTPError(500, "Google auth failed")
        self.set_secure_cookie("name", user["name"])
        self.set_secure_cookie("email", user["email"])
        self.redirect("/")

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
        (r"/login", LoginHandler),
        (r"/get_lixian_url", GetLiXianURL),
        (r"/add_task", AddTaskHandler),
        (r"/next", GetNextTasks),
        (r"/share/(\d+)", ShareHandler),
]
ui_modules = {
        "TaskItems": TaskItems
}
