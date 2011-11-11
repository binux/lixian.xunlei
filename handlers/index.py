# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError
from .base import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        self.render("base.html")

handlers = [
        (r"/", IndexHandler),
        ]
ui_modules = {}
