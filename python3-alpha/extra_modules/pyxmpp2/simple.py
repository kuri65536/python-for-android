#
# (C) Copyright 2005-2011 Jacek Konieczny <jajcus@jajcus.net>
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

"""Simple API for simple things like sendig messages.

The simplest way to send a message:

    >>> from pyxmpp2.simple import send_message
    >>> send_message("bob@example.org", "bob's password", "alice@example.org",
    ...                                                          "Hello Alice")

Please note, though:
    - this is inefficient for anything more than sending a single message,
      as a new connection is established and closed for each `send_message`
      call.
    - the default TLS settings are insecure (not peer certificate validation)
"""



__docformat__ = "restructuredtext en"

import sys

from .interfaces import EventHandler, event_handler, QUIT
from .client import Client
from .jid import JID
from .streamevents import AuthorizedEvent, DisconnectedEvent
from .message import Message
from .settings import XMPPSettings

class FireAndForget(EventHandler):
    """A minimal XMPP client that just connects to a server
    and runs single function.

    :Ivariables:
        - `action`: the function to run after the stream is authorized
        - `client`: a `Client` instance to do the rest of the job
    :Types:
        - `action`: a callable accepting a single 'client' argument
        - `client`: `pyxmpp2.client.Client`
    """
    def __init__(self, local_jid, action, settings):
        self.action = action
        self.client = Client(local_jid, [self], settings)

    def run(self):
        """Request client connection and start the main loop."""
        self.client.connect()
        self.client.run()

    def disconnect(self):
        """Request disconnection and let the main loop run for a 2 more
        seconds for graceful disconnection."""
        self.client.disconnect()
        self.client.run(timeout = 2)

    @event_handler(AuthorizedEvent)
    def handle_authorized(self, event):
        """Send the initial presence after log-in."""
        # pylint: disable=W0613
        self.action(self.client)
        self.client.disconnect()

    @event_handler(DisconnectedEvent)
    def handle_disconnected(self, event):
        """Quit the main loop upon disconnection."""
        # pylint: disable=W0613,R0201
        return QUIT
 
def send_message(source_jid, password, target_jid, body, subject = None,
                message_type = "chat", message_thread = None, settings = None):
    """Star an XMPP session and send a message, then exit.

    :Parameters:
        - `source_jid`: sender JID
        - `password`: sender password
        - `target_jid`: recipient JID
        - `body`: message body
        - `subject`: message subject
        - `message_type`: message type
        - `message_thread`: message thread id
        - `settings`: other settings
    :Types:
        - `source_jid`: `pyxmpp2.jid.JID` or `basestring`
        - `password`: `basestring`
        - `target_jid`: `pyxmpp.jid.JID` or `basestring`
        - `body`: `basestring`
        - `subject`: `basestring`
        - `message_type`: `basestring`
        - `settings`: `pyxmpp2.settings.XMPPSettings`
    """
    # pylint: disable=R0913,R0912
    if sys.version_info.major < 3:
        # pylint: disable-msg=W0404
        from locale import getpreferredencoding
        encoding = getpreferredencoding()
        if isinstance(source_jid, str):
            source_jid = source_jid.decode(encoding)
        if isinstance(password, str):
            password = password.decode(encoding)
        if isinstance(target_jid, str):
            target_jid = target_jid.decode(encoding)
        if isinstance(body, str):
            body = body.decode(encoding)
        if isinstance(message_type, str):
            message_type = message_type.decode(encoding)
        if isinstance(message_thread, str):
            message_thread = message_thread.decode(encoding)

    if not isinstance(source_jid, JID):
        source_jid = JID(source_jid)
    if not isinstance(target_jid, JID):
        target_jid = JID(target_jid)

    msg = Message(to_jid = target_jid, body = body, subject = subject,
                                                    stanza_type = message_type)
    def action(client):
        """Send a mesage `msg` via a client."""
        client.stream.send(msg)

    if settings is None:
        settings = XMPPSettings({"starttls": True, "tls_verify_peer": False})

    if password is not None:
        settings["password"] = password

    handler = FireAndForget(source_jid, action, settings)
    try:
        handler.run()
    except KeyboardInterrupt:
        handler.disconnect()
        raise

# vi: sts=4 et sw=4
