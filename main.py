#/usr/bin/env python
# -*- encoding: utf8 -*-
# author: binux<17175297.hk@gmail.com>

import os
import tornado
import logging
from time import time
from tornado import web
from tornado.ioloop import IOLoop
from tornado.options import define, options

define("debug", default=True, help="debug mode")
define("port", default=8880, help="the port tornado listen to")
define("username", help="xunlei vip login name")
define("password", help="xunlei vip password")
define("check_interval", default=60*60, help="the interval of checking login status")

class Application(web.Application):
    def __init__(self):
        from handlers import handlers, ui_modules
        from libs.util import ui_methods
        from libs.lixian_api import LiXianAPI
        settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),

            ui_modules=ui_modules,
            ui_methods=ui_methods,
        )
        super(Application, self).__init__(handlers, **settings)

        self.xunlei = LiXianAPI()
        if not self.xunlei.login(options.username, options.password):
            raise Exception, "xunlei login error"
        self._last_check_login = time()
        logging.info("load finished!")

    def relogin(self):
        self.xunlei.logout()
        if not self.xunlei.login(options.username, options.password):
            raise Exception, "xunlei login error"
        self._last_check_login = time()


def main():
    tornado.options.parse_command_line()

    application = Application()
    application.listen(options.port)
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
