# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError
from tornado.options import options
from .base import BaseHandler

class GetLiXianURLHandler(BaseHandler):
    def get(self):
        task_id = int(self.get_argument("task_id"))
        referer = self.request.headers.get("referer")
        if referer and not self.request.host in referer:
            self.redirect("/share/"+str(task_id))
            return
        
        task = self.task_manager.get_task(task_id)
        if task is None:
            raise HTTPError(404)

        files = self.task_manager.get_file_list(task_id)
        if files is None:
            raise HTTPError(500)

        cookie = options.cookie_str % self.task_manager.gdriveid
        self.render("lixian.html", task=task, files=files, cookie=cookie)

class IDMExportHandler(BaseHandler):
    def get(self, task_id):
        template = "<\r\n%s\r\ncookie: gdriveid=%s\r\n>\r\n"
        files = self.task_manager.get_file_list(task_id)
        if files is None:
            raise HTTPError(500)

        self.set_header("Content-Type", "application/octet-stream")
        for f in files:
            self.write(template % (f.lixian_url, self.task_manager.gdriveid))

class ShareHandler(BaseHandler):
    def get(self, task_id):
        task_id = int(task_id)

        task = self.task_manager.get_task(task_id)
        if task is None:
            raise HTTPError(404)

        files = self.task_manager.get_file_list(task_id)
        if files is None:
            raise HTTPError(500)

        cookie = options.cookie_str % self.task_manager.gdriveid
        self.render("share.html", task=task, files=files, cookie=cookie)

class XSSDoneHandler(BaseHandler):
    def get(self):
        self.set_cookie("xss", "done")

handlers = [
        (r"/get_lixian_url", GetLiXianURLHandler),
        (r"/export/"+options.site_name+"_idm_(\d+).*?\.ef2", IDMExportHandler),
        (r"/share/(\d+)", ShareHandler),
        (r"/xss", XSSDoneHandler),
]
ui_modules = {
}
