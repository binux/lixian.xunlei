# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError, UIModule, authenticated
from tornado.options import options
from .base import BaseHandler

class ManagerIndexHandler(BaseHandler):
    @authenticated
    def get(self, option):
        if not self.has_permission("admin"):
            raise HTTPError(403, "You might not have permissiont to do that.")
        message = self.get_argument("msg", "DANGER!")
        if option:
            if not hasattr(self, option) or not callable(getattr(self, option)):
                raise HTTPError(404, "option not exists.")
            message = getattr(self, option)()
            if self.request.method == "GET":
                self.render("manager.html", message=message)
            else:
                self.redirect("/manager?msg=%s" % message)
            return

        self.render("manager.html", message=message)

    post = get

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

    def set_vip_pool(self):
        pool_lines = self.get_argument("pool", "")
        self.vip_pool.pool = {}
        self.vip_pool.parser_mline(pool_lines)

    def set_tid(self):
        tid = int(self.get_argument("tid"))
        self.task_manager.last_task_id = tid
        return "tid被设置为 %d" % tid

    def clear_tid_sample(self):
        self.task_manager.task_id_sample.clear()
        return ""

    def change_user_group(self):
        user_id = int(self.get_argument("user_id"))
        group = int(self.getargument("group"))
        user = self.user_manager.get_user_by_id(user_id)
        if not user:
            raise HTTPError(404, "User not found.")
        user.group = group
        self.user_manager.session.add(user)
        self.user_manager.session.commit()
        return "OK"

    def block_user(self):
        user_id = int(self.get_argument("user_id"))
        user = self.user_manager.get_user_by_id(user_id)
        if not user:
            return "No such user"
        user.group = "block"
        self.user_manager.session.add(user)
        self.user_manager.session.commit()
        return "OK"

    def get_user_email(self):
        user_id = int(self.get_argument("user_id"))
        return self.user_manager.get_user_email_by_id(user_id)

    @property
    def logging_level(self):
        import logging
        return logging.getLevelName(logging.getLogger().level)

    def switch_level(self):
        import logging
        root_logging = logging.getLogger()
        if root_logging.level == logging.DEBUG:
            root_logging.setLevel(logging.INFO)
        else:
            root_logging.level = logging.DEBUG
        return ""

    def get_add_task_limit(self):
        return "%r" % self.user_manager.add_task_limit_used

    def get_reload_limit(self):
        return "%r" % self.user_manager.reload_limit

    def reset_limit(self):
        return self.user_manager.reset_all_add_task_limit()

handlers = [
        (r"/manager/?(\w*)", ManagerIndexHandler),
]
ui_modules = {
}
