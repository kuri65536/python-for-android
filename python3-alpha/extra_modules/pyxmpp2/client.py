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

"""Basic XMPP-IM client implementation.

The `Client` class provides the base for client applications.

To create an XMPP client session applications should create a `Client` instance 
providing in the constructor: a client JID, settings and handlers providing
application behaviour (the list may contain a single handler object which will
be 'the application). The `Client` class will provide some other handlers:
`StreamTLSHandler`, `StreamSASLHandler`, `SessionHandler`,
`ResourceBindingHandler` and `RosterClient`. The last one is available via the
`Client.roster_client` attribute and should be used to manipulate the roster.
The roster itself is available via the `Client.roster` property.

The `Client` object will open an XMPP stream after the `Client.connect` method
is called. It will send the initial presence (specified by 
the :r:`initial_presence setting` ) upon log-in and the final presence on
log-out.  Other presence handling, including subscriptions is the
responsibility of the application.

The API is asynchronous and actual connection is made and data exchanged in the
main event loop. A `MainLoop` object can be passed to the `Client` constructor,
but this is not needed, as `Client` will create one if needed. The main loop
can be started by `Client.run()`.

To close the XMPP session use the `Client.disconnect()` method.

Normative reference:
  - :RFC:`6120`
  - :RFC:`6121`
"""



__docformat__ = "restructuredtext en"

import logging

from .clientstream import ClientStream
from .mainloop import main_loop_factory
from .interfaces import EventHandler, event_handler
from .interfaces import TimeoutHandler, timeout_handler
from .streamevents import DisconnectedEvent, AuthenticatedEvent
from .streamevents import AuthorizedEvent
from .transport import TCPTransport
from .settings import XMPPSettings
from .session import SessionHandler
from .streamtls import StreamTLSHandler
from .streamsasl import StreamSASLHandler
from .binding import ResourceBindingHandler
from .stanzaprocessor import StanzaProcessor
from .roster import RosterClient
from .presence import Presence

logger = logging.getLogger("pyxmpp2.client")

def _move_session_handler(handlers):
    """Find a SessionHandler instance in the list and move it to the beginning.
    """
    index = 0
    for i, handler in enumerate(handlers):
        if isinstance(handler, SessionHandler):
            index = i
            break
    if index:
        handlers[:index + 1] = [handlers[index]] + handlers[:index]

class Client(StanzaProcessor, TimeoutHandler, EventHandler):
    """Base class for an XMPP-IM client.

    Joins the `MainLoop`, `ClientStream` and some basic handlers together,
    so a client application needs only to add its handlers.

    :Ivariables:
        - `jid`: configured JID of the client (current full JID is avialable as
          ``self.stream.jid``).
        - `main_loop`: the main loop object
        - `settings`: configuration settings
        - `handlers`: stream and main loop handlers provided via the
          constructor
        - `stream`: the stream object when connected
        - `roster_client`: the roster interface object
        - `_ml_handlers`: list of handlers installed by this object to at the
          main loop
    :Types:
        - `jid`: `jid.JID`
        - `main_loop`: `main_loop.interfaces.MainLoop`
        - `settings`: `XMPPSettings`
        - `stream`: `clientstream.ClientStream`
        - `roster_client`: `RosterClient`
    """
    # pylint: disable-msg=R0902
    def __init__(self, jid, handlers, settings = None, main_loop = None):
        """Initialize a Client object.

        :Parameters:
            - `jid`: user JID for the connection.
            - `settings`: client settings.
            - `main_loop`: Main event loop to attach to. If None, a loop
              will be created.
        :Types:
            - `jid`: `jid.JID`
            - `settings`: `settings.XMPPSettings`
            - `main_loop`: `main_loop.interfaces.MainLoop`
        """
        self._ml_handlers = []
        self.jid = jid
        self.settings = settings if settings else XMPPSettings()
        StanzaProcessor.__init__(self, self.settings["default_stanza_timeout"])
        self.handlers = handlers
        self._base_handlers = self.base_handlers_factory()
        self.roster_client = self.roster_client_factory()
        self._base_handlers += [self.roster_client]
        self._ml_handlers += list(handlers) + self._base_handlers + [self]
        _move_session_handler(self._ml_handlers)
        if main_loop is not None:
            self.main_loop = main_loop
            for handler in self._ml_handlers:
                self.main_loop.add_handler(handler)
        else:
            self.main_loop = main_loop_factory(settings, self._ml_handlers)
        self.stream = None

    def __del__(self):
        for handler in self._ml_handlers:
            self.main_loop.remove_handler(handler)
        self._ml_handlers = []

    @property
    def roster(self):
        """Current roster.

        Shortcut for ``self.roster_client.roster``.
        """
        with self.lock:
            if self.roster_client is not None:
                return self.roster_client.roster
            else:
                return None

    def connect(self):
        """Schedule a new XMPP c2s connection.
        """
        with self.lock:
            if self.stream:
                logger.debug("Closing the previously used stream.")
                self._close_stream()

            transport = TCPTransport(self.settings)
            
            addr = self.settings["server"]
            if addr:
                service = None
            else:
                addr = self.jid.domain
                service = self.settings["c2s_service"]

            transport.connect(addr, self.settings["c2s_port"], service)
            handlers = self._base_handlers
            handlers += self.handlers + [self]
            self.clear_response_handlers()
            self.setup_stanza_handlers(handlers, "pre-auth")
            stream = ClientStream(self.jid, self, handlers, self.settings)
            stream.initiate(transport)
            self.main_loop.add_handler(transport)
            self.main_loop.add_handler(stream)
            self._ml_handlers += [transport, stream]
            self.stream = stream
            self.uplink = stream

    def disconnect(self):
        """Gracefully disconnect from the server."""
        with self.lock:
            if self.stream:
                if self.settings["initial_presence"]:
                    self.send(Presence(stanza_type = "unavailable"))
                self.stream.disconnect()

    def close_stream(self):
        """Close the stream immediately.
        """
        with self.lock:
            self._close_stream()

    def _close_stream(self):
        """Same as `close_stream` but with the `lock` acquired.
        """
        self.stream.close()
        if self.stream.transport in self._ml_handlers:
            self._ml_handlers.remove(self.stream.transport)
            self.main_loop.remove_handler(self.stream.transport)
        self.stream = None
        self.uplink = None

    def run(self, timeout = None):
        """Call the main loop.

        Convenience wrapper for ``self.main_loop.loop``
        """
        self.main_loop.loop(timeout)

    @event_handler(AuthenticatedEvent)
    def _stream_authenticated(self, event):
        """Handle the `AuthenticatedEvent`.
        """
        with self.lock:
            if event.stream != self.stream:
                return
            self.me = event.stream.me
            self.peer = event.stream.peer
            handlers = self._base_handlers
            handlers += self.handlers + [self]
            self.setup_stanza_handlers(handlers, "post-auth")

    @event_handler(AuthorizedEvent)
    def _stream_authorized(self, event):
        """Handle the `AuthorizedEvent`.
        """
        with self.lock:
            if event.stream != self.stream:
                return
            self.me = event.stream.me
            self.peer = event.stream.peer
            presence = self.settings["initial_presence"]
            if presence:
                self.send(presence)

    @event_handler(DisconnectedEvent)
    def _stream_disconnected(self, event):
        """Handle stream disconnection event.
        """
        with self.lock:
            if event.stream != self.stream:
                return
            if self.stream is not None and event.stream == self.stream:
                if self.stream.transport in self._ml_handlers:
                    self._ml_handlers.remove(self.stream.transport)
                    self.main_loop.remove_handler(self.stream.transport)
                self.stream = None
                self.uplink = None

    @timeout_handler(1)
    def regular_tasks(self):
        """Do some housekeeping (cache expiration, timeout handling).

        This method should be called periodically from the application's
        main loop.
        
        :Return: suggested delay (in seconds) before the next call to this
                                                                    method.
        :Returntype: `int`
        """
        with self.lock:
            ret = self._iq_response_handlers.expire()
            if ret is None:
                return 1
            else:
                return min(1, ret)

    def base_handlers_factory(self):
        """Default base client handlers factory.

        Subclasses can provide different behaviour by overriding this.

        :Return: list of handlers
        """
        tls_handler = StreamTLSHandler(self.settings)
        sasl_handler = StreamSASLHandler(self.settings)
        session_handler = SessionHandler()
        binding_handler = ResourceBindingHandler(self.settings)
        return [tls_handler, sasl_handler, binding_handler, session_handler]

    def roster_client_factory(self):
        """Creates the `RosterClient` instance for the `roster_client`
        attribute.
        
        Subclasses can provide different behaviour by overriding this. The
        overriding method can return `None` if no roster client is needed.

        :Return: `RosterClient`
        """
        return RosterClient(self.settings)

def _initial_presence_factory(settings):
    """Factory for the :r:`initial_presence setting` default.
    """
    return Presence()

XMPPSettings.add_setting("initial_presence",
    factory = _initial_presence_factory,
    default_d = "Just ``Presence()``",
    doc = """Default initial presence stanza, to be send on login.
Set to ``None`` not to send the initial presence."""
    )

XMPPSettings.add_setting("c2s_port", default = 5222, basic = True,
    type = int, validator = XMPPSettings.get_int_range_validator(1, 65536),
    cmdline_help = "Port number for XMPP client connections",
    doc = """Port number for client to server connections."""
    )

XMPPSettings.add_setting("c2s_service", default = "xmpp-client",
    type = str,
    cmdline_help = "SRV service name XMPP client connections",
    doc = """SRV service name for client to server connections."""
    )

XMPPSettings.add_setting("server", type = str, basic = True,
    cmdline_help = "Server address. (Default: use SRV lookup)",
    doc = """Server address to connect to. By default a DNS SRV record look-up
is done for the requested JID domain part and if that fails - 'A' or 'AAAA'
record lookup for the same domain. This setting may be used to force using
a specific server or when SRV look-ups are not available."""
    )
XMPPSettings.add_setting("default_stanza_timeout", type = float, default = 300,
        validator = XMPPSettings.validate_positive_float,
        cmdline_help = "Time in seconds to wait for a stanza response",
        doc = """Time in seconds to wait for a stanza response."""
    )

# vi: sts=4 et sw=4
