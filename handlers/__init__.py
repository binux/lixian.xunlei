# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

handlers = []
ui_modules = {}

modules = ['index', 'files', 'add_task', 'edit_task', 'login', 'manager', ]

for module in modules:
    module = __import__("handlers."+module, fromlist=["handlers"])
    handlers.extend(module.handlers)
    ui_modules.update(module.ui_modules)
