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

"""XMPP transport.

This module provides the abstract base class for XMPP transports (mechanisms
used to send and receive XMPP content, not to be confused with protocol
gateways sometimes also called 'transports') and the standard TCP transport.
"""



__docformat__ = "restructuredtext en"

import socket
import threading
import errno
import logging
import ssl

from functools import partial
from collections import deque

from .etree import element_to_unicode
from .mainloop.interfaces import IOHandler, HandlerReady, PrepareAgain
from .settings import XMPPSettings
from .exceptions import DNSError, PyXMPPIOError
from .streamevents import ResolvingSRVEvent, ResolvingAddressEvent
from .streamevents import ConnectedEvent, ConnectingEvent, DisconnectedEvent
from .streamevents import TLSConnectingEvent, TLSConnectedEvent
from .xmppserializer import XMPPSerializer
from .xmppparser import StreamReader
from .mainloop.wait import wait_for_write
from .interfaces import XMPPTransport

# pylint: disable=W0611
from . import resolver  

logger = logging.getLogger("pyxmpp2.transport")

IN_LOGGER = logging.getLogger("pyxmpp2.IN")
OUT_LOGGER = logging.getLogger("pyxmpp2.OUT")

class WriteJob(object):
    """Base class for objects put to the `TCPTransport` write queue."""
    # pylint: disable-msg=R0903
    def __repr__(self):
        return "<WriteJob: {0}>".format(self.__class__.__name__)

class ContinueConnect(WriteJob):
    """Object to signal (via the write queue) a pending connect request.
    """
    # pylint: disable-msg=R0903
    pass

class StartTLS(WriteJob):
    """StartTLS request for the `TCPTransport` write queue."""
    # pylint: disable-msg=R0903
    def __init__(self, **kwargs):
        WriteJob.__init__(self)
        self.kwargs = kwargs
    def __repr__(self):
        args = [ "{0}={1!r}".format(k, v) for (k, v) in list(self.kwargs.items()) ]
        return "<WriteJob: StartTLS: {0}>".format(" ".join(args))

class TLSHandshake(WriteJob):
    """Object to signal (via the write queue) a pending TLS handshake.
    """
    # pylint: disable-msg=R0903
    pass

class WriteData(WriteJob):
    """Data queued for write.
    """
    # pylint: disable-msg=R0903
    def __init__(self, data):
        WriteJob.__init__(self)
        self.data = data
    def __repr__(self):
        return "<WriteJob: WriteData: {0!r}>".format(self.data)

class TCPTransport(XMPPTransport, IOHandler):
    """XMPP over TCP with optional TLS.

    :Ivariables:
        - `lock`: the lock protecting this object
        - `settings`: settings for this object
          socket is currently open)
        - `_dst_addr`: socket address currently in use
        - `_dst_addrs`: list of (family, sockaddr) candidates to connect to
        - `_dst_family`: address family of the socket
        - `_dst_hostname`: hostname the transport is connecting to or connected
          to
        - `_dst_name`: requested domain name of the remote service
        - `_dst_nameports`: list of (hostname, port) candidates to connect to
        - `_dst_port`: requested port of the remote service
        - `_dst_service`: requested service name (e.g. 'xmpp-client')
        - `_eof`: `True` when reading side of the socket is closed
        - `_event_queue`: queue to send connection events to
        - `_hup`: `True` when the writing side of the socket is closed
        - `_reader`: parser for the data received from the socket
        - `_serializer`: XML serializer for data sent over the socket
        - `_socket`: socket currently used by the transport (`None` if no
        - `_state_cond`: condition object to synchronize threads over state
          change
        - `_state`: connection state (one of: `None`, "resolve-srv",
          "resolve-hostname", "connect", "connected", "tls-handshake",
          "closing", "closed", "aborted")
        - `_stream`: the stream associated with this transport
        - `_tls_state`: state of TLS handshake
    :Types:
        - `lock`: :std:`threading.RLock`
        - `settings`: `XMPPSettings`
        - `_dst_addr`: tuple
        - `_dst_addrs`: list of tuples
        - `_dst_family`: `int`
        - `_dst_hostname`: `str`
        - `_dst_name`: `str`
        - `_dst_nameports`: list of tuples
        - `_dst_port`: `int`
        - `_dst_service`: `str`
        - `_eof`: `bool`
        - `_event_queue`: :std:`Queue.Queue`
        - `_hup`: `bool`
        - `_reader`: `StreamReader`
        - `_serializer`: `XMPPSerializer`
        - `_socket`: :std:`socket.socket`
        - `_state_cond`: :std:`threading.Condition`
        - `_state`: `str`
        - `_stream`: `streambase.StreamBase`
        - `_tls_state`: `str`
    """
    # pylint: disable=R0902
    def __init__(self, settings = None, sock = None):
        """Initialize the `TCPTransport` object.

        :Parameters:
            - `settings`: XMPP settings to use
            - `sock`: existing socket, e.g. for accepted incoming connection.
        """
        if settings:
            self.settings = settings
        else:
            self.settings = XMPPSettings()
        self.lock = threading.RLock()
        self._write_queue = deque()
        self._write_queue_cond = threading.Condition(self.lock)
        self._eof = False
        self._hup = False
        self._stream = None
        self._serializer = None
        self._reader = None
        self._dst_name = None
        self._dst_port = None
        self._dst_service = None
        self._dst_nameports = None
        self._dst_hostname = None
        self._dst_addrs = None
        self._tls_state = None
        self._state_cond = threading.Condition(self.lock)
        if sock is None:
            self._socket = None
            self._dst_addr = None
            self._family = None
            self._state = None
        else:
            self._socket = sock
            self._family = sock.family
            self._dst_addr = sock.getpeername()
            self._state = "connected"
            self._socket.setblocking(False)
        self._event_queue = self.settings["event_queue"]

    def _set_state(self, state):
        """Set `_state` and notify any threads waiting for the change.
        """
        logger.debug(" _set_state({0!r})".format(state))
        self._state = state
        self._state_cond.notify()

    def connect(self, addr, port = None, service = None):
        """Start establishing TCP connection with given address.

        One of: `port` or `service` must be provided and `addr` must be 
        a domain name and not an IP address if `port` is not given.

        When `service` is given try an SRV lookup for that service
        at domain `addr`. If `service` is not given or `addr` is an IP address, 
        or the SRV lookup fails, connect to `port` at host `addr` directly.

        [initiating entity only]

        :Parameters:
            - `addr`: peer name or IP address
            - `port`: port number to connect to
            - `service`: service name (to be resolved using SRV DNS records)
        """
        with self.lock:
            self._connect(addr, port, service)

    def _connect(self, addr, port, service):
        """Same as `connect`, but assumes `lock` acquired.
        """
        self._dst_name = addr
        self._dst_port = port
        family = None
        try:
            res = socket.getaddrinfo(addr, port, socket.AF_UNSPEC,
                                socket.SOCK_STREAM, 0, socket.AI_NUMERICHOST)
            family = res[0][0]
            sockaddr = res[0][4]
        except socket.gaierror:
            family = None
            sockaddr = None

        if family is not None:
            if not port:
                raise ValueError("No port number given with literal IP address")
            self._dst_service = None
            self._family = family
            self._dst_addrs = [(family, sockaddr)]
            self._set_state("connect")
        elif service is not None:
            self._dst_service = service
            self._set_state("resolve-srv")
            self._dst_name = addr
        elif port:
            self._dst_nameports = [(self._dst_name, self._dst_port)]
            self._dst_service = None
            self._set_state("resolve-hostname")
        else:
            raise ValueError("No port number and no SRV service name given")

    def _resolve_srv(self):
        """Start resolving the SRV record.
        """
        resolver = self.settings["dns_resolver"] # pylint: disable=W0621
        self._set_state("resolving-srv")
        resolver.resolve_srv(self._dst_name, self._dst_service, "tcp",
                                                    callback = self._got_srv)
        self.event(ResolvingSRVEvent(self._dst_name, self._dst_service))

    def _got_srv(self, addrs):
        """Handle SRV lookup result.
        
        :Parameters:
            - `addrs`: properly sorted list of (hostname, port) tuples
        """
        with self.lock:
            if not addrs:
                self._dst_service = None
                if self._dst_port:
                    self._dst_nameports = [(self._dst_name, self._dst_port)]
                else:
                    self._dst_nameports = []
                    self._set_state("aborted")
                    raise DNSError("Could not resolve SRV for service {0!r}"
                            " on host {1!r} and fallback port number not given"
                                    .format(self._dst_service, self._dst_name))
            elif addrs == [(".", 0)]:
                self._dst_nameports = []
                self._set_state("aborted")
                raise DNSError("Service {0!r} not available on host {1!r}"
                                    .format(self._dst_service, self._dst_name))
            else:
                self._dst_nameports = addrs
            self._set_state("resolve-hostname")

    def _resolve_hostname(self):
        """Start hostname resolution for the next name to try.

        [called with `lock` acquired]
        """
        self._set_state("resolving-hostname")
        resolver = self.settings["dns_resolver"] # pylint: disable=W0621
        name, port = self._dst_nameports.pop(0)
        resolver.resolve_address(name, callback = partial(
                                self._got_addresses, name, port),
                                allow_cname = self._dst_service is None)
        self.event(ResolvingAddressEvent(name))

    def _got_addresses(self, name, port, addrs):
        """Handler DNS address record lookup result.
        
        :Parameters:
            - `name`: the name requested
            - `port`: port number to connect to
            - `addrs`: list of (family, address) tuples
        """
        with self.lock:
            if not addrs:
                if self._dst_nameports:
                    self._set_state("resolve-hostname")
                    return
                else:
                    self._dst_addrs = []
                    self._set_state("aborted")
                    raise DNSError("Could not resolve address record for {0!r}"
                                                                .format(name))
            else:
                self._dst_nameports = addrs
            self._dst_addrs = [ (family, (addr, port)) for (family, addr)
                                                                    in addrs ]
            self._set_state("connect")

    def _start_connect(self):
        """Start connecting to the next address on the `_dst_addrs` list.

        [ called with `lock` acquired ] 
        
        """
        family, addr = self._dst_addrs.pop(0)
        if not self._socket or self._family != family:
            self._socket = socket.socket(family, socket.SOCK_STREAM)
            self._socket.setblocking(False)
        self._dst_addr = addr
        self._family  = family
        try:
            self._socket.connect(addr)
        except socket.error as err:
            if err.args[0] == errno.EINPROGRESS:
                self._set_state("connecting")
                self._write_queue.append(ContinueConnect())
                self._write_queue_cond.notify()
                self.event(ConnectingEvent(addr))
                return
            elif self._dst_addrs:
                self._set_state("connect")
                return
            elif self._dst_nameports:
                self._set_state("resolve-hostname")
                return
            else:
                self._socket.close()
                self._socket = None
                self._set_state("aborted")
                self._write_queue.clear()
                self._write_queue_cond.notify()
                raise
        self.event(ConnectedEvent(self._dst_addr))
        self._set_state("connected")
        self._stream.transport_connected()

    def _continue_connect(self):
        """Continue connecting.

        [called with `lock` acquired]

        :Return: `True` when just connected
        """
        try:
            self._socket.connect(self._dst_addr)
        except socket.error as err:
            if err.args[0] == errno.EINPROGRESS:
                return None
            elif self._dst_addrs:
                self._set_state("connect")
                return None
            elif self._dst_nameports:
                self._set_state("resolve-hostname")
                return None
            else:
                self._socket.close()
                self._socket = None
                self._set_state("aborted")
                raise
        self._set_state("connected")
        self._stream.transport_connected()
        self.event(ConnectedEvent(self._dst_addr))

    def _write(self, data):
        """Write raw data to the socket.

        :Parameters:
            - `data`: data to send
        :Types:
            - `data`: `bytes`
        """
        OUT_LOGGER.debug("OUT: %r", data)
        if self._hup or not self._socket:
            raise PyXMPPIOError("Connection closed.")
        try:
            while data:
                try:
                    sent = self._socket.send(data)
                except ssl.SSLError as err:
                    if err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                        continue
                    else:
                        raise
                except socket.error as err:
                    if err.args[0] == errno.EINTR:
                        continue
                    if err.args[0] == errno.EWOULDBLOCK:
                        wait_for_write(self._socket)
                        continue
                    raise
                data = data[sent:]
        except (IOError, OSError, socket.error) as err:
            raise PyXMPPIOError("IO Error: {0}".format(err))

    def set_target(self, stream):
        """Make the `stream` the target for this transport instance.

        The 'stream_start', 'stream_end' and 'stream_element' methods
        of the target will be called when appropriate content is received.

        :Parameters:
            - `stream`: the stream handler to receive stream content
              from the transport
        :Types:
            - `stream`: `StreamBase`
        """
        with self.lock:
            if self._stream:
                raise ValueError("Target stream already set")
            self._stream = stream
            self._reader = StreamReader(stream)

    def send_stream_head(self, stanza_namespace, stream_from, stream_to, 
                        stream_id = None, version = '1.0', language = None):
        """
        Send stream head via the transport.

        :Parameters:
            - `stanza_namespace`: namespace of stream stanzas (e.g.
              'jabber:client')
            - `stream_from`: the 'from' attribute of the stream. May be `None`.
            - `stream_to`: the 'to' attribute of the stream. May be `None`.
            - `version`: the 'version' of the stream.
            - `language`: the 'xml:lang' of the stream
        :Types:
            - `stanza_namespace`: `str`
            - `stream_from`: `str`
            - `stream_to`: `str`
            - `version`: `str`
            - `language`: `str`
        """
        # pylint: disable=R0913
        with self.lock:
            self._serializer = XMPPSerializer(stanza_namespace,
                                            self.settings["extra_ns_prefixes"])
            head = self._serializer.emit_head(stream_from, stream_to,
                                                stream_id, version, language)
            self._write(head.encode("utf-8"))

    def restart(self):
        """Restart the stream after SASL or StartTLS handshake."""
        self._reader = StreamReader(self._stream)
        self._serializer = None

    def send_stream_tail(self):
        """
        Send stream tail via the transport.
        """
        with self.lock:
            if not self._socket or self._hup:
                logger.debug("Cannot send stream closing tag: already closed")
                return
            data = self._serializer.emit_tail()
            try:
                self._write(data.encode("utf-8"))
            except (IOError, SystemError, socket.error) as err:
                logger.debug("Sending stream closing tag failed: {0}"
                                                                .format(err))
            self._serializer = None
            self._hup = True
            if self._tls_state is None:
                try:
                    self._socket.shutdown(socket.SHUT_WR)
                except socket.error:
                    pass
            self._set_state("closing")
            self._write_queue.clear()
            self._write_queue_cond.notify()

    def send_element(self, element):
        """
        Send an element via the transport.
        """
        with self.lock:
            if self._eof or self._socket is None or not self._serializer:
                logger.debug("Dropping element: {0}".format(
                                                element_to_unicode(element)))
                return
            data = self._serializer.emit_stanza(element)
            self._write(data.encode("utf-8"))

    def prepare(self):
        """When connecting start the next connection step and schedule
        next `prepare` call, when connected return `HandlerReady()`
        """
        result = HandlerReady()
        logger.debug("TCPHandler.prepare(): state: {0!r}".format(self._state))
        with self.lock:
            if self._state in ("connected", "closing", "closed", "aborted"):
                # no need to call prepare() .fileno() is stable
                pass
            elif self._state == "connect":
                self._start_connect()
                result = PrepareAgain(None)
            elif self._state == "resolve-hostname":
                self._resolve_hostname()
                result = PrepareAgain(0)
            elif self._state == "resolve-srv":
                self._resolve_srv()
                result = PrepareAgain(0)
            else:
                # wait for i/o, but keep calling prepare()
                result = PrepareAgain(None)
        logger.debug("TCPHandler.prepare(): new state: {0!r}"
                                                        .format(self._state))
        return result

    def fileno(self):
        """Return file descriptor to poll or select."""
        with self.lock:
            if self._socket is not None:
                return self._socket.fileno()
        return None
    
    def is_readable(self):
        """
        :Return: `True` when the I/O channel can be read
        """
        return self._socket is not None and not self._eof and (
                    self._state in ("connected", "closing")
                        or self._state == "tls-handshake" 
                                        and self._tls_state == "want_read")

    def wait_for_readability(self):
        """
        Stop current thread until the channel is readable.

        :Return: `False` if it won't be readable (e.g. is closed)
        """
        with self.lock:
            while True:
                if self._socket is None or self._eof:
                    return False
                if self._state in ("connected", "closing"):
                    return True
                if self._state == "tls-handshake" and \
                                            self._tls_state == "want_read":
                    return True
                self._state_cond.wait()

    def is_writable(self):
        """
        :Return: `False` as currently the data is always written synchronously
        """
        with self.lock:
            return self._socket and bool(self._write_queue)

    def wait_for_writability(self):
        """
        Stop current thread until the channel is writable.

        :Return: `False` if it won't be readable (e.g. is closed)
        """
        with self.lock:
            while True:
                if self._state in ("closing", "closed", "aborted"):
                    return False
                if self._socket and bool(self._write_queue):
                    return True
                self._write_queue_cond.wait()
        return False

    def handle_write(self):
        """
        Handle the 'channel writable' state. E.g. send buffered data via a
        socket.
        """
        with self.lock:
            logger.debug("handle_write: queue: {0!r}".format(self._write_queue))
            try:
                job = self._write_queue.popleft()
            except IndexError:
                return
            if isinstance(job, WriteData):
                self._do_write(job.data) # pylint: disable=E1101
            elif isinstance(job, ContinueConnect):
                self._continue_connect()
            elif isinstance(job, StartTLS):
                self._initiate_starttls(**job.kwargs)
            elif isinstance(job, TLSHandshake):
                self._continue_tls_handshake()
            else:
                raise ValueError("Unrecognized job in the write queue: "
                                        "{0!r}".format(job))

    def starttls(self, **kwargs):
        """Request a TLS handshake on the socket ans switch
        to encrypted output.
        The handshake will start after any currently buffered data is sent.
        
        :Parameters:
            - `kwargs`: arguments for :std:`ssl.wrap_socket`
        """
        with self.lock:
            self.event(TLSConnectingEvent())
            self._write_queue.append(StartTLS(**kwargs))
            self._write_queue_cond.notify()

    def getpeercert(self):
        """Return the peer certificate. The format is the same
        as for the standard :std:`ssl.SSLSocket.getpeercert()` method,
        but may (in future) include data not normally recognized by Python.
        """
        with self.lock:
            if not self._socket or self._tls_state != "connected":
                raise ValueError("Not TLS-connected")
            return self._socket.getpeercert()

    def _initiate_starttls(self, **kwargs):
        """Initiate starttls handshake over the socket.
        """
        if self._tls_state == "connected":
            raise RuntimeError("Already TLS-connected")
        kwargs["do_handshake_on_connect"] = False
        logger.debug("Wrapping the socket into ssl")
        self._socket = ssl.wrap_socket(self._socket, **kwargs)
        self._set_state("tls-handshake")
        self._continue_tls_handshake()

    def _continue_tls_handshake(self):
        """Continue a TLS handshake."""
        try:
            logger.debug(" do_handshake()")
            self._socket.do_handshake()
        except ssl.SSLError as err:
            if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                self._tls_state = "want_read"
                logger.debug("   want_read")
                self._state_cond.notify()
                return
            elif err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                self._tls_state = "want_write"
                logger.debug("   want_write")
                self._write_queue.appendleft(TLSHandshake)
                return
            else:
                raise
        self._tls_state = "connected"
        self._set_state("connected")
        self.event(TLSConnectedEvent(self._socket.cipher(),
                                                self._socket.getpeercert()))

    def handle_read(self):
        """
        Handle the 'channel readable' state. E.g. read from a socket.
        """
        with self.lock:
            logger.debug("handle_read()")
            if self._eof or self._socket is None:
                return
            if self._state == "tls-handshake":
                while True:
                    logger.debug("tls handshake read...")
                    self._continue_tls_handshake()
                    logger.debug("  state: {0}".format(self._tls_state))
                    if self._tls_state != "want_read":
                        break
            elif self._tls_state == "connected":
                while self._socket and not self._eof:
                    logger.debug("tls socket read...")
                    try:
                        data = self._socket.read(4096)
                    except ssl.SSLError as err:
                        if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                            break
                        elif err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                            break
                        else:
                            raise
                    except socket.error as err:
                        if err.args[0] == errno.EINTR:
                            continue
                        elif err.args[0] == errno.EWOULDBLOCK:
                            break
                        elif err.args[0] == errno.ECONNRESET:
                            logger.warning("Connection reset by peer")
                            data = None
                        else:
                            raise
                    self._feed_reader(data)
            else:
                while self._socket and not self._eof:
                    logger.debug("raw socket read...")
                    try:
                        data = self._socket.recv(4096)
                    except socket.error as err:
                        if err.args[0] == errno.EINTR:
                            continue
                        elif err.args[0] == errno.EWOULDBLOCK:
                            break
                        elif err.args[0] == errno.ECONNRESET:
                            logger.warning("Connection reset by peer")
                            data = None
                        else:
                            raise
                    self._feed_reader(data)

    def handle_hup(self):
        """
        Handle the 'channel hungup' state. The handler should not be writable
        after this.
        """
        self._hup = True

    def handle_err(self):
        """
        Handle an error reported.
        """
        with self.lock:
            self._socket.close()
            self._socket = None
            self._set_state("aborted")
            self._write_queue.clear()
            self._write_queue_cond.notify()
        raise PyXMPPIOError("Unhandled error on socket")

    def handle_nval(self):
        """
        Handle an error reported.
        """
        if self._socket is None:
            # socket closed by other thread
            return
        self._set_state("aborted")
        raise PyXMPPIOError("Invalid file descriptor used in main event loop")

    def is_connected(self):
        """
        Check if the transport is connected.

        :Return: `True` if is connected.
        """
        return self._state in ("connected", "tls-handshake") \
                                            and not self._eof and not self._hup

    def disconnect(self):
        """Disconnect the stream gracefully."""
        logger.debug("TCPTransport.disconnect()")
        with self.lock:
            if self._socket is None:
                if self._state != "closed":
                    self.event(DisconnectedEvent(self._dst_addr))
                    self._set_state("closed")
                return
            if self._hup or not self._serializer:
                self._close()
            else:
                self.send_stream_tail()

    def close(self):
        """Close the stream immediately, so it won't expect more events."""
        with self.lock:
            self._close()

    def _close(self):
        """Same as `_close` but expects `lock` acquired.
        """
        if self._state != "closed":
            self.event(DisconnectedEvent(self._dst_addr))
            self._set_state("closed")
        if self._socket is None:
            return
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self._socket.close()
        self._socket = None
        self._write_queue.clear()
        self._write_queue_cond.notify()

    def _feed_reader(self, data):
        """Feed the stream reader with data received.

        [ called with `lock` acquired ] 

        If `data` is None or empty, then stream end (peer disconnected) is
        assumed and the stream is closed.

        `lock` is acquired during the operation.

        :Parameters:
            - `data`: data received from the stream socket.
        :Types:
            - `data`: `str`
        """
        IN_LOGGER.debug("IN: %r", data)
        if data:
            self._reader.feed(data)
        else:
            self._eof = True
            self._stream.stream_eof()
            if not self._serializer:
                if self._state != "closed":
                    self.event(DisconnectedEvent(self._dst_addr))
                    self._set_state("closed")

    def event(self, event):
        """Pass an event to the target stream or just log it."""
        logger.debug("TCP transport event: {0}".format(event))
        if self._stream:
            event.stream = self._stream
        self._event_queue.put(event)

