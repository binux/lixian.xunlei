# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import RequestHandler

class BaseHandler(RequestHandler):
    def render_string(self, template_name, **kwargs):
        return super(BaseHandler, self).render_string(template_name, **kwargs)
