# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
import traceback
import thread
import tornado
from multiprocessing import Pipe

units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def format_size(request, size):
    i = 0
    while size > 1024:
        size /= 1024
        i += 1
    return "%d%s" % (size, units[i])

d_status = {
        "finished": u"完成",
        "downloading": u"下载中",
        "waiting": u"队列中",
        "failed": u"下载失败",
        "paused": u"暂停中",
}
def format_download_status(request, status):
    return d_status.get(status, u"未知状态")

def email2name(request, email):
    return request.user_manager.get_name(email)

def email2id(request, email):
    return request.user_manager.get_id(email)

ui_methods = {
        "format_size": format_size,
        "format_status": format_download_status,
        "email2name": email2name,
        "email2id": email2id,
}

class AsyncProcessMixin(object):
    def call_subprocess(self, func, callback=None, args=[], kwargs={}):
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.pipe, child_conn = Pipe()

        def wrap(func, pipe, args, kwargs):
            try:
                pipe.send(func(*args, **kwargs))
            except Exception, e:
                logging.error(traceback.format_exc())
                pipe.send(e)
        
        self.ioloop.add_handler(self.pipe.fileno(),
                  self.async_callback(self.on_pipe_result, callback),
                  self.ioloop.READ)
        thread.start_new_thread(wrap, (func, child_conn, args, kwargs))

    def on_pipe_result(self, callback, fd, result):
        try:
            ret = self.pipe.recv()
            if isinstance(ret, Exception):
                raise ret

            if callback:
                callback(ret)
        finally:
            self.ioloop.remove_handler(fd)
