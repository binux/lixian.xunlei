# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import re

from tornado import gen
from tornado.web import HTTPError, UIModule, asynchronous, authenticated
from functools import partial

from base import BaseHandler
from libs.util import AsyncProcessMixin

add_task_info_map = {
     0: u"添加任务失败",
    -1: u"获取任务信息失败",
    -2: u"不允许添加无法秒传的资源",
    -3: u"未知的链接类型",
    -4: u"任务已存在",
    -99: u"与迅雷服务器通信失败，请稍候再试...",
}
_split_re = re.compile(u"[,|，]")
class AddTaskHandler(BaseHandler, AsyncProcessMixin):
    def get(self, anonymous):
        if not self.current_user:
            message = u"please login first"
        else:
            message = ""
        if anonymous:
            self.render("add_task_anonymous.html", message=message)
        else:
            self.render("add_task.html", message=message)

    @authenticated
    @asynchronous
    @gen.engine
    def post(self, anonymous):
        url = self.get_argument("url", None)
        btfile = self.request.files.get("btfile")
        btfile = btfile[0] if btfile else None
        title = self.get_argument("title", None)
        tags = self.get_argument("tags", set())
        anonymous = self.get_argument("anonymous", False)
        render_path = "add_task_anonymous.html" if anonymous else "add_task.html"

        if url is None and btfile is None:
            self.render(render_path, message="任务下载地址不能为空")
            return
        if btfile and len(btfile['body']) > 500*1024:
            self.render(render_path, message="种子文件过大")
            return
        
        if tags:
            tags = set([x.strip() for x in _split_re.split(tags)])

        result, task = yield gen.Task(self.call_subprocess,
                partial(self.task_manager.add_task, btfile or url, title, tags, self.current_user['email'], anonymous))

        if result == 1:
            if task:
                self.write("""<script>
    parent.$('#fancybox-content').css({height: "350px"});
	parent.$.fancybox.resize();
    location='/get_lixian_url?task_id=%d'
</script>""" % task.id)
            else:
                self.write("<script>top.location='/'</script>")
            self.finish()
        else:
            if anonymous:
                self.render("add_task_anonymous.html", message=add_task_info_map.get(result, u"未知错误"))
            else:
                self.render("add_task.html", message=add_task_info_map.get(result, u"未知错误"))

handlers = [
        (r"/add_task(_anonymous)?", AddTaskHandler),
]
ui_modules = {
}
