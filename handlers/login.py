# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import HTTPError, asynchronous
from tornado.auth import GoogleMixin
from tornado.options import options
from .base import BaseHandler

class LoginHandler(BaseHandler, GoogleMixin):
    @asynchronous
    def get(self):
       if self.get_argument("openid.mode", None):
           self.get_authenticated_user(self.async_callback(self._on_auth))
           return
       if self.get_argument("logout", None):
           self.clear_cookie("name")
           self.clear_cookie("email")
           self.redirect("/")
           return
       self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            raise HTTPError(500, "Google auth failed")
        self.set_secure_cookie("name", user["name"])
        self.set_secure_cookie("email", user["email"])
        self.user_manager.update_user(user["email"], user["name"])
        self.redirect("/")

handlers = [
        (r"/login", LoginHandler),
]
ui_modules = {
}
