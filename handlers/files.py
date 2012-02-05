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
        if files == []:
            raise HTTPError(404)

        self.set_header("Content-Type", "application/octet-stream")
        for f in files:
            self.write(template % (f.lixian_url, self.task_manager.gdriveid))

class aria2cExportHandler(BaseHandler):
    def get(self, task_id):
        template = "%s\r\n  out=%s\r\n  header=Cookie: gdriveid=%s\r\n  continue=true\r\n  max-connection-per-server=5\r\n  split=10\r\n  parameterized-uri=true\r\n\r\n"
        files = self.task_manager.get_file_list(task_id)
        if files is None:
            raise HTTPError(500)
        if files == []:
            raise HTTPError(404)

        self.set_header("Content-Type", "application/octet-stream")
        for f in files:
            self.write(template % (f.lixian_url.replace("gdl", "{gdl,dl.f,dl.g,dl.h,dl.i,dl.twin}"), f.dirtitle, self.task_manager.gdriveid))

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

class XSSJSHandler(BaseHandler):
    def get(self):
        v = int(self.get_argument("v", 0))
        if v == 0:
            render_tpl = "xss.js"
        else:
            render_tpl = "xss2.js"

        cookie = options.cookie_str % self.task_manager.gdriveid
        self.render(render_tpl, cookie=cookie)

handlers = [
        (r"/get_lixian_url", GetLiXianURLHandler),
        (r"/export/"+options.site_name+"_idm_(\d+).*?\.ef2", IDMExportHandler),
        (r"/export/"+options.site_name+"_aria2c_(\d+).*?\.down", aria2cExportHandler),
        (r"/share/(\d+)", ShareHandler),
        (r"/xss", XSSDoneHandler),
        (r"/xssjs", XSSJSHandler),
]
ui_modules = {
}
