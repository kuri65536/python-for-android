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
import threading
import logging
import sys
import queue
import inspect

from .interfaces import MainLoop, HandlerReady, PrepareAgain
from .interfaces import IOHandler, QUIT, EventHandler, TimeoutHandler
from .events import EventDispatcher
from ..settings import XMPPSettings
from .wait import wait_for_read, wait_for_write

logger = logging.getLogger("pyxmpp2.mainloop.threads")

class IOThread(object):
    """Base class for `ReadingThread` and `WrittingThread`.

    :Ivariables:
        - `name`: thread name (for debugging)
        - `io_handler`: the I/O handler object to poll
        - `thread`: the actual thread object
        - `exc_info`: this will hold exception information tuple for the
          last exception raised in the thread.
        - `exc_queue`: queue to put all exceptions raised in the thread.

    :Types:
        - `name`: `str`
        - `io_handler`: `IOHandler`
        - `thread`: :std:`threading.Thread`
        - `exc_info`: (type, value, traceback) tuple
    """
    def __init__(self, settings, io_handler, name, daemon = True,
                                                        exc_queue = None):
        # pylint: disable=R0913
        self.settings = settings if settings else XMPPSettings()
        self.name = name
        self.io_handler = io_handler
        self.thread = threading.Thread(name = name, target = self._run)
        self.thread.daemon = daemon
        self.exc_info = None
        self.exc_queue = exc_queue
        self._quit = False

    def start(self):
        """Start the thread.
        """
        self.thread.start()
    
    def is_alive(self):
        """Check if the thread is alive."""
        return self.thread.is_alive()

    def stop(self):
        """Request the thread to stop."""
        self._quit = True

    def join(self, timeout):
        """Join the thread (wait until it stops)."""
        return self.thread.join(timeout)

    def _run(self):
        """The thread function. Calls `self.run()` in loop and if it raises an
        exception, stores it in self.exc_queue. If `exc_queue` is None
        the exception will abort the thread.
        """
        logger.debug("{0}: entering thread".format(self.name))
        while True:
            try:
                self.run()
            except Exception: # pylint: disable-msg=W0703
                self.exc_info = sys.exc_info()
                logger.debug("exception in the {0!r} thread:"
                                .format(self.name), exc_info = self.exc_info)
                if self.exc_queue:
                    self.exc_queue.put( (self, self.exc_info) )
                    continue
                else:
                    logger.debug("{0}: aborting thread".format(self.name))
                    return
            except:
                logger.debug("{0}: aborting thread".format(self.name))
                return
            break
        logger.debug("{0}: exiting thread".format(self.name))

    def run(self):
        """The thread function."""
        raise NotImplementedError

class ReadingThread(IOThread):
    """A thread reading from io_handler.

    This thread will be also the one to call the `IOHandler.prepare` method
    until HandlerReady is returned.
    
    It can be used (together with `WrittingThread`) instead of 
    a main loop."""
    def __init__(self, settings, io_handler, name = None, daemon = True,
                                                            exc_queue = None):
        # pylint: disable=R0913
        if name is None:
            name = "{0!r} reader".format(io_handler)
        IOThread.__init__(self, settings, io_handler, name, daemon, exc_queue)

    def run(self):
        """The thread function.
        
        First, call the handler's 'prepare' method until it returns
        `HandlerReady` then loop waiting for the socket input and calling
        'handle_read' on the handler.
        """
        # pylint: disable-msg=R0912
        interval = self.settings["poll_interval"]
        prepared = False
        timeout = 0.1
        while not self._quit:
            if not prepared:
                logger.debug("{0}: preparing handler: {1!r}".format(
                                                   self.name, self.io_handler))
                ret = self.io_handler.prepare()
                logger.debug("{0}: prepare result: {1!r}".format(self.name,
                                                                        ret))
                if isinstance(ret, HandlerReady):
                    prepared = True
                elif isinstance(ret, PrepareAgain):
                    if ret.timeout is not None:
                        timeout = ret.timeout
                else:
                    raise TypeError("Unexpected result type from prepare()")
            if self.io_handler.is_readable():
                logger.debug("{0}: readable".format(self.name))
                fileno = self.io_handler.fileno()
                if fileno is not None:
                    readable = wait_for_read(fileno, interval)
                    if readable:
                        self.io_handler.handle_read()
            elif not prepared:
                if timeout:
                    time.sleep(timeout)
            else:
                logger.debug("{0}: waiting for readability".format(self.name))
                if not self.io_handler.wait_for_readability():
                    break

class WrittingThread(IOThread):
    """A thread reading from io_handler.
    
    It can be used (together with `WrittingThread`) instead of 
    a main loop."""
    def __init__(self, settings, io_handler, name = None, daemon = True,
                                                            exc_queue = None):
        # pylint: disable=R0913
        if name is None:
            name = "{0!r} writer".format(io_handler)
        IOThread.__init__(self, settings, io_handler, name, daemon, exc_queue)

    def run(self):
        """The thread function.
        
        Loop waiting for the handler and socket being writable and calling 
        `interfaces.IOHandler.handle_write`.
        """
        while not self._quit:
            interval = self.settings["poll_interval"]
            if self.io_handler.is_writable():
                logger.debug("{0}: writable".format(self.name))
                fileno = self.io_handler
                if fileno:
                    writable = wait_for_write(fileno, interval)
                    if writable:
                        self.io_handler.handle_write()
            else:
                logger.debug("{0}: waiting for writaility".format(self.name))
                if not self.io_handler.wait_for_writability():
                    break

class EventDispatcherThread(object):
    """Event dispatcher thread.
    
    :Ivariables:
        - `name`: thread name (for debugging)
        - `event_queue`: the event queue to poll
        - `thread`: the actual thread object
        - `exc_info`: this will hold exception information tuple whenever the
          thread was aborted by an exception.

    :Types:
        - `name`: `str`
        - `event_queue`: :std:`Queue.Queue`
        - `thread`: :std:`threading.Thread`
        - `exc_info`: (type, value, traceback) tuple
    """
    def __init__(self, event_dispatcher, name = None,
                                            daemon = True, exc_queue = None):
        if name is None:
            name = "event dispatcher"
        self.name = name
        self.thread = threading.Thread(name = name, target = self.run)
        self.thread.daemon = daemon
        self.exc_info = None
        self.exc_queue = exc_queue
        self.event_dispatcher = event_dispatcher

    def start(self):
        """Start the thread."""
        self.thread.start()

    def is_alive(self):
        """Check if the thread is alive."""
        return self.thread.is_alive()

    def join(self, timeout):
        """Join the thread."""
        return self.thread.join(timeout)

    def run(self):
        """The thread function. Calls `self.run()` and if it raises
        an exception, stores it in self.exc_info and exc_queue
        """
        logger.debug("{0}: entering thread".format(self.name))
        while True:
            try:
                self.event_dispatcher.loop()
            except Exception: # pylint: disable-msg=W0703
                self.exc_info = sys.exc_info()
                logger.debug("exception in the {0!r} thread:"
                                .format(self.name), exc_info = self.exc_info)
                if self.exc_queue:
                    self.exc_queue.put( (self, self.exc_info) )
                    continue
                else:
                    logger.debug("{0}: aborting thread".format(self.name))
                    return
            except:
                logger.debug("{0}: aborting thread".format(self.name))
                return
            break
        logger.debug("{0}: exiting thread".format(self.name))

class TimeoutThread(object):
    """Thread to handle `TimeoutHandler` methods.

    :Ivariables:
        - `method`: the timout handler method
        - `name`: thread name (for debugging)
        - `thread`: the actual thread object
        - `exc_info`: this will hold exception information tuple whenever the
          thread was aborted by an exception.
        - `exc_queue`: queue for raised exceptions

    :Types:
        - `name`: `str`
        - `method`: a bound method decorated with `interfaces.timeout_handler`
        - `thread`: :std:`threading.Thread`
        - `exc_info`: (type, value, traceback) tuple
        - `exc_queue`: queue for raised exceptions
    """
    def __init__(self, method, name = None, daemon = True, exc_queue = None):
        if name is None:
            name = "{0!r} timer thread"
        self.name = name
        self.method = method
        self.thread = threading.Thread(name = name, target = self._run)
        self.thread.daemon = daemon
        self.exc_info = None
        self.exc_queue = exc_queue
        self._quit = False

    def start(self):
        """Start the thread.
        """
        self.thread.start()
    
    def is_alive(self):
        """Check if the thread is alive."""
        return self.thread.is_alive()

    def stop(self):
        """Request the thread to stop."""
        self._quit = True

    def join(self, timeout):
        """Join the thread (wait until it stops)."""
        return self.thread.join(timeout)

    def _run(self):
        """The thread function. Calls `self.run()` and if it raises
        an exception, stores it in self.exc_info
        """
        logger.debug("{0}: entering thread".format(self.name))
        while True:
            try:
                self.run()
            except Exception: # pylint: disable-msg=W0703
                self.exc_info = sys.exc_info()
                logger.debug("exception in the {0!r} thread:"
                                .format(self.name), exc_info = self.exc_info)
                if self.exc_queue:
                    self.exc_queue.put( (self, self.exc_info) )
                    continue
                else:
                    logger.debug("{0}: aborting thread".format(self.name))
                    return
            except:
                logger.debug("{0}: aborting thread".format(self.name))
                return
            break
        logger.debug("{0}: exiting thread".format(self.name))

    def run(self):
        """The thread function."""
        # pylint: disable-msg=W0212
        timeout = self.method._pyxmpp_timeout
        recurring = self.method._pyxmpp_recurring
        while not self._quit and timeout is not None:
            if timeout:
                time.sleep(timeout)
            if self._quit:
                break
            ret = self.method()
            if recurring is None:
                timeout = ret
            elif not recurring:
                break

class ThreadPool(MainLoop):
    """Thread pool object, as a replacement for an asychronous event loop."""
    # pylint: disable-msg=R0902
    def __init__(self, settings = None, handlers = None):
        self.settings = settings if settings else XMPPSettings()
        self.io_handlers = []
        self.timeout_handlers = []
        self.event_queue = self.settings["event_queue"]
        self.event_dispatcher = EventDispatcher(self.settings, handlers)
        self.exc_queue = queue.Queue()
        self.io_threads = []
        self.timeout_threads = []
        self.event_thread = None
        self.daemon = False
        if handlers:
            for handler in handlers:
                self.add_handler(handler)

    def add_handler(self, handler):
        if isinstance(handler, IOHandler):
            self._add_io_handler(handler)
        if isinstance(handler, EventHandler):
            self.event_dispatcher.add_handler(handler)
        if isinstance(handler, TimeoutHandler):
            self._add_timeout_handler(handler)

    def remove_handler(self, handler):
        if isinstance(handler, IOHandler):
            self._remove_io_handler(handler)
        if isinstance(handler, EventHandler):
            self.event_dispatcher.remove_handler(handler)
        if isinstance(handler, TimeoutHandler):
            self._remove_timeout_handler(handler)

    def _add_io_handler(self, handler):
        """Add an IOHandler to the pool.
        """
        self.io_handlers.append(handler)
        if self.event_thread is None:
            return

    def _run_io_threads(self, handler):
        """Start threads for an IOHandler.
        """
        reader = ReadingThread(self.settings, handler, daemon = self.daemon,
                                                exc_queue = self.exc_queue)
        writter = WrittingThread(self.settings, handler, daemon = self.daemon,
                                                exc_queue = self.exc_queue)
        self.io_threads += [reader, writter]
        reader.start()
        writter.start()

    def _remove_io_handler(self, handler):
        """Remove an IOHandler from the pool.
        """
        if handler not in self.io_handlers:
            return
        self.io_handlers.remove(handler)
        for thread in self.io_threads:
            if thread.io_handler is handler:
                thread.stop()

    def _add_timeout_handler(self, handler):
        """Add a TimeoutHandler to the pool.
        """
        self.timeout_handlers.append(handler)
        if self.event_thread is None:
            return
        self._run_timeout_threads(handler)

    def _run_timeout_threads(self, handler):
        """Start threads for a TimeoutHandler.
        """
        # pylint: disable-msg=W0212
        for dummy, method in inspect.getmembers(handler, callable):
            if not hasattr(method, "_pyxmpp_timeout"):
                continue
            thread = TimeoutThread(method, daemon = self.daemon,
                                                    exc_queue = self.exc_queue)
            self.timeout_threads.append(thread)
            thread.start()

    def _remove_timeout_handler(self, handler):
        """Remove a TimeoutHandler from the pool.
        """
        if handler not in self.timeout_handlers:
            return
        self.io_handlers.remove(handler)
        for thread in self.timeout_threads:
            if thread.handler_method.__self__ is handler:
                thread.stop()

    def start(self, daemon = False):
        """Start the threads."""
        self.daemon = daemon
        self.io_threads = []
        self.event_thread = EventDispatcherThread(self.event_dispatcher,
                                    daemon = daemon, exc_queue = self.exc_queue)
        self.event_thread.start()
        for handler in self.io_handlers:
            self._run_io_threads(handler)
        for handler in self.timeout_handlers:
            self._run_timeout_threads(handler)

    def stop(self, join = False, timeout = None):
        """Stop the threads.

        :Parameters:
            - `join`: join the threads (wait until they exit)
            - `timeout`: maximum time (in seconds) to wait when `join` is
              `True`).  No limit when `timeout` is `None`.
        """
        logger.debug("Closing the io handlers...")
        for handler in self.io_handlers:
            handler.close()
        if self.event_thread.is_alive():
            logger.debug("Sending the QUIT signal")
            self.event_queue.put(QUIT)
        logger.debug("  sent")
        threads = self.io_threads + self.timeout_threads
        for thread in threads:
            logger.debug("Stopping thread: {0!r}".format(thread))
            thread.stop()
        if not join:
            return
        if self.event_thread:
            threads.append(self.event_thread)
        if timeout is None:
            for thread in threads:
                thread.join()
        else:
            timeout1 = (timeout * 0.01) / len(threads)
            threads_left = []
            for thread in threads:
                logger.debug("Quick-joining thread {0!r}...".format(thread))
                thread.join(timeout1)
                if thread.is_alive():
                    logger.debug("  thread still alive".format(thread))
                    threads_left.append(thread)
            if threads_left:
                timeout2 = (timeout * 0.99) / len(threads_left)
                for thread in threads_left:
                    logger.debug("Joining thread {0!r}...".format(thread))
                    thread.join(timeout2)
        self.io_threads = []
        self.event_thread = None

    @property
    def finished(self):
        return self.event_thread is None or not self.event_thread.is_alive()

    @property
    def started(self):
        return self.event_thread is not None
        
    def quit(self):
        self.event_queue.put(QUIT)

    def loop(self, timeout = None):
        if not self.event_thread:
            return
        interval = self.settings["poll_interval"]
        if timeout is None:
            while self.event_thread.is_alive():
                self.loop_iteration(interval)
        else:
            timeout = time.time() + timeout
            while self.event_thread.is_alive() and time.time() < timeout:
                self.loop_iteration(interval)

    def loop_iteration(self, timeout = 0.1):
        """Wait up to `timeout` seconds, raise any exception from the
        threads.
        """
        try:
            exc_info = self.exc_queue.get(True, timeout)[1]
        except queue.Empty:
            return
        exc_type, exc_value, ext_stack = exc_info
        raise exc_type(exc_value).with_traceback(ext_stack)

