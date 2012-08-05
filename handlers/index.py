# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError, UIModule
from tornado.options import options
from .base import BaseHandler
from libs.cache import mem_cache

TASK_LIMIT = 30

class IndexHandler(BaseHandler):
    def get(self):
        if not self.has_permission("view_tasklist"):
            self.set_status(403)
            self.render("view_tasklist.html")
            return

        q = self.get_argument("q", "")
        feed = self.get_argument("feed", None)
        view_all = self.has_permission("view_invalid")
        tasks = self.task_manager.get_task_list(q=q, limit=TASK_LIMIT, all=view_all)
        if feed:
            self.set_header("Content-Type", "application/atom+xml")
            self.render("feed.xml", tasks=tasks)
        else:
            self.render("index.html", tasks=tasks, query={"q": q})

class FeedHandler(BaseHandler):
    def get(self):
        self.redirect("/?feed=rss", True)

class SitemapHandler(BaseHandler):
    def get(self):
        taskids = self.task_manager.get_task_ids()
        tags = self.task_manager.get_tag_list()
        self.render("sitemap.xml", taskids=taskids, tags=tags)

class TagHandler(BaseHandler):
    def get(self, tag):
        if not self.has_permission("view_tasklist"):
            self.set_status(403)
            self.render("view_tasklist.html")
            return

        feed = self.get_argument("feed", None)
        tasks = self.task_manager.get_task_list(t=tag, limit=TASK_LIMIT)
        if feed:
            self.set_header("Content-Type", "application/atom+xml")
            self.render("feed.xml", tasks=tasks)
        else:
            self.render("index.html", tasks=tasks, query={"t": tag})

class UploadHandler(BaseHandler):
    def get(self, creator_id):
        if not self.has_permission("view_tasklist"):
            self.set_status(403)
            self.render("view_tasklist.html")
            return

        feed = self.get_argument("feed", None)
        creator = self.user_manager.get_user_email_by_id(int(creator_id)) or "no such user"
        if self.current_user and self.current_user["email"] == creator:
            all = True
        elif self.has_permission("view_invalid"):
            all = True
        else:
            all = False
        tasks = self.task_manager.get_task_list(a=creator, limit=TASK_LIMIT, all=all)
        if feed:
            self.set_header("Content-Type", "application/atom+xml")
            self.render("feed.xml", tasks=tasks)
        else:
            self.render("index.html", tasks=tasks, query={"a": creator_id, "creator": creator})

class GetNextTasks(BaseHandler):
    def get(self):
        if not self.has_permission("view_tasklist"):
            raise HTTPError(403)

        start_task_id = int(self.get_argument("s"))
        q = self.get_argument("q", "")
        t = self.get_argument("t", "")
        a = self.get_argument("a", "")
        creator = ""
        if a:
            creator = self.user_manager.get_user_email_by_id(int(a)) or "no such user"
        if self.current_user and self.current_user["email"] == creator:
            all = True
        elif self.has_permission("view_invalid"):
            all = True
        else:
            all = False
        tasks = self.task_manager.get_task_list(start_task_id,
                q=q, t=t, a=creator, limit = TASK_LIMIT, all=all)
        self.render("task_list.html", tasks=tasks)

class NoIEHandler(BaseHandler):
    def get(self):
        self.render("no-ie.html")

class TaskItemsModule(UIModule):
    def render(self, tasks):
        return self.render_string("task_list.html", tasks=tasks)

class TagsModule(UIModule):
    def render(self, tags):
        if not tags:
            return u"无"
        result = []
        for tag in tags:
            result.append("""<a href="/tag/%s">%s</a>""" % (tag, tag))
        return u", ".join(result)

class TagListModule(UIModule):
    @mem_cache(60*60)
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
        (r"/noie", NoIEHandler),
        (r"/feed", FeedHandler),
        #(r"/sitemap\.xml", SitemapHandler),
        (r"/tag/(.+)", TagHandler),
        (r"/uploader/(\d+)", UploadHandler),
        (r"/next", GetNextTasks),
]
ui_modules = {
        "TaskItems": TaskItemsModule,
        "TagsModule": TagsModule,
        "TagList": TagListModule,
}
