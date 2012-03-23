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

"""Main loop implementation Base.
"""



__docformat__ = "restructuredtext en"

import time
import logging
import inspect

from .events import EventDispatcher
from .interfaces import EventHandler, IOHandler, TimeoutHandler, MainLoop, QUIT
from ..settings import XMPPSettings

logger = logging.getLogger("pyxmpp2.mainloop.base")

class MainLoopBase(MainLoop):
    """Base class for main loop implementations."""
    # pylint: disable-msg=W0223
    def __init__(self, settings = None, handlers = None):
        self.settings = settings if settings else XMPPSettings()
        if not handlers:
            handlers = []
        self._timeout_handlers = []
        self.event_dispatcher = EventDispatcher(self.settings, handlers)
        self.event_queue = self.settings["event_queue"]
        self._quit = False
        self._started = False
        for handler in handlers:
            self.add_handler(handler)

    def add_handler(self, handler):
        if isinstance(handler, IOHandler):
            self._add_io_handler(handler)
        if isinstance(handler, TimeoutHandler):
            self._add_timeout_handler(handler)
        if isinstance(handler, EventHandler):
            self.event_dispatcher.add_handler(handler)

    def remove_handler(self, handler):
        if isinstance(handler, IOHandler):
            self._remove_io_handler(handler)
        if isinstance(handler, TimeoutHandler):
            self._remove_timeout_handler(handler)
        if isinstance(handler, EventHandler):
            self.event_dispatcher.remove_handler(handler)

    def _add_io_handler(self, handler):
        """Add an `IOHandler` to the loop."""
        raise NotImplementedError

    def _remove_io_handler(self, handler):
        """Remove an `IOHandler` from the loop."""
        raise NotImplementedError

    @property
    def finished(self):
        return self._quit
    @property
    def started(self):
        return self._started
    def quit(self):
        self.event_queue.put(QUIT)
    def loop(self, timeout = None):
        interval = self.settings["poll_interval"]
        if timeout is None:
            while not self._quit:
                self.loop_iteration(interval)
        else:
            timeout = time.time() + timeout
            while not self._quit and time.time() < timeout:
                self.loop_iteration(interval)
    def loop_iteration(self, timeout = 1):
        if self.check_events():
            return
        time.sleep(timeout)
    def check_events(self):
        """Call the event dispatcher. 

        Quit the main loop when the `QUIT` event is reached.

        :Return: `True` if `QUIT` was reached.
        """
        if self.event_dispatcher.flush() is QUIT:
            self._quit = True
            return True
        return False

    def _add_timeout_handler(self, handler):
        """Add a `TimeoutHandler` to the main loop."""
        # pylint: disable-msg=W0212
        now = time.time()
        for dummy, method in inspect.getmembers(handler, callable):
            if not hasattr(method, "_pyxmpp_timeout"):
                continue
            self._timeout_handlers.append((now + method._pyxmpp_timeout,
                                                                    method))
        self._timeout_handlers.sort(key = lambda x: x[0])

    def _remove_timeout_handler(self, handler):
        """Remove `TimeoutHandler` from the main loop."""
        self._timeout_handlers = [(t, h) for (t, h) 
                                            in self._timeout_handlers
                                            if h.__self__ != handler]

    def _call_timeout_handlers(self):
        """Call the timeout handlers due.

        :Return: (next_event_timeout, sources_handled) tuple.
            next_event_timeout is number of seconds until the next timeout
            event, sources_handled is number of handlers called.
        """
        sources_handled = 0
        now = time.time()
        schedule = None
        while self._timeout_handlers:
            schedule, handler = self._timeout_handlers[0]
            if schedule <= now:
                # pylint: disable-msg=W0212
                logger.debug("About to call a timeout handler: {0!r}"
                                                        .format(handler))
                self._timeout_handlers = self._timeout_handlers[1:]
                result = handler()
                logger.debug(" handler result: {0!r}".format(result))
                rec = handler._pyxmpp_recurring
                if rec:
                    logger.debug(" recurring, restarting in {0} s"
                                        .format(handler._pyxmpp_timeout))
                    self._timeout_handlers.append(
                                    (now + handler._pyxmpp_timeout, handler))
                    self._timeout_handlers.sort(key = lambda x: x[0])
                elif rec is None and result is not None:
                    logger.debug(" auto-recurring, restarting in {0} s"
                                                            .format(result))
                    self._timeout_handlers.append((now + result, handler))
                    self._timeout_handlers.sort(key = lambda x: x[0])
                sources_handled += 1
            else:
                break
            if self.check_events():
                return 0, sources_handled
        if self._timeout_handlers and schedule:
            timeout = schedule - now
        else:
            timeout = None
        return timeout, sources_handled

