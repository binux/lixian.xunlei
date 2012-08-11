# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError
from tornado.options import options
from .base import BaseHandler

import re
from urllib import quote_plus
from libs.tools import thunder_filename_encode

class GetLiXianURLHandler(BaseHandler):
    def get(self):
        if not self.has_permission("view_tasklist"):
            self.set_status(403)
            self.render("view_tasklist.html")
            return

        task_id = int(self.get_argument("task_id"))
        referer = self.request.headers.get("referer")
        if referer and not self.request.host in referer[4:10+len(self.request.host)]:
            self.redirect("/share/"+str(task_id))
            return
        
        task = self.task_manager.get_task(task_id)
        if task is None:
            raise HTTPError(404, "task is not exists.")

        vip_info = self.get_vip()
        files = self.task_manager.get_file_list(task_id, vip_info)
        if files is None:
            raise HTTPError(500, "Error when getting file list.")

        cookie = options.cookie_str % vip_info["gdriveid"]
        self.render("lixian.html", task=task, files=files, cookie=cookie, gdriveid=vip_info["gdriveid"])

class ShareHandler(BaseHandler):
    def get(self, task_id):
        task_id = int(task_id)

        if not options.enable_share:
            raise HTTPError(404, "share is not enabled")

        task = self.task_manager.get_task(task_id)
        if task is None:
            raise HTTPError(404, "Task not exists.")

        vip_info = self.get_vip()
        files = self.task_manager.get_file_list(task_id, vip_info)
        if files is None:
            raise HTTPError(500, "Error when getting file list.")

        cookie = options.cookie_str % vip_info["gdriveid"]
        self.render("share.html", task=task, files=files, cookie=cookie, gdriveid=vip_info["gdriveid"])

class XSSDoneHandler(BaseHandler):
    def get(self):
        gdriveid = self.get_argument("gdriveid")
        cookie = options.cookie_str % gdriveid
        self.write('document.cookie="%s"' % cookie)
        self.set_cookie("xss", gdriveid)

class XSSJSHandler(BaseHandler):
    def get(self):
        render_tpl = "xss.js"

        gdriveid = self.get_vip()["gdriveid"]
        cookie = options.cookie_str % gdriveid
        self.render(render_tpl, cookie=cookie, gdriveid=gdriveid)

class XSSCheckHandler(BaseHandler):
    def get(self):
        gdriveid = self.get_argument("gdriveid")
        self.render("xss_check.js", gdriveid=gdriveid)

lixian_n_re = re.compile(r"&n=\w+")
class IDMExportHandler(BaseHandler):
    def get(self, task_id):
        index = self.get_argument("i", None)
        if index:
            try:
                index = set((int(x) for x in index.split(",")))
            except:
                raise HTTPError(403, "Request format error.")

        def rewrite_url(url, filename):
            return lixian_n_re.sub("&n="+thunder_filename_encode(filename), url)

        vip_info = self.get_vip()
        template = "<\r\n%s\r\ncookie: gdriveid=%s\r\n>\r\n"
        files = self.task_manager.get_file_list(task_id, vip_info)
        if files is None:
            raise HTTPError(500, "Error when getting file list.")
        if files == []:
            raise HTTPError(404, "Task not exists.")

        gdriveid = vip_info["gdriveid"]
        self.set_header("Content-Type", "application/octet-stream")
        if index:
            files = (x for i, x in enumerate(files) if i in index)
        for f in files:
            if not f.lixian_url:
                continue
            self.write(template % (rewrite_url(f.lixian_url, f.dirtitle), gdriveid))

class aria2cExportHandler(BaseHandler):
    def get(self, task_id):
        index = self.get_argument("i", None)
        if index:
            try:
                index = set((int(x) for x in index.split(",")))
            except:
                raise HTTPError(403, "Request format error.")

        template = "%s\r\n  out=%s\r\n  header=Cookie: gdriveid=%s\r\n  continue=true\r\n  max-connection-per-server=5\r\n  split=10\r\n  parameterized-uri=true\r\n\r\n"
        vip_info = self.get_vip()
        files = self.task_manager.get_file_list(task_id, vip_info)
        if files is None:
            raise HTTPError(500, "Error when getting file list.")
        if files == []:
            raise HTTPError(404, "Task not exists.")

        gdriveid = vip_info["gdriveid"]
        self.set_header("Content-Type", "application/octet-stream")
        if index:
            files = (x for i, x in enumerate(files) if i in index)
        for f in files:
            if not f.lixian_url:
                continue
            self.write(template % (f.lixian_url.replace("gdl", "{gdl,dl.f,dl.g,dl.h,dl.i,dl.twin}"), f.dirtitle, gdriveid))

class orbitExportHandler(BaseHandler):
    def get(self, task_id):
        index = self.get_argument("i", None)
        if index:
            try:
                index = set((int(x) for x in index.split(",")))
            except:
                raise HTTPError(403, "Request format error.")

        template = "%s|%s||gdriveid=%s\r\n"
        vip_info = self.get_vip()
        files = self.task_manager.get_file_list(task_id, vip_info)
        if files is None:
            raise HTTPError(500, "Error when getting file list.")
        if files == []:
            raise HTTPError(404, "Task not exists.")

        gdriveid = vip_info["gdriveid"]
        self.set_header("Content-Type", "application/octet-stream")
        if index:
            files = (x for i, x in enumerate(files) if i in index)
        for f in files:
            if not f.lixian_url:
                continue
            self.write(template % (f.lixian_url, f.dirtitle.replace("|", "_"), gdriveid))

handlers = [
        (r"/get_lixian_url", GetLiXianURLHandler),
        (r"/export/"+options.site_name+"_idm_(\d+).*?\.ef2", IDMExportHandler),
        (r"/export/"+options.site_name+"_aria2c_(\d+).*?\.down", aria2cExportHandler),
        (r"/export/"+options.site_name+"_orbit_(\d+).*?\.olt", orbitExportHandler),
        (r"/share/(\d+)", ShareHandler),
        (r"/xss", XSSDoneHandler),
        (r"/xssjs", XSSJSHandler),
        (r"/xss_check.js", XSSCheckHandler),
]
ui_modules = {
}
