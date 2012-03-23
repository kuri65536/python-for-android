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

"""IM Session establishement implementation.

This module provides a stream feature handler to implement the
IM session establishment request defined in :RFC:`3921`, but dropped
in :RFC:`6120`. The implementation is needed for backward compatibility.

Normative reference:
  - :RFC:`3921`
  - :RFC:`6120` (Appendix E. states it should be no-op now, when implemented
    on server side)
"""



__docformat__ = "restructuredtext en"

import logging

from .etree import ElementTree

from .constants import SESSION_QNP
from .streamevents import AuthorizedEvent
from .exceptions import FatalStreamError
from .stanzapayload import XMLPayload
from .iq import Iq
from .interfaces import XMPPFeatureHandler
from .interfaces import iq_set_stanza_handler
from .interfaces import StreamFeatureHandler
from .interfaces import EventHandler, event_handler

logger = logging.getLogger("pyxmpp2.session")

SESSION_TAG = SESSION_QNP + "session"

class SessionHandler(StreamFeatureHandler, XMPPFeatureHandler, EventHandler):
    """:RFC:`3921` session establishment implementation.

    """
    def __init__(self):
        """Initialize the SASL handler"""
        super(SessionHandler, self).__init__()

    def make_stream_features(self, stream, features):
        established = getattr(stream, "_session_established", False)
        if stream.peer_authenticated and not established:
            ElementTree.SubElement(features, SESSION_TAG)

    def handle_stream_features(self, stream, features):
        pass

    @event_handler(AuthorizedEvent)
    def handle_authorized(self, event):
        """Send session esteblishment request if the feature was advertised by
        the server.
        """
        stream = event.stream
        if not stream:
            return
        if not stream.initiator:
            return
        if stream.features is None:
            return
        element = stream.features.find(SESSION_TAG)
        if element is None:
            return
        logger.debug("Establishing IM session")
        stanza = Iq(stanza_type = "set")
        payload = XMLPayload(ElementTree.Element(SESSION_TAG))
        stanza.set_payload(payload)
        self.stanza_processor.set_response_handlers(stanza, 
                                        self._session_success,
                                        self._session_error)
        stream.send(stanza)

    def _session_success(self, stanza):
        """Handle session establishment success.

        [initiating entity only]

        :Parameters:
            - `stanza`: <iq type="result"/> stanza received.

        """
        # pylint: disable-msg=R0201,W0613
        logger.debug("Session established")

    def _session_error(self, stanza): # pylint: disable-msg=R0201,W0613
        """Handle resource session establishment error.

        [initiating entity only]

        :raise FatalStreamError:"""
        raise FatalStreamError("Session establishment failed")

    @iq_set_stanza_handler(XMLPayload, SESSION_TAG)
    def handle_bind_iq_set(self, stanza):
        """Handler <iq type="set"/> for session establishment."""
        # pylint: disable-msg=R0201
        logger.debug("Accepting session establishment request.")
        return stanza.make_result_response()

# vi: sts=4 et sw=4
