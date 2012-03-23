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

"""Abstract base classes for the main loop framework.

:Variables:
    - `QUIT`: event (instance of a QuitEvent class) used to terminate
      the main event loop.
"""
# pylint: disable=R0201



__docformat__ = "restructuredtext en"

from abc import ABCMeta, abstractmethod, abstractproperty

class IOHandlerPrepareResult(object):
    """Result of the `IOHandler.prepare` method."""
    # pylint: disable-msg=R0903,R0921,R0922
    pass

class HandlerReady(IOHandlerPrepareResult):
    """Returned by the `IOHandler.prepare` method
    when the object is ready to handle I/O events and doesn't need further
    calls to the `IOHandler.prepare` method.
    """
    # pylint: disable-msg=R0903
    def __repr__(self):
        return "HandlerReady()"

class PrepareAgain(IOHandlerPrepareResult):
    """Returned by the `IOHandler.prepare` method
    when the method needs to be called again.

    :Ivariables:
      - `timeout`: how long may the main loop wait before calling
        `IOHandler.prepare` again. `None` means wait until the next loop
        iteration whenever it happens, `0` - do not wait on I/O in this
        iteration.
    """
    # pylint: disable-msg=R0903
    def __init__(self, timeout = None):
        IOHandlerPrepareResult.__init__(self)
        self.timeout = timeout
    def __repr__(self):
        if self.timeout is not None:
            return "PrepareAgain({0!r})".format(self.timeout)
        else:
            return "PrepareAgain()"

class IOHandler(metaclass=ABCMeta):
    """Wrapper for a socket or a file descriptor to be used in event loop
    or for I/O threads."""

    @abstractmethod
    def fileno(self):
        """Return file descriptor to poll or select."""
        return None

    @abstractmethod
    def is_readable(self):
        """
        :Return: `True` when the I/O channel can be read
        """
        return False

    @abstractmethod
    def wait_for_readability(self):
        """
        Stop current thread until the channel is readable.

        :Return: `False` if it won't be readable (e.g. is closed)
        """
        return False

    @abstractmethod
    def is_writable(self):
        """
        :Return: `True` when the I/O channel can be written to
        """
        return False

    @abstractmethod
    def prepare(self):
        """
        Prepare the I/O handler for the event loop or an event loop 
        iteration. 

        :Return: `HandlerReady()` if there is no need to call `prepare` again
            or `PrepareAgain()` otherwise.
        :Returntype: `IOHandlerPrepareResult`
        """
        return HandlerReady()

    @abstractmethod
    def wait_for_writability(self):
        """
        Stop current thread until the channel is writable.

        :Return: `False` if it won't be readable (e.g. is closed)
        """
        return False

    @abstractmethod
    def handle_write(self):
        """
        Handle the 'channel writable' state. E.g. send buffered data via a
        socket.
        """
        pass

    @abstractmethod
    def handle_read(self):
        """
        Handle the 'channel readable' state. E.g. read from a socket.
        """
        pass

    @abstractmethod
    def handle_hup(self):
        """
        Handle the 'channel hungup' state. The handler should not be writtable
        after this.
        """
        pass

    @abstractmethod
    def handle_err(self):
        """
        Handle an error reported.
        """
        pass

    @abstractmethod
    def handle_nval(self):
        """
        Handle an 'invalid file descriptor' event.
        """
        pass

    @abstractmethod
    def close(self):
        """Close the channell immediately, so it won't expect more events."""
        pass

class Event(metaclass=ABCMeta):
    """Base class for PyXMPP2 events.
    """

    @abstractmethod
    def __str__(self):
        return repr(self)

QUIT = None
class QuitEvent(Event):
    """The `QUIT` event class."""
    # pylint: disable-msg=W0232,R0903
    def __str__(self):
        return "Quit"
QUIT = QuitEvent()
del QuitEvent

class EventHandler(metaclass=ABCMeta):
    """Base class for PyXMPP event handlers."""

def event_handler(event_class = None):
    """Method decorator generator for decorating event handlers.

    To be used on `EventHandler` subclass methods only.

    Such methods may return:
        - `True`: if they 'completely' handled the event and no more events
          should be called (use with care)
        - `QUIT`: to quit the main loop. Other handlers still will be called
          for current event and nother events in the queue.
    
    :Parameters:
        - `event_class`: event class expected
    :Types:
        - `event_class`: subclass of `Event`
    """
    def decorator(func):
        """The decorator"""
        func._pyxmpp_event_handled = event_class
        return func
    return decorator

class TimeoutHandler(metaclass=ABCMeta):
    """Base class for PyXMPP timeout handlers."""

def timeout_handler(interval, recurring = None):
    """Method decorator generator for decorating event handlers.
    
    To be used on `TimeoutHandler` subclass methods only.
    
    :Parameters:
        - `interval`: interval (in seconds) before the method will be called.
        - `recurring`: When `True`, the handler will be called each `interval`
          seconds, when `False` it will be called only once. If `True`,
          then the handler should return the next interval or `None` if it
          should not be called again.
    :Types:
        - `interval`: `float`
        - `recurring`: `bool`
    """
    def decorator(func):
        """The decorator"""
        func._pyxmpp_timeout = interval
        func._pyxmpp_recurring = recurring
        return func
    return decorator

class MainLoop(metaclass=ABCMeta):
    """Base class for main loop implementations."""
    @abstractmethod
    def add_handler(self, handler):
        """Add a new handler to the main loop.

        :Parameters:
            - `handler`: the handler object to add
        :Types:
            - `handler`: `IOHandler` or `EventHandler` or `TimeoutHandler`
        """
        pass

    @abstractmethod
    def remove_handler(self, handler):
        """Add a new handler to the main loop.

        Do nothing if the handler is not registered at the main loop.

        :Parameters:
            - `handler`: the handler object to add
        :Types:
            - `handler`: `IOHandler` or `EventHandler` or `TimeoutHandler`
        """
        pass
    
    def delayed_call(self, delay, function):
        """Schedule function to be called from the main loop after `delay`
        seconds.

        :Parameters:
            - `delay`: seconds to wait
        :Types:
            - `delay`: `float`
        """
        main_loop = self
        handler = []
        class DelayedCallHandler(TimeoutHandler):
            """Wrapper timeout handler class for the delayed call."""
            # pylint: disable=R0903
            @timeout_handler(delay, False)
            def callback(self):
                """Wrapper timeout handler method for the delayed call."""
                try:
                    function()
                finally:
                    main_loop.remove_handler(handler[0])
        handler.append(DelayedCallHandler())
        self.add_handler(handler[0])

    @abstractmethod
    def quit(self):
        """Make the loop stop after the current iteration."""
        pass

    @abstractproperty
    def started(self):
        """`True` then the loop has been started.
        """
        return False

    @abstractproperty
    def finished(self):
        """`True` then the loop has been finished or is about to finish (the
        final iteration in progress).
        """
        return False

    @abstractmethod
    def loop(self, timeout = None):
        """Run the loop.
        
        :Parameters:
            - `timeout`: time to loop, if not given the method will run
              until `finished`
        :Types:
            - `timeout`: `float`
        """
        pass

    @abstractmethod
    def loop_iteration(self, timeout = 1):
        """Single loop iteration.

        :Parameters:
            - `timeout`: maximum time (in seconds) to block for
        :Types:
            - `timeout`: `float`
        
        """
        pass

