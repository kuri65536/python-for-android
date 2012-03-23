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

"""Resource binding implementation.

Normative reference:
  - `RFC 6120 <http://xmpp.org/rfcs/rfc6120.html>`__
"""



__docformat__ = "restructuredtext en"

import logging
import uuid

from .etree import ElementTree, element_to_unicode

from .constants import BIND_QNP
from .settings import XMPPSettings
from .streamevents import BindingResourceEvent, AuthorizedEvent
from .exceptions import ResourceConstraintProtocolError, JIDError
from .exceptions import BadRequestProtocolError, FatalStreamError
from .iq import Iq
from .jid import JID
from .interfaces import XMPPFeatureHandler
from .interfaces import iq_set_stanza_handler
from .interfaces import StanzaPayload, payload_element_name
from .interfaces import StreamFeatureHandler, StreamFeatureHandled

logger = logging.getLogger("pyxmpp2.binding")


FEATURE_BIND = BIND_QNP + "bind"
BIND_JID_TAG = BIND_QNP + "jid"
BIND_RESOURCE_TAG = BIND_QNP + "resource"

@payload_element_name(FEATURE_BIND)
class ResourceBindingPayload(StanzaPayload):
    """Resource binding <iq/> stanza payload.
    
    :Ivariables:
        - `jid`: content of the <jid/> child element
        - `resource`: content of the <resource/> child element
    :Types:
        - `jid`: `JID`
        - `resource`: `str`
    """
    def __init__(self, jid = None, resource = None):
        self.jid = jid
        self.resource = resource

    @classmethod
    def from_xml(cls, element):
        jid = None
        resource = None
        for child in element:
            if child.tag == BIND_JID_TAG:
                if jid:
                    raise BadRequestProtocolError(
                                "<bind/> contains multiple <jid/> elements")
                jid = JID(child.text)
            if child.tag == BIND_RESOURCE_TAG:
                if resource:
                    raise BadRequestProtocolError(
                            "<bind/> contains multiple <resource/> elements")
                resource = child.text
        return cls(jid, resource)

    def as_xml(self):
        element = ElementTree.Element(FEATURE_BIND)
        if self.jid:
            sub = ElementTree.SubElement(element, BIND_JID_TAG)
            sub.text = str(self.jid)
        if self.resource:
            sub = ElementTree.SubElement(element, BIND_RESOURCE_TAG)
            sub.text = self.resource
        return element

class ResourceBindingHandler(StreamFeatureHandler, XMPPFeatureHandler):
    """Resource binding implementation.

    Can handle only one stream at time.

    To be used e.g. as one of the handlers passed to a client class
    constructor.
    """
    def __init__(self, settings = None):
        self.stream = None
        self.settings = settings if settings else XMPPSettings()

    def make_stream_features(self, stream, features):
        """Add resource binding feature to the <features/> element of the
        stream.

        [receving entity only]

        :returns: update <features/> element.
        """
        self.stream = stream
        if stream.peer_authenticated and not stream.peer.resource:
            ElementTree.SubElement(features, FEATURE_BIND)

    def handle_stream_features(self, stream, features):
        """Process incoming <stream:features/> element.

        [initiating entity only]

        The received features element is available in `features`.
        """
        logger.debug("Handling stream features: {0}".format(
                                        element_to_unicode(features)))
        element = features.find(FEATURE_BIND)
        if element is None:
            logger.debug("No <bind/> in features")
            return None
        resource = stream.settings["resource"]
        self.bind(stream, resource)
        return StreamFeatureHandled("Resource binding", mandatory = True)

    def bind(self, stream, resource):
        """Bind to a resource.

        [initiating entity only]

        :Parameters:
            - `resource`: the resource name to bind to.
        :Types:
            - `resource`: `str`

        XMPP stream is authenticated for bare JID only. To use
        the full JID it must be bound to a resource.
        """
        self.stream = stream
        stanza = Iq(stanza_type = "set")
        payload = ResourceBindingPayload(resource = resource)
        stanza.set_payload(payload)
        self.stanza_processor.set_response_handlers(stanza, 
                                        self._bind_success, self._bind_error)
        stream.send(stanza)
        stream.event(BindingResourceEvent(resource))

    def _bind_success(self, stanza):
        """Handle resource binding success.

        [initiating entity only]

        :Parameters:
            - `stanza`: <iq type="result"/> stanza received.

        Set `streambase.StreamBase.me` to the full JID negotiated."""
        # pylint: disable-msg=R0201
        payload = stanza.get_payload(ResourceBindingPayload)
        jid = payload.jid
        if not jid:
            raise BadRequestProtocolError("<jid/> element mising in"
                                                    " the bind response")
        self.stream.me = jid
        self.stream.event(AuthorizedEvent(self.stream.me))

    def _bind_error(self, stanza): # pylint: disable-msg=R0201,W0613
        """Handle resource binding success.

        [initiating entity only]

        :raise FatalStreamError:"""
        raise FatalStreamError("Resource binding failed")

    @iq_set_stanza_handler(ResourceBindingPayload)
    def handle_bind_iq_set(self, stanza):
        """Handler <iq type="set"/> for resource binding."""
        # pylint: disable-msg=R0201
        if not self.stream:
            logger.error("Got bind stanza before stream feature has been set")
            return False
        if self.stream.initiator:
            return False
        peer = self.stream.peer
        if peer.resource:
            raise ResourceConstraintProtocolError(
                        "Only one resource per client supported")
        resource = stanza.get_payload(ResourceBindingPayload).resource
        jid = None
        if resource:
            try:
                jid = JID(peer.local, peer.domain, resource)
            except JIDError:
                pass
        if jid is None:
            resource = str(uuid.uuid4())
            jid = JID(peer.local, peer.domain, resource)
        response = stanza.make_result_response()
        payload = ResourceBindingPayload(jid = jid)
        response.set_payload(payload)
        self.stream.peer = jid
        self.stream.event(AuthorizedEvent(jid))
        return response

def default_resource_factory(settings):
    """Factory for the 'resource' setting default: use random uuid"""
    # pylint: disable-msg=W0613
    return str(uuid.uuid4())

XMPPSettings.add_setting("resource", type = str, basic = False,
    cmdline_help = "Default JID resource",
    doc = """JID resource to bind. Use the server-provided resource if not set.
Automatically set to the resource of the JID provided to the `ClientStream`
constructor."""
    )

# vi: sts=4 et sw=4
