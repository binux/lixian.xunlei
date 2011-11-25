# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError, UIModule
from tornado.options import options
from .base import BaseHandler

TASK_LIMIT = 30

class IndexHandler(BaseHandler):
    def get(self):
        q = self.get_argument("q", "")
        tasks = self.task_manager.get_task_list(q=q, limit=TASK_LIMIT)
        self.render("index.html", tasks=tasks, query={"q": q})

class TagHandler(BaseHandler):
    def get(self, tag):
        tasks = self.task_manager.get_task_list(t=tag, limit=TASK_LIMIT)
        self.render("index.html", tasks=tasks, query={"t": tag})

class UploadHandler(BaseHandler):
    def get(self, creator):
        tasks = self.task_manager.get_task_list(a=creator, limit=TASK_LIMIT)
        self.render("index.html", tasks=tasks, query={"a": creator})

class GetNextTasks(BaseHandler):
    def get(self):
        start_task_id = int(self.get_argument("s"))
        q = self.get_argument("q", "")
        t = self.get_argument("t", "")
        a = self.get_argument("a", "")
        tasks = self.task_manager.get_task_list(start_task_id,
                q=q, t=t, a=a, limit = TASK_LIMIT)
        self.render("task_list.html", tasks=tasks)

class TaskItemsModule(UIModule):
    def render(self, tasks):
        return self.render_string("task_list.html", tasks=tasks)

class TagsModule(UIModule):
    def render(self, tags):
        result = []
        for tag in tags:
            result.append("""<a href="/tag/%s">%s</a>""" % (tag, tag))
        return u", ".join(result)

class TagListModule(UIModule):
    def render(self):
        def size_type(count):
            if count < 10:
                return 1
            elif count < 100:
                return 2
            else:
                return 3

        tags = self.handler.task_manager.get_tag_list()
        return self.render_string("tag_list.html", tags=tags, size_type=size_type)

handlers = [
        (r"/", IndexHandler),
        (r"/tag/(.*)", TagHandler),
        (r"/uploader/(.*)", UploadHandler),
        (r"/next", GetNextTasks),
]
ui_modules = {
        "TaskItems": TaskItemsModule,
        "TagsModule": TagsModule,
        "TagList": TagListModule,
}
