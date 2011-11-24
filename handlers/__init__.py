# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

handlers = []
ui_modules = {}

from handlers import index, files, add_task, login

handlers.extend(index.handlers)
handlers.extend(files.handlers)
handlers.extend(add_task.handlers)
handlers.extend(login.handlers)

ui_modules.update(index.ui_modules)
ui_modules.update(files.ui_modules)
ui_modules.update(add_task.ui_modules)
ui_modules.update(login.ui_modules)
