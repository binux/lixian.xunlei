# -*- encoding: utf8 -*-

import db
from db.util import *
from libs.cache import mem_cache

default_group_permission = {
        "add_task": True,
        "add_anonymous_task": True,
        "add_task_limit_size": 20,
        "add_task_limit": True,
        "mod_task": True,
        "view_tasklist": True,
        "view_invalid": False,
        "need_miaoxia": True,
        "admin": False,
}
not_login_permission = {
        "add_task": False,
        "add_anonymous_task": False,
        "add_task_limit_size": 0,
        "add_task_limit": True,
        "mod_task": False,
        "view_tasklist": True,
        "view_invalid": False,
        "need_miaoxia": True,
        "admin": False,
}
group_permission = {
        None: {
        },
        "": {
        },
        "user": {
        },
        "admin": {
            "add_task_limit": False,
            "view_invalid": True,
            "need_miaoxia": False,
            "admin": True,
        },
        "block": {
            "add_task": False,
            "add_anonymous_task": True,
            "add_task_limit_size": 10,
            "mod_task": False,
        },
}
permission_mark = {
        "add_task": 1,
        "add_anonymous_task": 2,
        "add_task_limit": 64,
        "mod_task": 4,
        "view_invalid": 8,
        "need_miaoxia": 16,
        "admin": 32,
        }

for group, permission_dict in group_permission.iteritems():
    tmp = dict(default_group_permission)
    tmp.update(permission_dict)
    group_permission[group] = tmp

class UserManager(object):
    def __init__(self):
        self.session = db.Session()
        self.add_task_limit_used = {}
        self.reload_limit = {}

    @sqlalchemy_rollback
    def get_user_by_id(self, _id):
        return self.session.query(db.User).get(_id)

    @sqlalchemy_rollback
    def get_user_email_by_id(self, _id):
        if _id == 0:
            return "bot@localhost"
        return self.session.query(db.User.email).filter(db.User.id==_id).scalar()

    @sqlalchemy_rollback
    def get_user(self, email):
        if not email: return None
        return self.session.query(db.User).filter(db.User.email==email).scalar()

    @sqlalchemy_rollback
    def update_user(self, email, name):
        self.reset_add_task_limit(email)
        user = self.get_user(email) or db.User()
        user.email = email
        user.name = name
        self.session.add(user)
        self.session.commit()

    @mem_cache(expire=60*60)
    def get_id(self, email):
        if email == "bot@localhost":
            return 0
        user = self.get_user(email)
        if user:
            return user.id
        return None

    @mem_cache(expire=60*60)
    def get_name(self, email):
        if email == "bot@localhost":
            return "bot"
        user = self.get_user(email)
        if user:
            return user.name
        return None

    @mem_cache(expire=30*60)
    def get_group(self, email):
        if email == "bot@localhost":
            return "admin"
        user = self.get_user(email)
        if user:
            return user.group
        return None

    def get_add_task_limit(self, email):
        if not self.check_permission(email, "add_task_limit"):
            return 1
        limit = group_permission.get(self.get_group(email), default_group_permission)["add_task_limit_size"]
        used = self.add_task_limit_used.get(email, 0)
        return limit - used

    def incr_add_task_limit(self, email):
        self.add_task_limit_used[email] = self.add_task_limit_used.setdefault(email, 0) + 1

    def reset_add_task_limit(self, email):
        if email in self.add_task_limit_used:
            if self.add_task_limit_used[email] > self.reload_limit.get(email, 0):
                self.reload_limit[email] = self.reload_limit.setdefault(email, 0) + 1
            self.add_task_limit_used[email] = self.reload_limit.get(email, 0)

    def reset_all_add_task_limit(self):
        self.add_task_limit_used = {}
        self.reload_limit = {}

    @mem_cache(expire=30*60)
    def get_permission(self, email):
        user = self.get_user(email)
        if user:
            return user.permission or 0
        return 0

    @mem_cache(expire=60)
    def check_permission(self, email, permission):
        if email is None:
            return not_login_permission[permission]
        return group_permission.get(self.get_group(email), default_group_permission)[permission] or (self.get_permission(email) & permission_mark[permission])
