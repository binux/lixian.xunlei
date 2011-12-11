# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from time import time
from tornado.web import RequestHandler
from tornado.options import options

class BaseHandler(RequestHandler):
    @property
    def task_manager(self):
        return self.application.task_manager

    @property
    def user_manager(self):
        return self.application.user_manager

    def render_string(self, template_name, **kwargs):
        kwargs["options"] = options
        return super(BaseHandler, self).render_string(template_name, **kwargs)

    def get_current_user(self):
        email = self.get_secure_cookie("email")
        name = self.get_secure_cookie("name")
        if email and name:
            return {
                    "email": email,
                    "name": name,
                    "group": self.user_manager.get_group(email),
                    "permission": self.user_manager.get_permission(email),
                   }
        elif self.request.remote_ip in ("localhost", "127.0.0.1"):
            return {
                    "email": "bot@localhost",
                    "name": "bot",
                    "group": "bot",
                    "permission": 999,
                    }
        else:
            return None
