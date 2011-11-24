# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError
from tornado.options import options
from .base import BaseHandler

class GetLiXianURL(BaseHandler):
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

class ShareHandler(BaseHandler):
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

handlers = [
        (r"/get_lixian_url", GetLiXianURL),
        (r"/share/(\d+)", ShareHandler),
]
ui_modules = {
}
