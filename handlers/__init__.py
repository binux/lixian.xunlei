# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

handlers = []
ui_modules = {}

from handlers import index, add_task

handlers.extend(index.handlers)
handlers.extend(add_task.handlers)

ui_modules.update(index.ui_modules)
ui_modules.update(add_task.ui_modules)
