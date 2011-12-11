# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
from flexget.plugin import register_plugin, PluginError
from flexget import validator
from lixian_api import LiXianAPI

log = logging.getLogger("transmission")

class PluginXunleiLixian(object):
    def __init__(self):
        self.xunlei_client_cache = dict()

    def gen_cache_key(self, config):
        return "username:%(username)s\npassword:%(password)s" % config

    def create_xunlei_client(self, config):
        client = LiXianAPI()
        if client.login(config['username'], config['password']):
            self.xunlei_client_cache[self.gen_cache_key(config)] = client
        else:
            raise PluginError("Cannot login to lixian.xunlei.com. Please check you username and password")
        return client

    def get_xunlei_client(self, config):
        cache_key = self.gen_cache_key(config)
        if cache_key in self.xunlei_client_cache:
            return self.xunlei_client_cache[cache_key]
        else:
            return self.create_xunlei_client(config)

    def validator(self):
        root = validator.factory()
        advanced = root.accept("dict")
        advanced.accept("text", key="username")
        advanced.accept("text", key="password")
        return root

    def prepare_config(self, config):
        if "username" not in config:
            raise PluginError("username is expected in PluginXunleiLixian")
        if "password" not in config:
            raise PluginError("password is expected in PluginXunleiLixian")
        return config

    def on_pocess_end(self, feed, config):
        for key, client in self.xunlei_client_cache.iteritem():
            client.logout()

    def on_feed_download(self, feed, config):
        if not feed.manager.options.test:
            client = self.get_xunlei_client(config)
        for entry in feed.accepted:
            if feed.manager.options.test:
                log.info("Would add %s to lixian.xunlei.com" % entry['url'])
                continue
            if not client.add(entry['url'], entry['title']):
                feed.fail(entry, "Add task error")
            else:
                log.info('"%s" added to lixian.xunlei.com' % entry['title'])

register_plugin(PluginXunleiLixian, "xunlei_lixian", api_ver=2)
