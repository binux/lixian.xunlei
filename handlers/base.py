# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from time import time
from tornado.web import RequestHandler
from tornado.options import options

class BaseHandler(RequestHandler):
    @property
    def xunlei(self):
        return self.application.task_manager

    def render_string(self, template_name, **kwargs):
        kwargs["options"] = options
        return super(BaseHandler, self).render_string(template_name, **kwargs)
