# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError, UIModule, asynchronous
from tornado.auth import GoogleMixin
from tornado.options import options
from .base import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        q = self.get_argument("q", "")
        tasks = self.task_manager.get_task_list(q=q, limit=30)
        self.render("index.html", tasks=tasks, q=q)

class GetNextTasks(BaseHandler):
    def get(self):
        start_task_id = int(self.get_argument("s"))
        q = self.get_argument("q", "")
        tasks = self.task_manager.get_task_list(start_task_id, q=q, limit = 30)
        self.render("task_list.html", tasks=tasks)

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
        self.user_manager.update_user(user["email"], user["name"])
        self.redirect("/")

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

class TaskItems(UIModule):
    def render(self, tasks):
        return self.render_string("task_list.html", tasks=tasks)

handlers = [
        (r"/", IndexHandler),
        (r"/login", LoginHandler),
        (r"/get_lixian_url", GetLiXianURL),
        (r"/next", GetNextTasks),
        (r"/share/(\d+)", ShareHandler),
]
ui_modules = {
        "TaskItems": TaskItems
}
