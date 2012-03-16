# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError, UIModule, authenticated
from tornado.options import options
from .base import BaseHandler

class ManagerIndexHandler(BaseHandler):
    @authenticated
    def get(self, option):
        if not self.has_permission("admin"):
            raise HTTPError(403)
        message = self.get_argument("msg", "DANGER!")
        if option:
            if not hasattr(self, option) or not callable(getattr(self, option)):
                raise HTTPError(404)
            message = getattr(self, option)()
            self.redirect("/manager?msg=%s" % message)
            return

        self.render("manager.html", message=message)

    def flush_mem_cache(self):
        from libs.cache import _mem_caches
        _mem_caches.clear()
        return "清除缓存成功"

    def refetch_finished_tasks(self):
        self.task_manager._last_update_task = 0
        self.task_manager.async_update()
        return "已启动refetch任务"

    def refetch_downloading_tasks(self):
        self.task_manager._last_update_downloading_task = 0
        self.task_manager.async_update()
        return "已启动refetch任务"

    def recheck_login(self):
        self.task_manager._last_check_login = 0
        _ = self.task_manager.xunlei
        return ""

    def set_uid(self):
        uid = int(self.get_argument("uid"))
        gdriveid = self.get_argument("gdriveid")
        tid = int(self.get_argument("tid"))
        self.task_manager._uid = uid
        self.task_manager._gdriveid = gdriveid
        self.task_manager.last_task_id = tid
        return "uid=%s, gdriveid=%s, tid=%s" % (
                self.task_manager.uid,
                self.task_manager.gdriveid,
                self.task_manager.last_task_id)

    def set_tid(self):
        tid = int(self.get_argument("tid"))
        self.task_manager.last_task_id = tid
        return "tid被设置为 %d" % tid

    def clear_tid_sample(self):
        self.task_manager.task_id_sample.clear()
        return ""

    @property
    def logging_level(self):
        import logging
        return logging.getLevelName(logging.getLogger().level)

    def switch_level(self):
        import logging
        root_logging = logging.getLogger()
        if root_logging.level == logging.DEBUG:
            root_logging.setLevel(options.logging.upper())
        else:
            root_logging.level = logging.DEBUG
        return ""

handlers = [
        (r"/manager/?(\w*)", ManagerIndexHandler),
]
ui_modules = {
}
