# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
from flexget.plugin import register_plugin, PluginError
from flexget import validator
from flexget.entry import Entry
from lixian_api import LiXianAPI

log = logging.getLogger("transmission")

class XunleiLixianBase(object):
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

class PluginFromXunleiLixian(XunleiLixianBase):
    def validator(self):
        root = validator.factory()
        advanced = root.accept("dict")
        advanced.accept("text", key="username")
        advanced.accept("text", key="password")
        advanced.accept("integer", key="limit")
        advanced.accept("any", key="fields")
        return root

    def prepare_config(self, config):
        if "username" not in config:
            raise PluginError("username is expected in PluginXunleiLixian")
        if "password" not in config:
            raise PluginError("password is expected in PluginXunleiLixian")
        if "limit" not in config:
            config['limit'] = 30
        if "fields" not in config:
            config['fields'] = {}
        return config

    def on_feed_input(self, feed, config):
        entries = []
        client = self.get_xunlei_client(config)
        tasks = client.get_task_list(config['limit'], 2)
        for task in tasks:
            if task['status'] != "finished":
                continue
            elif task['lixian_url']:
                entry = Entry(title=task['taskname'],
                              url=task['lixian_url'],
                              cookie="gdriveid=%s;" % client.gdriveid,
                              taskname=".",
                              size=task['size'],
                              format=task['format'],
                              fields=config['fields'],
                              )
                entries.append(entry)
            elif task['task_type'] in ("bt", "magnet"):
                files = client.get_bt_list(task['task_id'], task['cid'])
                for file in files:
                    if not file['lixian_url']:
                        continue
                    entry = Entry(title=file['dirtitle'],
                                  url=file['lixian_url'],
                                  cookie="gdriveid=%s;" % client.gdriveid,
                                  taskname=task['taskname'],
                                  size=file['size'],
                                  format=file['format'],
                                  fields=config['fields'],
                                  )
                    entries.append(entry)
        return entries

class PluginXunleiLixian(XunleiLixianBase):
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

    def on_feed_output(self, feed, config):
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

register_plugin(PluginFromXunleiLixian, "from_xunlei_lixian", api_ver=2)
register_plugin(PluginXunleiLixian, "xunlei_lixian", api_ver=2)
