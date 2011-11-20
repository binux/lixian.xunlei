# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
import json
from functools import partial
from tornado.auth import GoogleMixin
from tornado.web import HTTPError, UIModule, asynchronous, authenticated
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado import gen
from libs.lixian_api import LiXianAPI
from libs.util import AsyncProcessMixin
from .base import BaseHandler

class IndexHandler(BaseHandler, AsyncProcessMixin):
    def get(self):
        q = self.get_argument("q", "")
        tasks = self.task_manager.get_task_list(q=q, limit=30)
        self.render("index.html", tasks=tasks, q=q)

class GetNextTasks(BaseHandler, AsyncProcessMixin):
    def get(self):
        start_task_id = int(self.get_argument("s"))
        q = self.get_argument("q", "")
        tasks = self.task_manager.get_task_list(start_task_id, q=q, limit = 30)
        self.render("task_list.html", tasks=tasks)

class GetLiXianURL(BaseHandler, AsyncProcessMixin):
    def get(self):
        task_id = int(self.get_argument("task_id"))
        task = self.task_manager.get_task(task_id)
        if task is None:
            raise HTTPError(404)

        files = self.task_manager.get_file_list(task_id)
        if files is None:
            raise HTTPError(500)

        cookie = options.cookie_str % self.task_manager.gdriveid
        self.render("lixian.html", task=task, files=files, cookie=cookie)

add_task_info_map = {
     0: u"添加任务失败",
    -1: u"获取任务信息失败",
    -2: u"不允许添加无法秒传的资源",
    -3: u"未知的链接类型",
    -4: u"任务已存在",
}
class AddTaskHandler(BaseHandler, AsyncProcessMixin):
    def get(self):
        if not self.current_user:
            message = u"please login first"
        else:
            message = ""
        self.render("add_task.html", message=message)

    @authenticated
    @asynchronous
    @gen.engine
    def post(self):
        url = self.get_argument("url", None)
        title = self.get_argument("title", None)
        tags = self.get_argument("tags", set())
        if url is None:
            self.render("add_task.html", message="任务下载地址不能为空")
            return
        
        if tags:
            tags = set([x.strip() for x in tags.split(u",|，")])
        result, task = yield gen.Task(self.call_subprocess,
                partial(self.task_manager.add_task, url, title, tags, self.current_user['email']))
        if result == 1:
            if task:
                self.write("<script>top.location='/share/%d'</script>" % task.id)
            else:
                self.write("<script>top.location='/'</script>")
            self.finish()
        else:
            self.render("add_task.html", message=add_task_info_map.get(result, u"未知错误"))

class LoginHandler(BaseHandler, GoogleMixin):
    @asynchronous
    def get(self):
       if self.get_argument("openid.mode", None):
           self.get_authenticated_user(self.async_callback(self._on_auth))
           return
       if self.get_argument("logout", None):
           self.clear_cookie("name")
           self.clear_cookie("email")
           self.redirect("/")
           return
       self.authenticate_redirect(callback_uri=options.oauth_callback_uri)

    def _on_auth(self, user):
        if not user:
            raise HTTPError(500, "Google auth failed")
        self.set_secure_cookie("name", user["name"])
        self.set_secure_cookie("email", user["email"])
        self.redirect("/")

class ShareHandler(BaseHandler, AsyncProcessMixin):
    def get(self, task_id):
        task_id = int(task_id)

        task = self.task_manager.get_task(task_id)
        if task is None:
            raise HTTPError(404)

        files = self.task_manager.get_file_list(task_id)
        if files is None:
            raise HTTPError(500)

        cookie = options.cookie_str % self.task_manager.gdriveid
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
