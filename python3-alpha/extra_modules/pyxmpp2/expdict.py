#
# (C) Copyright 2003-2011 Jacek Konieczny <jajcus@jajcus.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License Version
# 2.1 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

"""Dictionary with item expiration."""



__docformat__ = "restructuredtext en"

import time
import threading
import logging

logger = logging.getLogger("pyxmpp2.expdict")

_NO_DEFAULT = object()

class ExpiringDictionary(dict):
    """An extension to standard Python dictionary objects which implements item
    expiration.

    Each item in ExpiringDictionary has its expiration time assigned, after
    which the item is removed from the mapping.

    :Ivariables:
        - `_timeouts`: a dictionary with timeout values and timeout callback for
          stored objects.
        - `_default_timeout`: the default timeout value (in seconds from now).
        - `_lock`: access synchronization lock.
    :Types:
        - `_timeouts`: `dict`
        - `_default_timeout`: `float`
        - `_lock`: :std:`threading.RLock`"""
    __slots__ = ['_timeouts', '_default_timeout', '_lock']
    def __init__(self, default_timeout = 300.0):
        """Initialize an `ExpiringDictionary` object.

        :Parameters:
            - `default_timeout`: default timeout value (in seconds) for stored
              objects.
        :Types:
            - `default_timeout`: `float`
        """
        dict.__init__(self)
        self._timeouts = {}
        self._default_timeout = default_timeout
        self._lock = threading.RLock()

    def __delitem__(self, key):
        with self._lock:
            logger.debug("expdict.__delitem__({0!r})".format(key))
            del self._timeouts[key]
            return dict.__delitem__(self, key)

    def __getitem__(self, key):
        with self._lock:
            logger.debug("expdict.__getitem__({0!r})".format(key))
            self._expire_item(key)
            return dict.__getitem__(self, key)

    def pop(self, key, default = _NO_DEFAULT):
        with self._lock:
            self._expire_item(key)
            del self._timeouts[key]
            if default is not _NO_DEFAULT:
                return dict.pop(self, key, default)
            else:
                return dict.pop(self, key)

    def __setitem__(self, key, value):
        logger.debug("expdict.__setitem__({0!r}, {1!r})".format(key, value))
        return self.set_item(key, value)

    def set_item(self, key, value, timeout = None, timeout_callback = None):
        """Set item of the dictionary.

        :Parameters:
            - `key`: the key.
            - `value`: the object to store.
            - `timeout`: timeout value for the object (in seconds from now).
            - `timeout_callback`: function to be called when the item expires.
              The callback should accept none, one (the key) or two (the key
              and the value) arguments.
        :Types:
            - `key`: any hashable value
            - `value`: any python object
            - `timeout`: `int`
            - `timeout_callback`: callable
        """
        with self._lock:
            logger.debug("expdict.__setitem__({0!r}, {1!r}, {2!r}, {3!r})"
                            .format(key, value, timeout, timeout_callback))
            if not timeout:
                timeout = self._default_timeout
            self._timeouts[key] = (time.time() + timeout, timeout_callback)
            return dict.__setitem__(self, key, value)

    def expire(self):
        """Do the expiration of dictionary items.

        Remove items that expired by now from the dictionary.

        :Return: time, in seconds, when the next item expires or `None`
        :returntype: `float`
        """
        with self._lock:
            logger.debug("expdict.expire. timeouts: {0!r}"
                                                    .format(self._timeouts))
            next_timeout = None
            for k in list(self._timeouts.keys()):
                ret = self._expire_item(k)
                if ret is not None:
                    if next_timeout is None:
                        next_timeout = ret
                    else:
                        next_timeout = min(next_timeout, ret)
            return next_timeout

    def clear(self):
        with self._lock:
            self._timeouts.clear()
            dict.clear(self)

    def _expire_item(self, key):
        """Do the expiration of a dictionary item.

        Remove the item if it has expired by now.

        :Parameters:
            - `key`: key to the object.
        :Types:
            - `key`: any hashable value
        """
        (timeout, callback) = self._timeouts[key]
        now = time.time()
        if timeout <= now:
            item = dict.pop(self, key)
            del self._timeouts[key]
            if callback:
                try:
                    callback(key, item)
                except TypeError:
                    try:
                        callback(key)
                    except TypeError:
                        callback()
            return None
        else:
            return timeout - now

# vi: sts=4 et sw=4
