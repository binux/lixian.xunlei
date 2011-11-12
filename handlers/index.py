# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError
from .base import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        tasks = [
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][02][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][04][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][05][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][06][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][07][GB][R10][848X480][rmvb][WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][08][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][02][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][04][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][05][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][06][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][07][GB][R10][848X480][rmvb][WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][08][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][02][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][04][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][05][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][06][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][07][GB][R10][848X480][rmvb][WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][08][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][02][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][04][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][05][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][06][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][07][GB][R10][848X480][rmvb][WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][08][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][02][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][04][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][05][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][06][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][07][GB][R10][848X480][rmvb][WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][08][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][02][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][04][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][05][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][06][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][07][GB][R10][848X480][rmvb][WOLF][Nurarihyon no Mago2 Sennen Makyo][03][GB][R10][848X480][rmvb]",
                "[WOLF][Nurarihyon no Mago2 Sennen Makyo][08][GB][R10][848X480][rmvb]",
                ]
        self.render("index.html", tasks=tasks)

handlers = [
        (r"/", IndexHandler),
        ]
ui_modules = {}
