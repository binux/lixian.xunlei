# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>


from tornado.gen import coroutine
from tornado.web import HTTPError, asynchronous
from tornado.auth import GoogleOAuth2Mixin
from tornado.options import options
from .base import BaseHandler

class LoginHandler(BaseHandler, GoogleOAuth2Mixin):
    @coroutine
    def get(self):
        if self.get_argument('code', False):
            user = yield self.get_authenticated_user(
                redirect_uri='http://%s/auth/google' % self.request.host,
                code=self.get_argument('code'))
            self._on_auth(user)
            return

        if self.get_argument("logout", None):
            self.clear_cookie("name")
            self.clear_cookie("email")
            self.redirect("/")
            return
        reg_key = self.get_argument("key", None)
        if reg_key:
            self.set_secure_cookie("reg_key", reg_key, expires_days=1)
        yield self.authorize_redirect(
            redirect_uri='http://%s/login' % self.request.host,
            client_id=self.settings['google_oauth']['key'],
            scope=['profile', 'email'],
            response_type='code',
            extra_params={'approval_prompt': 'auto'})

    def _on_auth(self, user):
        import logging
        if not user:
            raise HTTPError(500, "Google auth failed.")
        if "zh" in user.get("locale", ""):
            chinese = False
            for word in user.get("name", ""):
                if ord(word) > 128:
                    chinese = True
                    break
            if chinese:
                user["name"] = user.get("last_name", "")+user.get("first_name", "")
        if options.reg_key:
            _user = self.user_manager.get_user(user["email"])
            reg_key = self.get_secure_cookie("reg_key", max_age_days=1)
            if not _user and reg_key != options.reg_key:
                self.set_status(403)
                self.write("Registry is Disabled by Administrator.")
                self.finish()
                return
        self.user_manager.update_user(user["email"], user["name"])
        self.set_secure_cookie("name", user["name"])
        self.set_secure_cookie("email", user["email"])
        self.redirect("/")

handlers = [
        (r"/login", LoginHandler),
]
ui_modules = {
}
