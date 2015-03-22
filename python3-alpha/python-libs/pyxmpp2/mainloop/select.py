#
# (C) Copyright 2011 Jacek Konieczny <jajcus@jajcus.net>
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

"""I/O Handling classes

This module has a purpose similar to :std:`asyncore` from the base library, but
should be more usable, especially for PyXMPP.

Also, these interfaces should allow building application not only in
asynchronous event loop model, but also threaded model.
"""



__docformat__ = "restructuredtext en"

import time
import select
import logging

from .interfaces import HandlerReady, PrepareAgain
from .base import MainLoopBase

logger = logging.getLogger("pyxmpp2.mainloop.select")

class SelectMainLoop(MainLoopBase):
    """Main event loop implementation based on the `select.select()` call."""
    def __init__(self, settings = None, handlers = None):
        self._handlers = []
        self._prepared = set()
        MainLoopBase.__init__(self, settings, handlers)

    def _add_io_handler(self, handler):
        """Add an I/O handler to the loop."""
        self._handlers.append(handler)

    def _remove_io_handler(self, handler):
        self._handlers.remove(handler)

    def loop_iteration(self, timeout = 60):
        """A loop iteration - check any scheduled events
        and I/O available and run the handlers.
        """
        if self.check_events():
            return 0
        next_timeout, sources_handled = self._call_timeout_handlers()
        if self._quit:
            return sources_handled
        if next_timeout is not None:
            timeout = min(next_timeout, timeout)
        readable, writable, next_timeout = self._prepare_handlers()
        if next_timeout is not None:
            timeout = min(next_timeout, timeout)
        if not readable and not writable:
            readable, writable, _unused = [], [], None
            time.sleep(timeout)
        else:
            logger.debug("select({0!r}, {1!r}, [], {2!r})"
                                    .format( readable, writable,timeout))
            readable, writable, _unused = select.select(
                                            readable, writable, [], timeout)
        for handler in readable:
            handler.handle_read()
            sources_handled += 1
        for handler in writable:
            handler.handle_write()
            sources_handled += 1
        return sources_handled

    def _prepare_handlers(self):
        """Prepare the I/O handlers.

        :Return: (readable, writable, timeout) tuple. 'readable' is the list
            of readable handlers, 'writable' - the list of writable handlers,
            'timeout' the suggested maximum timeout for this loop iteration or
            `None`
        """
        timeout = None
        readable = []
        writable = []
        for handler in self._handlers:
            if handler not in self._prepared:
                logger.debug(" preparing handler: {0!r}".format(handler))
                ret = handler.prepare()
                logger.debug("   prepare result: {0!r}".format(ret))
                if isinstance(ret, HandlerReady):
                    self._prepared.add(handler)
                elif isinstance(ret, PrepareAgain):
                    if ret.timeout is not None:
                        if timeout is None:
                            timeout = ret.timeout
                        else:
                            timeout = min(timeout, ret.timeout)
                else:
                    raise TypeError("Unexpected result type from prepare()")
            if not handler.fileno():
                logger.debug(" {0!r}: no fileno".format(handler))
                continue
            if handler.is_readable():
                logger.debug(" {0!r} readable".format(handler))
                readable.append(handler)
            if handler.is_writable():
                logger.debug(" {0!r} writable".format(handler))
                writable.append(handler)
        return readable, writable, timeout

