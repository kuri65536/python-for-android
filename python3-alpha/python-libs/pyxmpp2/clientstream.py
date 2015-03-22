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
# pylint: disable-msg=W0221

"""Client-Server stream handling.

Normative reference:
  - `RFC 6120 <http://www.ietf.org/rfc/rfc6120.txt>`__
"""



__docformat__ = "restructuredtext en"

from .streambase import StreamBase
from .jid import JID
from .settings import XMPPSettings
from .constants import STANZA_CLIENT_NS

class ClientStream(StreamBase):
    """Handles XMPP-IM c2s stream.

    Both client and server side of the connection is supported.
    """
    # pylint: disable=R0904
    def __init__(self, jid, stanza_route, handlers, settings = None):
        """Initialize the ClientStream object.

        :Parameters:
            - `jid`: local JID.
            - `handlers`: XMPP feature and event handlers
            - `settings`: PyXMPP settings for the stream
        :Types:
            - `jid`: `JID`
            - `settings`: `XMPPSettings`
        """
        if handlers is None:
            handlers = []
        if settings is None:
            settings = XMPPSettings()
        if "resource" not in settings:
            settings["resource"] = jid.resource
        StreamBase.__init__(self, STANZA_CLIENT_NS, stanza_route, 
                                                        handlers, settings)
        self.me = JID(jid.local, jid.domain)
    
    def initiate(self, transport, to = None):
        """Initiate an XMPP connection over the `transport`.
        
        :Parameters:
            - `transport`: an XMPP transport instance
            - `to`: peer name (defaults to own jid domain part)
        """
        if to is None:
            to = JID(self.me.domain)
        return StreamBase.initiate(self, transport, to)

    def receive(self, transport, myname = None):
        """Receive an XMPP connection over the `transport`.

        :Parameters:
            - `transport`: an XMPP transport instance
            - `myname`: local stream endpoint name (defaults to own jid domain
              part).
        """
        if myname is None:
            myname = JID(self.me.domain)
        return StreamBase.receive(self, transport, myname)

    def fix_out_stanza(self, stanza):
        """Fix outgoing stanza.

        On a client clear the sender JID. On a server set the sender
        address to the own JID if the address is not set yet."""
        StreamBase.fix_out_stanza(self, stanza)
        if self.initiator:
            if stanza.from_jid:
                stanza.from_jid = None
        else:
            if not stanza.from_jid:
                stanza.from_jid = self.me

    def fix_in_stanza(self, stanza):
        """Fix an incoming stanza.

        Ona server replace the sender address with authorized client JID."""
        StreamBase.fix_in_stanza(self, stanza)
        if not self.initiator:
            if stanza.from_jid != self.peer:
                stanza.set_from(self.peer)

# vi: sts=4 et sw=4
