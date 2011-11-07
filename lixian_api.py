#/bin/usr/env python
#encoding: utf8
#author: binux<17175297.hk@gmail.com>

import re
import time
import json
import urllib
import requests
from hashlib import md5
from random import random
from BeautifulSoup import BeautifulSoup
from jsfunctionParser import parser_js_function_call

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
    def bt_task_check(self, url):
        r = self.session.get(self.QUERY_URL % {"url": urllib.quote_plus(url),
                              "random": self._random,
                              "cachetime": self._now})
        if r.error:
            r.raise_for_status()
        #queryUrl(flag,infohash,fsize,bt_title,is_full,subtitle,subformatsize,size_list,valid_list,file_icon,findex,random)
        function, args = parser_js_function_call(r.content)
        if len(args) < 12: return {}
        return dict(
                flag = args[0],
                infohash = args[1],
                fsize = args[2],
                bt_title = args[3],
                is_full = args[4],
                subtitle = args[5],
                subformatsize = args[6],
                size_list = args[7],
                valid_list = args[8],
                file_icon = args[9],
                findex = args[10],
                random = args[11])

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

    TASK_CHECK_URL = "http://dynamic.cloud.vip.xunlei.com/interface/task_check?callback=queryCid&url=%(url)s&random=%(random)s&tcache=%(cachetime)d"
    def task_check(self, url):
        r = self.session.get(self.TASK_CHECK_URL % {
                                   "url": urllib.quote_plus(url),
                                   "random": self._random,
                                   "cachetime": self._now})
        if r.error:
            r.raise_for_status()
        #queryCid(cid,gcid,file_size,tname,goldbean_need,silverbean_need,is_full,random)
        function, args = parser_js_function_call(r.content)
        if len(args) < 8: return {}
        return dict(
            cid = args[0],
            gcid = args[1],
            file_size = args[2],
            tname = args[3],
            goldbean_need = args[4],
            silverbean_need = args[5],
            is_full = args[6],
            random = args[7])

    TASK_COMMIT_URL = "http://dynamic.cloud.vip.xunlei.com/interface/task_commit?callback=ret_task&uid=%(uid)s&cid=%(cid)s&gcid=%(gcid)s&size=%(file_size)s&goldbean=%(goldbean_need)s&silverbean=%(silverbean_need)s&t=%(tname)s&url=%(url)s&type=%(type)s&o_page=task&o_taskid=0"
    def add_task(self, url):
        #TODO
        pass

    BATCH_TASK_CHECK_URL = "http://dynamic.cloud.vip.xunlei.com/interface/batch_task_check"
    def batch_task_check(self, url_list):
        data = dict(url="\r\n".join(url_list), random=self._random)
        r = self.session.post(self.BATCH_TASK_CHECK_URL, data=data)
        if r.error:
            r.raise_for_status()
        m = re.search("""parent.begin_task_batch_resp\((\[{.*?}\])\s*,\s*'\d+\.\d+\'\)""",
                      r.content)
        if not m:
            raise Exception, "batch task check data error: %r" % r.content
        json_data = json.loads(m.group(1))
        return json_data

    BATCH_TASK_COMMIT_URL = "http://dynamic.cloud.vip.xunlei.com/interface/batch_task_commit"
    def add_batch_task(self, url_list):
        json_data = self.batch_task_check(url_list)
        data = dict()
        for i, task in enumerate(json_data):
            if not "url" in task: continue
            data["cid[%d]" % i] = task.get("cid", "")
            data["url[%d]" % i] = task["url"]
        r = self.session.post(self.BATCH_TASK_COMMIT_URL, data)
        if r.error:
            r.raise_for_status()
        if "top.location" in r.content:
            return True

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
