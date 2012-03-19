# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
import random

class VIPool:
    def __init__(self):
        self.pool = {}

    def parser(self, line):
        try:
            uid, gdriveid, tid = line.split(":", 2)
            return {"uid": int(uid),
                    "gdriveid": gdriveid,
                    "tid": int(tid)
                   }
        except:
            logging.error("unknow vip format: %s" % line)
        return {}

    def parser_line(self, line):
        ret = self.parser(line)
        if ret:
            self.pool[ret["gdriveid"]] = ret

    def parser_mline(self, lines):
        for line in lines.split("\n"):
            line = line.strip()
            self.parser_line(line)

    def get_vip(self, gdriveid=None):
        if not self.pool:
            return None

        if not gdriveid:
            gdriveid = random.choice(self.pool.keys())
        elif ":" in gdriveid:
            ret = self.parser(gdriveid)
            if ret:
                return ret
        elif gdriveid not in self.pool:
            gdriveid = random.choice(self.pool.keys())

        return self.pool[gdriveid]

    def serialize(self):
        result = []
        for each in self.pool.values():
            result.append("%(uid)s:%(gdriveid)s:%(tid)s" % each)
        return "\n".join(result)
