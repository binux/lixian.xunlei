# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import re

from tornado.web import HTTPError, UIModule, authenticated
from functools import partial

from base import BaseHandler

_split_re = re.compile(u"[,|，, ]")
class EditTaskHandler(BaseHandler):
    @authenticated
    def get(self, message=""):
        task_id = self.get_argument("task_id")
        task = self.task_manager.get_task(int(task_id))
        if self.current_user['email'] != task.creator and\
           not self.user_manager.check_permission(self.current_user['email'], "admin"):
               raise HTTPError(403)
        self.render("edit.html", task=task, message=message)

    @authenticated
    def post(self):
        task_id = self.get_argument("task_id")
        task = self.task_manager.get_task(int(task_id))
        title = self.get_argument("title", None)
        tags = self.get_argument("tags", "")
        public = self.get_argument("public", False)
        if tags:
            tags = set([x.strip() for x in _split_re.split(tags)])
        if self.current_user['email'] != task.creator and\
           not self.user_manager.check_permission(self.current_user['email'], "admin"):
               raise HTTPError(403)
        task.taskname = title
        task.tags = tags
        task.invalid = not public
        self.task_manager.merge_task(task)
        return self.get("修改成功")

handlers = [
        (r"/edit", EditTaskHandler),
]
ui_modules = {
}
