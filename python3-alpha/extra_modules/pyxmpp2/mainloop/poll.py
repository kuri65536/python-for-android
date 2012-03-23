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

import logging
import select

from .interfaces import HandlerReady, PrepareAgain
from .base import MainLoopBase

logger = logging.getLogger("pyxmpp2.mainloop.poll")

class PollMainLoop(MainLoopBase):
    """Main event loop based on the poll() syscall."""
    def __init__(self, settings = None, handlers = None):
        self._handlers = {}
        self._unprepared_handlers = {}
        self.poll = select.poll()
        self._timeout = None
        MainLoopBase.__init__(self, settings, handlers)

    def _add_io_handler(self, handler):
        """Add an I/O handler to the loop."""
        self._unprepared_handlers[handler] = None
        self._configure_io_handler(handler)

    def _configure_io_handler(self, handler):
        """Register an io-handler at the polling object."""
        if self.check_events():
            return
        if handler in self._unprepared_handlers:
            old_fileno = self._unprepared_handlers[handler]
            prepared = self._prepare_io_handler(handler)
        else:
            old_fileno = None
            prepared = True
        fileno = handler.fileno()
        if old_fileno is not None and fileno != old_fileno:
            del self._handlers[old_fileno]
            self.poll.unregister(old_fileno)
        if not prepared:
            self._unprepared_handlers[handler] = fileno
        if not fileno:
            return
        self._handlers[fileno] = handler
        events = 0
        if handler.is_readable():
            logger.debug(" {0!r} readable".format(handler))
            events |= select.POLLIN
        if handler.is_writable():
            logger.debug(" {0!r} writable".format(handler))
            events |= select.POLLOUT
        if events:
            logger.debug(" registering {0!r} handler fileno {1} for"
                            " events {2}".format(handler, fileno, events))
            self.poll.register(fileno, events)

    def _prepare_io_handler(self, handler):
        """Call the `interfaces.IOHandler.prepare` method and
        remove the handler from unprepared handler list when done.
        """
        logger.debug(" preparing handler: {0!r}".format(handler))
        ret = handler.prepare()
        logger.debug("   prepare result: {0!r}".format(ret))
        if isinstance(ret, HandlerReady):
            del self._unprepared_handlers[handler]
            prepared = True
        elif isinstance(ret, PrepareAgain):
            if ret.timeout is not None:
                if self._timeout is not None:
                    self._timeout = min(self._timeout, ret.timeout)
                else:
                    self._timeout = ret.timeout
            prepared = False
        else:
            raise TypeError("Unexpected result type from prepare()")
        return prepared

    def _remove_io_handler(self, handler):
        """Remove an i/o-handler."""
        if handler in self._unprepared_handlers:
            old_fileno = self._unprepared_handlers[handler]
            del self._unprepared_handlers[handler]
        else:
            old_fileno = handler.fileno()
        if old_fileno is not None:
            try:
                del self._handlers[old_fileno]
                self.poll.unregister(old_fileno)
            except KeyError:
                pass

    def loop_iteration(self, timeout = 60):
        """A loop iteration - check any scheduled events
        and I/O available and run the handlers.
        """
        next_timeout, sources_handled = self._call_timeout_handlers()
        if self._quit:
            return sources_handled
        if self._timeout is not None:
            timeout = min(timeout, self._timeout)
        if next_timeout is not None:
            timeout = min(next_timeout, timeout)
        for handler in list(self._unprepared_handlers):
            self._configure_io_handler(handler)
        events = self.poll.poll(timeout)
        self._timeout = None
        for (fileno, event) in events:
            if event & select.POLLHUP:
                self._handlers[fileno].handle_hup()
            if event & select.POLLNVAL:
                self._handlers[fileno].handle_nval()
            if event & select.POLLIN:
                self._handlers[fileno].handle_read()
            elif event & select.POLLERR:
                # if POLLIN was set this condition should be already handled
                self._handlers[fileno].handle_err()
            if event & select.POLLOUT:
                self._handlers[fileno].handle_write()
            sources_handled += 1
            self._configure_io_handler(self._handlers[fileno])
        return sources_handled
