#/usr/bin/env python
# -*- encoding: utf8 -*-
# author: binux<17175297.hk@gmail.com>

import os
import tornado
import logging
from time import time
from tornado import web
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import define, options
from tornado.httpserver import HTTPServer

define("f", default="", help="config file path")
define("debug", default=True, help="debug mode")
define("port", default=8880, help="the port tornado listen to")
define("bind_ip", default="0.0.0.0", help="the bind ip")
define("username", help="xunlei vip login name")
define("password", help="xunlei vip password")
define("ga_account", default="", help="account of google analytics")
define("site_name", default="LOLI.LU", help="site name used in description")
define("cookie_secret", default="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o",
        help="key for HMAC")
define("check_interval", default=60*60,
        help="the interval of checking login status")
define("cache_enabled", default=True,
        help="enable mem cache")
define("cross_userscript", default="http://userscripts.org/scripts/show/117745",
        help="the web url of cross cookie userscirpt")
define("cross_cookie_version", default="0.2",
        help="cross cookie user script version")
define("cross_userscript_local", default="/static/cross-cookie.user.js",
        help="the local path of cross cookie userscirpt")
define("cross_cookie_url", default="http://vip.xunlei.com/gen/yuanxun/gennew/newyx.html",
        help="the url to insert to")
define("cookie_str", default="gdriveid=%s; path=/; domain=.vip.xunlei.com",
        help="the cookie insert to cross path")
define("finished_task_check_interval", default=60*60,
        help="the interval of getting the task list")
define("downloading_task_check_interval", default=5*60,
        help="the interval of getting the downloading task list")
define("task_list_limit", default=500,
        help="the max limit of get task list each time")
define("always_update_lixian_url", default=False,
        help="always update lixian url")
define("database_echo", default=False,
        help="sqlalchemy database engine echo switch")
define("database_engine", default="sqlite:///task_files.db",
        help="the database connect string for sqlalchemy")
define("task_title_prefix", default="[loli.lu] ",
        help="prefix of task")
define("using_xss", default=False,
        help="use xss or cross-cookie")
define("using_xsrf", default=False,
        help="using xsrf to prevent cross-site request forgery")

class Application(web.Application):
    def __init__(self):
        from handlers import handlers, ui_modules
        from libs.util import ui_methods
        from libs.db_task_manager import DBTaskManager
        from libs.user_manager import UserManager
        from libs.vip_pool import VIPool
        settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=options.cookie_secret,
            login_url="/login",

            ui_modules=ui_modules,
            ui_methods=ui_methods,
        )
        super(Application, self).__init__(handlers, **settings)

        self.user_manager = UserManager()
        self.task_manager = DBTaskManager(
                    username = options.username,
                    password = options.password
                )
        self.vip_pool = VIPool()
        if not self.task_manager.islogin:
            raise Exception, "xunlei login error"
        self.task_manager.async_update()
        PeriodicCallback(self.task_manager.async_update,
                options.downloading_task_check_interval * 1000).start()
        PeriodicCallback(self.user_manager.reset_all_add_task_limit, 86400 * 1000).start()

        logging.info("load finished! listening on %s:%s" % (options.bind_ip, options.port))

def main():
    tornado.options.parse_command_line()
    if options.f:
        tornado.options.parse_config_file(options.f)
    tornado.options.parse_command_line()

    http_server = HTTPServer(Application(), xheaders=True)
    http_server.bind(options.port, options.bind_ip)
    http_server.start()

    IOLoop.instance().start()

if __name__ == "__main__":
    main()
