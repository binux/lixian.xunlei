# -*- encoding: utf8 -*-

import db
from db.util import *
from libs.cache import mem_cache

class UserManager(object):
    def __init__(self):
        self.session = db.Session()

    @sqlalchemy_rollback
    def get_user(self, email):
        if not email: return None
        return self.session.query(db.User).filter(db.User.email==email).scalar()

    @sqlalchemy_rollback
    def update_user(self, email, name):
        user = self.get_user(email) or db.User()
        user.email = email
        user.name = name
        self.session.merge(user)
        self.session.commit()

    @mem_cache(expire=60*60)
    def get_name(self, email):
        user = self.get_user(email)
        if user:
            return user.name
        return None

    @mem_cache(expire=30*60)
    def get_group(self, email):
        user = self.get_user(email)
        if user:
            return user.group
        return None

    @mem_cache(expire=30*60)
    def get_permission(self, email):
        user = self.get_user(email)
        if user:
            return user.permission
        return None

    def permission_check(self, email, permission):
        pass
