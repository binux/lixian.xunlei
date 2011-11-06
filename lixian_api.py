#/bin/usr/env python
#encoding: utf8
#author: binux<17175297.hk@gmail.com>

import time
import urllib
import requests
from BeautifulSoup import BeautifulSoup
from hashlib import md5

def hex_md5(string):
    return md5(string).hexdigest()

class LiXianAPIException(Exception):
    pass

class NotLogin(LiXianAPIException):
    pass

class HTTPFetchError(LiXianAPIException):
    pass

class LiXianAPI(object):
    DEFAULT_USER_AGENT = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.106 Safari/535.2'
    DEFAULT_REFERER = 'http://lixian.vip.xunlei.com/'
    def __init__(self, user_agent = DEFAULT_USER_AGENT, referer = DEFAULT_REFERER):
        self.session = requests.session()
        self.session.headers['User-Agent'] = user_agent
        self.session.headers['Referer'] = referer

        self.islogin = False
        self._task_url = None
        self.uid = 0
        self.username = ""

    LOGIN_URL = 'http://login.xunlei.com/sec2login/'
    def login(self, username, password):

        self.username = username
        verifycode = self._get_verifycode(username)
        login_data = dict(
                u = username,
                p = hex_md5(hex_md5(hex_md5(password))+verifycode.upper()),
                verifycode = verifycode,
                login_enable = 1,
                login_hour = 720)
        r = self.session.post(self.LOGIN_URL, login_data)
        if r.error:
            r.raise_for_status()

        if r.cookies.get('logintype', '0') == '1':
            self.islogin = True
            return True
        else:
            self.islogin = False
            return False

    @property
    def _now(self):
        return int(time.time()*1000)

    @property
    def _random(self):
        return str(self._now)+str(random()*(2000000-10)+10)

    CHECK_URL = 'http://login.xunlei.com/check?u=%(username)s&cachetime=%(cachetime)d'
    def _get_verifycode(self, username):
        if self.islogin:
            raise Exception, "should not get verifycode after logined!"

        r = self.session.get(self.CHECK_URL %
                {"username": username, "cachetime": self._now})
        if r.error:
            r.raise_for_status()

        verifycode_tmp = r.cookies['check_result'].split(":")
        if len(verifycode_tmp) != 2:
            raise Exception, "verifycode error: %s" % verifycode
        return verifycode_tmp[1]

    REDIRECT_URL = "http://dynamic.lixian.vip.xunlei.com/login"
    def _redirect_to_user_task(self):
        if not self.islogin: raise NotLogin
        r = self.session.get(self.REDIRECT_URL)
        if r.error:
            r.raise_for_status()
        return r.url

    def task_url(self):
        if self._task_url:
            return self._task_url
        self._task_url = self._redirect_to_user_task()
        url_query = urllib.splitquery(self._task_url)[1]
        for attr, value in map(urllib.splitvalue, url_query.split("&")):
            if attr == "userid":
                self.uid = int(value)
                break
        return self._task_url

    QUERY_URL = "http://dynamic.cloud.vip.xunlei.com/interface/url_query?callback=queryUrl&u=%(url)s&random=%(random)s&tcache=%(cachetime)d"
    def get_bt_info(self, url):
        self.get(self.QUERY_URL % {"url": urllib.quote_plus(url),
                              "random": self._random(),
                              "cachetime": self._now})
        if r.error:
            r.raise_for_status()
        return r #TODO

    BT_TASK_COMMIT_URL = "http://dynamic.cloud.vip.xunlei.com/interface/bt_task_commit"
    def add_bt_task(self):
        #createNewFormElement(f, "uid", $PU("userid"));
        #createNewFormElement(f, "btname", btname);
        #createNewFormElement(f, "cid", gCID);
        #createNewFormElement(f, "goldbean", gGoldBean);
        #createNewFormElement(f, "silverbean", gSilverBean);
        #createNewFormElement(f, "tsize", gBtSize);
        #createNewFormElement(f, "findex",index_list);
        #createNewFormElement(f, "size",size_list);
        #createNewFormElement(f, "name",gname.value); // title_list
        #createNewFormElement(f, "o_taskid",delete_id);
        #createNewFormElement(f, "o_page",G_PAGE);
        #createNewFormElement(f, "from","0");        
        # TODO
        pass

    def check_login(self):
        pass

    LOGOUT_URL = "http://login.xunlei.com/unregister?sessionid=%(sessionid)s"
    def logout(self):
        if not self.islogin: raise NotLogin
        cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        sessionid = cookies.get("sessionid", None)
        if sessionid:
            self.session.get(self.LOGOUT_URL % {"sessionid": sessionid})
        self.session.cookies.clear()
        self.islogin = False
        self._task_url = None
