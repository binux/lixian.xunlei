# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

handlers = []
ui_modules = {}

from handlers import index

handlers.extend(index.handlers)

ui_modules.update(index.ui_modules)
