# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import tornado
import thread
from multiprocessing import Pipe

units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def format_size(request, size):
    i = 0
    while size > 1024:
        size /= 1024
        i += 1
    return "%d%s" % (size, units[i])

def determin_url_type(url):
    url_lower = url.lower()
    if url_lower.endswith(".torrent"):
        return "bt"
    elif url_lower.startswith("ed2k"):
        return "ed2k"
    elif url_lower.startswith("thunder"):
        return "thunder"
    elif url_lower.startswith("magnet"):
        return "magnet"
    else:
        return "normal"

ui_methods = {
        "format_size": format_size,
}

class AsyncProcessMixin(object):
    def call_subprocess(self, func, callback=None, args=[], kwargs={}):
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.pipe, child_conn = Pipe()

        def wrap(func, pipe, args, kwargs):
            pipe.send(func(*args, **kwargs))
        
        self.ioloop.add_handler(self.pipe.fileno(),
                  self.async_callback(self.on_pipe_result, callback),
                  self.ioloop.READ)
        thread.start_new_thread(wrap, (func, child_conn, args, kwargs))

    def on_pipe_result(self, callback, fd, result):
        try:
            if callback:
                callback(self.pipe.recv())
        except Exception, e:
            logging.error(e)
        finally:
            self.ioloop.remove_handler(fd)
