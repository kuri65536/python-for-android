#
# (C) Copyright 2003-2010 Jacek Konieczny <jajcus@jajcus.net>
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
"""Component (jabber:component:accept) stream handling.

Normative reference:
  - `JEP 114 <http://www.jabber.org/jeps/jep-0114.html>`__
"""



raise ImportError("{0} is not yet rewritten for PyXMPP2".format(__name__))

__docformat__="restructuredtext en"

import hashlib

import logging

from ..stream import Stream
from ..streambase import stanza_factory,HostMismatch
from ..xmlextra import common_doc,common_root
from ..utils import to_utf8
from ..exceptions import StreamError,FatalStreamError,ComponentStreamError,FatalComponentStreamError

class ComponentStream(Stream):
    """Handles jabberd component (jabber:component:accept) connection stream.

    :Ivariables:
        - `server`: server to use.
        - `port`: port number to use.
        - `secret`: authentication secret.
    :Types:
        - `server`: `str`
        - `port`: `int`
        - `secret`: `str`"""

    def __init__(self, jid, secret, server, port, keepalive = 0, owner = None):
        """Initialize a `ComponentStream` object.

        :Parameters:
            - `jid`: JID of the component.
            - `secret`: authentication secret.
            - `server`: server address.
            - `port`: TCP port number on the server.
            - `keepalive`: keepalive interval. 0 to disable.
            - `owner`: `Client`, `Component` or similar object "owning" this stream.
        """
        Stream.__init__(self, "jabber:component:accept",
                    sasl_mechanisms = [],
                    tls_settings = None,
                    keepalive = keepalive,
                    owner = owner)
        self.server=server
        self.port=port
        self.me=jid
        self.secret=secret
        self.process_all_stanzas=1
        self.__logger=logging.getLogger("pyxmpp2.jabberd.ComponentStream")

    def _reset(self):
        """Reset `ComponentStream` object state, making the object ready to
        handle new connections."""
        Stream._reset(self)

    def connect(self,server=None,port=None):
        """Establish a client connection to a server.

        [component only]

        :Parameters:
            - `server`: name or address of the server to use.  If not given
              then use the one specified when creating the object.
            - `port`: port number of the server to use.  If not given then use
              the one specified when creating the object.

        :Types:
            - `server`: `str`
            - `port`: `int`"""
        self.lock.acquire()
        try:
            self._connect(server,port)
        finally:
            self.lock.release()

    def _connect(self,server=None,port=None):
        """Same as `ComponentStream.connect` but assume `self.lock` is acquired."""
        if self.me.node or self.me.resource:
            raise Value("Component JID may have only domain defined")
        if not server:
            server=self.server
        if not port:
            port=self.port
        if not server or not port:
            raise ValueError("Server or port not given")
        Stream._connect(self,server,port,None,self.me)

    def accept(self,sock):
        """Accept an incoming component connection.

        [server only]

        :Parameters:
            - `sock`: a listening socket."""
        Stream.accept(self,sock,None)

    def stream_start(self,doc):
        """Process <stream:stream> (stream start) tag received from peer.

        Call `Stream.stream_start`, but ignore any `HostMismatch` error.

        :Parameters:
            - `doc`: document created by the parser"""
        try:
            Stream.stream_start(self,doc)
        except HostMismatch:
            pass

    def _post_connect(self):
        """Initialize authentication when the connection is established
        and we are the initiator."""
        if self.initiator:
            self._auth()

    def _compute_handshake(self):
        """Compute the authentication handshake value.

        :return: the computed hash value.
        :returntype: `str`"""
        return hashlib.sha1(to_utf8(self.stream_id)+to_utf8(self.secret)).hexdigest()

    def _auth(self):
        """Authenticate on the server.

        [component only]"""
        if self.authenticated:
            self.__logger.debug("_auth: already authenticated")
            return
        self.__logger.debug("doing handshake...")
        hash_value=self._compute_handshake()
        n=common_root.newTextChild(None,"handshake",hash_value)
        self._write_node(n)
        n.unlinkNode()
        n.freeNode()
        self.__logger.debug("handshake hash sent.")

    def _process_node(self,node):
        """Process first level element of the stream.

        Handle component handshake (authentication) element, and
        treat elements in "jabber:component:accept", "jabber:client"
        and "jabber:server" equally (pass to `self.process_stanza`).
        All other elements are passed to `Stream._process_node`.

        :Parameters:
            - `node`: XML node describing the element
        """
        ns=node.ns()
        if ns:
            ns_uri=node.ns().getContent()
        if (not ns or ns_uri=="jabber:component:accept") and node.name=="handshake":
            if self.initiator and not self.authenticated:
                self.authenticated=1
                self.state_change("authenticated",self.me)
                self._post_auth()
                return
            elif not self.authenticated and node.getContent()==self._compute_handshake():
                self.peer=self.me
                n=common_doc.newChild(None,"handshake",None)
                self._write_node(n)
                n.unlinkNode()
                n.freeNode()
                self.peer_authenticated=1
                self.state_change("authenticated",self.peer)
                self._post_auth()
                return
            else:
                self._send_stream_error("not-authorized")
                raise FatalComponentStreamError("Hanshake error.")

        if ns_uri in ("jabber:component:accept","jabber:client","jabber:server"):
            stanza=stanza_factory(node)
            self.lock.release()
            try:
                self.process_stanza(stanza)
            finally:
                self.lock.acquire()
                stanza.free()
            return
        return Stream._process_node(self,node)

# vi: sts=4 et sw=4
