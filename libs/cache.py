# -*- coding: utf-8 -*-
#
# Copyright(c) 2010 poweredsites.org
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import hashlib
from time import time
from tornado.options import options

_mem_caches = {}

def mem_cache(expire=7200, key=""):
    """Mem cache to python dict by key"""
    def wrapper(func):
        def new_func(self, *args, **kwargs):
            now = time()
            if key:
                c = key
            else:
                c = self.__class__.__name__ + func.__name__ + repr(func)
            k = key_gen(self, c, *args, **kwargs)

            value = _mem_caches.get(k, None)
            if _valid_cache(value, now):
                return value["value"]
            else:
                val = func(self, *args, **kwargs)
                _mem_caches[k] = {"value":val, "expire":now+expire}

                return val

        if options.cache_enabled:
            return new_func
        else:
            return func
    return wrapper

def key_gen(self, key, *args, **kwargs):
    code = hashlib.md5()

    code.update(str(key))

    # copy args to avoid sort original args
    c = list(args[:])
    # sort c to avoid generate different key when args is the same
    # but sequence is different
    c.sort()
    c = [str(v) for v in c]
    code.update("".join(c))

    c = ["%s=%s" % (k, v) for k, v in kwargs]
    c.sort()
    code.update("".join(c))

    return code.hexdigest()

def _valid_cache(value, now):
    if value:
        if value["expire"] > now:
            return True
        else:
            return False
    else:
        return False
