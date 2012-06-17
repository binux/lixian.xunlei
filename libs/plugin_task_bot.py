# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
import requests
import HTMLParser
from flexget.plugin import register_plugin, PluginError
from flexget import validator

log = logging.getLogger("task_bot")
unescape = HTMLParser.HTMLParser().unescape

class PluginTaskBot(object):
    def __init__(self):
        pass

    def validator(self):
        root = validator.factory()
        advanced = root.accept("dict")
        advanced.accept("text", key="host")
        advanced.accept("text", key="tags")
        return root

    def prepare_config(self, config):
        if "host" not in config:
            config['host'] = "localhost:8880"
        if "tags" not in config:
            config['tags'] = ""
        return config

    def on_feed_output(self, feed, config):
        for entry in feed.accepted:
            if feed.manager.options.test:
                log.info("Would add %s to %s" % (entry['url'], config['host']))
                continue
            data = dict(
                    url = entry['url'],
                    title = unescape(entry['title']),
                    tags = config['tags'],
                    _xsrf = "1234567890"
                    )
            try:
                r = requests.post(config['host'], data=data, cookies={"_xsrf": "1234567890"})
            except Exception, e:
                feed.fail(entry, "Add task error: %s" % e)
                return
            log.info('"%s" added to %s' % (entry['title'], config['host']))

register_plugin(PluginTaskBot, "task_bot", api_ver=2)
