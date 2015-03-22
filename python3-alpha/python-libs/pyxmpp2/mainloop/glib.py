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

"""GLib main loop integration.
"""



__docformat__ = "restructuredtext en"

import inspect
import sys
import logging
import glib
import functools

from .interfaces import HandlerReady, PrepareAgain
from .base import MainLoopBase

logger = logging.getLogger("pyxmpp2.mainloop.glib")

def hold_exception(method):
    """Decorator for glib callback methods of GLibMainLoop used to store the
    exception raised."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper for methods decorated with `hold_exception`."""
        # pylint: disable=W0703
        try:
            return method(self, *args, **kwargs)
        except Exception:
            if self.exc_info:
                raise
            if not self._stack:
                logger.debug('@hold_exception wrapped method {0!r} called'
                            ' from outside of the main loop'.format(method))
                raise
            self.exc_info = sys.exc_info()
            logger.debug("exception in glib main loop callback:",
                                                exc_info = self.exc_info)
            # pylint: disable=W0212
            main_loop = self._stack[-1]
            if main_loop is not None:
                main_loop.quit()
            return False
    return wrapper

class GLibMainLoop(MainLoopBase):
    """Wrapper for the GLib main event loop.
    """
    # pylint: disable=R0902
    def __init__(self, settings = None, handlers = None):
        self._unprepared_handlers = {}
        self._io_sources = {}
        self._timer_sources = {}
        self._prepare_sources = {}
        self._stack = []
        self.exc_info = None
        self._anything_done = False
        self._unprepared_pending = set()
        MainLoopBase.__init__(self, settings, handlers)

    def __del__(self):
        for tag in list(self._prepare_sources.values()):
            glib.source_remove(tag)
        for tag in list(self._io_sources.values()):
            glib.source_remove(tag)
        for tag in list(self._timer_sources.values()):
            glib.source_remove(tag)

    def _add_io_handler(self, handler):
        """Add an I/O handler to the loop."""
        self._unprepared_handlers[handler] = None
        self._configure_io_handler(handler)

    def _configure_io_handler(self, handler):
        """Register an io-handler with the glib main loop."""
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
            tag = self._io_sources.pop(handler, None)
            if tag is not None:
                glib.source_remove(tag)
        if not prepared:
            self._unprepared_handlers[handler] = fileno
        if fileno is None:
            logger.debug(" {0!r}.fileno() is None, not polling"
                                                    .format(handler))
            return
        events = 0
        if handler.is_readable():
            logger.debug(" {0!r} readable".format(handler))
            events |= glib.IO_IN | glib.IO_ERR
        if handler.is_writable():
            logger.debug(" {0!r} writable".format(handler))
            events |= glib.IO_OUT | glib.IO_HUP | glib.IO_ERR
        if events:
            logger.debug(" registering {0!r} handler fileno {1} for"
                            " events {2}".format(handler, fileno, events))
            glib.io_add_watch(fileno, events, self._io_callback, handler)

    @hold_exception
    def _io_callback(self, fileno, condition, handler):
        """Called by glib on I/O event."""
        # pylint: disable=W0613
        self._anything_done = True
        logger.debug("_io_callback called for {0!r}, cond: {1}".format(handler,
                                                                    condition))
        try:
            if condition & glib.IO_HUP:
                handler.handle_hup()
            if condition & glib.IO_IN:
                handler.handle_read()
            elif condition & glib.IO_ERR:
                handler.handle_err()
            if condition & glib.IO_OUT:
                handler.handle_write()
            if self.check_events():
                return False
        finally:
            self._io_sources.pop(handler, None)
            self._configure_io_handler(handler)
            self._prepare_pending()
        return False

    def _prepare_io_handler(self, handler):
        """Call the `interfaces.IOHandler.prepare` method and
        remove the handler from unprepared handler list when done.
        """
        logger.debug(" preparing handler: {0!r}".format(handler))
        self._unprepared_pending.discard(handler)
        ret = handler.prepare()
        logger.debug("   prepare result: {0!r}".format(ret))
        if isinstance(ret, HandlerReady):
            del self._unprepared_handlers[handler]
            prepared = True
        elif isinstance(ret, PrepareAgain):
            if ret.timeout == 0:
                tag = glib.idle_add(self._prepare_io_handler_cb, handler)
                self._prepare_sources[handler] = tag
            elif ret.timeout is not None:
                timeout = ret.timeout
                timeout = int(timeout * 1000)
                if not timeout:
                    timeout = 1
                tag = glib.timeout_add(timeout, self._prepare_io_handler_cb,
                                                                    handler)
                self._prepare_sources[handler] = tag
            else:
                self._unprepared_pending.add(handler)
            prepared = False
        else:
            raise TypeError("Unexpected result type from prepare()")
        return prepared

    def _prepare_pending(self):
        """Prepare pending handlers.
        """
        if not self._unprepared_pending:
            return
        for handler in list(self._unprepared_pending):
            self._configure_io_handler(handler)
        self.check_events()

    @hold_exception
    def _prepare_io_handler_cb(self, handler):
        """Timeout callback called to try prepare an IOHandler again."""
        self._anything_done = True
        logger.debug("_prepar_io_handler_cb called for {0!r}".format(handler))
        self._configure_io_handler(handler)
        self._prepare_sources.pop(handler, None)
        return False

    def _remove_io_handler(self, handler):
        """Remove an i/o-handler."""
        if handler in self._unprepared_handlers:
            del self._unprepared_handlers[handler]
        tag = self._prepare_sources.pop(handler, None)
        if tag is not None:
            glib.source_remove(tag)
        tag = self._io_sources.pop(handler, None)
        if tag is not None:
            glib.source_remove(tag)

    def _add_timeout_handler(self, handler):
        """Add a `TimeoutHandler` to the main loop."""
        # pylint: disable=W0212
        for dummy, method in inspect.getmembers(handler, callable):
            if not hasattr(method, "_pyxmpp_timeout"):
                continue
            tag = glib.timeout_add(int(method._pyxmpp_timeout * 1000), 
                                                self._timeout_cb, method)
            self._timer_sources[method] = tag

    def _remove_timeout_handler(self, handler):
        """Remove `TimeoutHandler` from the main loop."""
        for dummy, method in inspect.getmembers(handler, callable):
            if not hasattr(method, "_pyxmpp_timeout"):
                continue
            tag = self._timer_sources.pop(method, None)
            if tag is not None:
                glib.source_remove(tag)
    
    @hold_exception
    def _timeout_cb(self, method):
        """Call the timeout handler due.
        """
        self._anything_done = True
        logger.debug("_timeout_cb() called for: {0!r}".format(method))
        result = method()
        # pylint: disable=W0212
        rec = method._pyxmpp_recurring
        if rec:
            self._prepare_pending()
            return True

        if rec is None and result is not None:
            logger.debug(" auto-recurring, restarting in {0} s"
                                                            .format(result))
            tag = glib.timeout_add(int(result * 1000), self._timeout_cb, method)
            self._timer_sources[method] = tag
        else:
            self._timer_sources.pop(method, None)
        self._prepare_pending()
        return False

    def loop(self, timeout = None):
        main_loop = glib.MainLoop()
        self._stack.append(main_loop)
        try:
            self._prepare_pending()
            if timeout is None:
                logger.debug("Calling main_loop.run()")
                main_loop.run()
                logger.debug("..main_loop.run() exited")
            else:
                tag = glib.timeout_add(int(timeout * 1000), 
                                            self._loop_timeout_cb, main_loop)
                try:
                    logger.debug("Calling main_loop.run()")
                    main_loop.run()
                    logger.debug("..main_loop.run() exited")
                finally:
                    glib.source_remove(tag)
        finally:
            self._stack.pop()
        if self.exc_info:
            (exc_type, exc_value, ext_stack), self.exc_info = (self.exc_info,
                                                                        None)
            raise exc_type(exc_value).with_traceback(ext_stack)
    
    def loop_iteration(self, timeout = 1):
        self._stack.append(None)
        try:
            if self.check_events():
                return
            self._prepare_pending()
            def dummy_cb():
                "Dummy callback function to force event if none are pending."
                self._anything_done = True
                logger.debug("Dummy timeout func called")
                return False
            if not glib.main_context_default().pending():
                glib.timeout_add(int(timeout * 1000), dummy_cb)
            self._anything_done = False
            logger.debug("Calling main_context_default().iteration()")
            while not self._anything_done:
                glib.main_context_default().iteration(True)
            logger.debug("..main_context_default().iteration() exited")
        finally:
            self._stack.pop()
        if self.exc_info:
            (exc_type, exc_value, ext_stack), self.exc_info = (self.exc_info,
                                                                        None)
            raise exc_type(exc_value).with_traceback(ext_stack)

    def _loop_timeout_cb(self, main_loop):
        """Stops the loop after the time specified in the `loop` call.
        """
        self._anything_done = True
        logger.debug("_loop_timeout_cb() called")
        main_loop.quit()

    def check_events(self):
        result = MainLoopBase.check_events(self)
        if result:
            main_loop = self._stack[-1]
            if main_loop:
                main_loop.quit()
        return result

