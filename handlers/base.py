# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from time import time
from tornado.web import RequestHandler
from tornado.options import options

class BaseHandler(RequestHandler):
    @property
    def xunlei(self):
        app = self.application
        if app._last_check_login + options.check_interval < time():
            if not app.xunlei.check_login():
                app.relogin()
        return app.xunlei

    def render_string(self, template_name, **kwargs):
        return super(BaseHandler, self).render_string(template_name, **kwargs)
