# -*- encoding: utf8 -*-
# author: binux<17175297.hk@gmail.com>

import db
from threading import RLock

__all__ = ("sqlite_fix", "sqlalchemy_rollback")

sqlite_lock = RLock()
def sqlite_fix(func):
    if db.engine.name == "sqlite":
        def wrap(self, *args, **kwargs):
            with sqlite_lock:
                self.session.close()
                result = func(self, *args, **kwargs)
            return result
        return wrap
    else:
        return func

def sqlalchemy_rollback(func):
    def wrap(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except db.SQLAlchemyError, e:
            db.Session().rollback()
            raise
    return wrap
