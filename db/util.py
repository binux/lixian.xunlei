# -*- encoding: utf8 -*-
# author: binux<17175297.hk@gmail.com>

import db
from multiprocessing import Lock

__all__ = ("sqlite_fix", "sqlalchemy_rollback")

sqlite_lock = Lock
def sqlite_fix(func):
    if db.engine.name == "sqlite":
        def wrap(self, *args, **kwargs):
            with sqlite_lock:
                if self.session:
                    self.session.close()
                self.session = db.Session(weak_identity_map=False)
                result = func(self, *args, **kwargs)
                self.session.close()
            return result
        return wrap
    else:
        return func

def sqlalchemy_rollback(func):
    def wrap(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except db.SQLAlchemyError, e:
            self.session.rollback()
            raise
    return wrap
