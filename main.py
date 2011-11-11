#/usr/bin/env python
# -*- encoding: utf8 -*-
# author: binux<17175297.hk@gmail.com>

import os
import tornado
from tornado import web
from tornado.ioloop import IOLoop
from tornado.options import define, options

define("debug", default=True, help="debug mode")
define("port", default=8880, help="the port tornado listen to")

class Application(web.Application):
    def __init__(self):
        from handlers import handlers, ui_modules
        settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),

            ui_modules=ui_modules,
            ui_methods={},
        )
        super(Application, self).__init__(handlers, **settings)

def main():
    tornado.options.parse_command_line()

    application = Application()
    application.listen(options.port)
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
