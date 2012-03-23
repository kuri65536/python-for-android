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
# pylint: disable-msg=W0201

"""XMPP stream events."""

# pylint: disable-msg=R0903,W0231



from .mainloop.interfaces import Event

class StreamEvent(Event):
    """Base class for all stream events."""
    # pylint: disable-msg=W0223,W0232
    stream = None

class AuthenticatedEvent(StreamEvent):
    """Event raised after stream authentication is complete.
    Usually it happens after SASL authentication and before XMPP resource
    binding.
    
    Default action: none
    
    :Ivariables:
        - `authenticated_jid`: JID (bare) just authenticated
    :Types:
        - `authenticated_jid`: `pyxmpp2.jid.JID`
    """
    def __init__(self, authenticated_jid):
        self.authenticated_jid = authenticated_jid
    def __str__(self):
        return "Authenticated: {0}".format(self.authenticated_jid)


class AuthorizedEvent(StreamEvent):
    """Event raised after stream authentication and authorization is complete.
    Usually it happens after SASL authentication and XMPP resource binding.
    
    Default action: none
    
    :Ivariables:
        - `authorized_jid`: JID just authorized to use the stream
    :Types:
        - `authorized_jid`: `pyxmpp2.jid.JID`
    """
    def __init__(self, authorized_jid):
        self.authorized_jid = authorized_jid
    def __str__(self):
        return "Authorized: {0}".format(self.authorized_jid)

class BindingResourceEvent(StreamEvent):
    """Emitted when resource binding is initiated for the stream.

    Probably useful only for connection progres monitoring.
    
    :Ivariables:
        - `resource`: the resource
    :Types:
        - `resource`: `str`
    """
    def __init__(self, resource):
        self.resource = resource
    def __str__(self):
        if self.resource is None:
            return "Requesting server-generated resource"
        else:
            return "Binding resource '{0}'".format(self.resource)

class ConnectedEvent(StreamEvent):
    """Emitted after the stream socket is connected, just before the actual
    XMPP exchange happens.
    
    :Ivariables:
        - `sockaddr`: remote IP address and port
    :Types:
        - `sockaddr`: (`str`, `int`)
    """
    def __init__(self, sockaddr):
        self.sockaddr = sockaddr
    def __str__(self):
        ipaddr, port = self.sockaddr
        if ":" in ipaddr:
            return "Connected to [{0}]:{1}".format(ipaddr, port)
        else:
            return "Connected to {0}:{1}".format(ipaddr, port)

class ConnectingEvent(StreamEvent):
    """Emitted on TCP connection attempt. May happen multiple times during
    single stream connection - several addresses may be tried until one answers.

    Probably useful only for connection progres monitoring.
    
    :Ivariables:
        - `sockaddr`: remote IP address and port
    :Types:
        - `sockaddr`: (`str`, `int`)
    """
    def __init__(self, sockaddr):
        self.sockaddr = sockaddr
    def __str__(self):
        ipaddr, port = self.sockaddr
        if ":" in ipaddr:
            return "Connecting to [{0}]:{1}...".format(ipaddr, port)
        else:
            return "Connecting to {0}:{1}...".format(ipaddr, port)

class ConnectionAcceptedEvent(StreamEvent):
    """Emitted when a new TCP connection is accepted.
    
    :Ivariables:
        - `sockaddr`: remote IP address and port
    :Types:
        - `sockaddr`: (`str`, `int`)
    """
    def __init__(self, sockaddr):
        self.sockaddr = sockaddr
    def __str__(self):
        ipaddr, port = self.sockaddr
        if ":" in ipaddr:
            return "Connection received from [{0}]:{1}".format(ipaddr, port)
        else:
            return "Connection received from {0}:{1}".format(ipaddr, port)

class DisconnectedEvent(StreamEvent):
    """Emitted when the stream is disconnected. No more stanzas will 
    be received and no more stanzas can be sent via this stream.
    
    :Ivariables:
        - `peer`: peer name
    :Types:
        - `peer`: `pyxmpp2.jid.JID`
    """
    def __init__(self, peer):
        self.peer = peer
    def __str__(self):
        return "Disconnected from {0}".format(self.peer)

class GotFeaturesEvent(StreamEvent):
    """Emitted when the stream features are received.

    Default action (skipped if the handler returns `True`) may be, depending
    on the features available, one of:
      
    - StartTLS initiation
    - SASL authentication
    - Resource binding
    
    :Ivariables:
        - `features`: the <stream:features/> element
    :Types:
        - `features`: :etree:`ElementTree.Element`
    """
    def __init__(self, features):
        self.features = features 
    def __str__(self):
        return "Got stream features"


class ResolvingAddressEvent(StreamEvent):
    """Emitted when staring to resolve an address (A or AAAA) DNS record
    for a hostname.

    Probably useful only for connection progres monitoring.
    
    :Ivariables:
        - `hostname`: host name
    :Types:
        - `hostname`: `str`
    """
    def __init__(self, hostname):
        self.hostname = hostname
    def __str__(self):
        return "Resolving address of '{0}'...".format(self.hostname)

class ResolvingSRVEvent(StreamEvent):
    """Emitted when staring to resolve an SRV DNS record for a domain.

    Probably useful only for connection progres monitoring.
    
    :Ivariables:
        - `domain`: domain name
        - `service`: service name
    :Types:
        - `hostname`: `str`
        - `service`: `str`
    """
    def __init__(self, domain, service):
        self.domain = domain
        self.service = service
    def __str__(self):
        return "Resolving SRV record of '{0}' for '{1}...".format(
                                                self.service, self.domain)

class StreamConnectedEvent(StreamEvent):
    """Emitted when the initial stream handshake (<stream:stream> tag exchange)
    is completed, before any authentication.
    
    :Ivariables:
        - `peer`: peer name
    :Types:
        - `peer`: `pyxmpp2.jid.JID`
    """
    def __init__(self, peer):
        self.peer = peer
    def __str__(self):
        return "Connected to {0}".format(self.peer)

class TLSConnectingEvent(StreamEvent):
    """Emitted when the TLS handshake starts.
    """
    def __init__(self):
        pass
    def __str__(self):
        return "TLS connecting"

class TLSConnectedEvent(StreamEvent):
    """Emitted when the TLS layer has been established.
    
    :Ivariables:
        - `cipher`: a three-value tuple containing the name of the cipher being
          used, the version of the SSL protocol that defines its use, and the
          number of secret bits being used
        - `peer_certificate`: dictionary describing the peer certificate 
    :Types:
        - `peer`: `pyxmpp2.jid.JID`
    """
    def __init__(self, cipher, peer_certificate):
        self.cipher = cipher
        self.peer_certificate = peer_certificate
    def __str__(self):
        if self.peer_certificate and 'subject' in self.peer_certificate:
            dname = ", ".join( [ ", ".join(
                        [ "{0}={1}".format(k,v) for k, v in dn_tuple ] ) 
                            for dn_tuple in self.peer_certificate["subject"] ])
            return ("TLS connected to {0} using {1} cipher {2} ({3} bits)"
                                .format(dname, self.cipher[0], self.cipher[1], 
                                                                self.cipher[2]))
        return "TLS connected using {0} cipher {1} ({2} bits)".format(
                            self.cipher[0], self.cipher[1], self.cipher[2])

class StreamRestartedEvent(StreamEvent):
    """Emitted after stream is restarted (<stream:stream> tag exchange)
    e.g. after SASL.
    
    :Ivariables:
        - `peer`: peer name
    :Types:
        - `peer`: `pyxmpp2.jid.JID`
    """
    def __init__(self, peer):
        self.peer = peer
    def __str__(self):
        return "Connected to {0}".format(self.peer)

