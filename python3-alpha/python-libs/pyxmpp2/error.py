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

"""XMPP error handling.

Normative reference:
  - `RFC 6120 <http://xmpp.org/rfcs/rfc6120.html>`__
  - `RFC 3920 <http://xmpp.org/rfcs/rfc3920.html>`__
"""



__docformat__ = "restructuredtext en"

import logging

from .etree import ElementTree, ElementClass
from copy import deepcopy

from .constants import STANZA_ERROR_NS, STREAM_ERROR_NS
from .constants import STREAM_QNP, STANZA_ERROR_QNP, STREAM_ERROR_QNP
from .constants import STANZA_CLIENT_QNP, STANZA_SERVER_QNP, STANZA_NAMESPACES
from .constants import XML_LANG_QNAME
from .xmppserializer import serialize

logger = logging.getLogger("pyxmpp2.error")

STREAM_ERRORS = {
            "bad-format":
                ("Received XML cannot be processed",),
            "bad-namespace-prefix":
                ("Bad namespace prefix",),
            "conflict":
                ("Closing stream because of conflicting stream being opened",),
            "connection-timeout":
                ("Connection was idle too long",),
            "host-gone":
                ("Hostname is no longer hosted on the server",),
            "host-unknown":
                ("Hostname requested is not known to the server",),
            "improper-addressing":
                ("Improper addressing",),
            "internal-server-error":
                ("Internal server error",),
            "invalid-from":
                ("Invalid sender address",),
            "invalid-namespace":
                ("Invalid namespace",),
            "invalid-xml":
                ("Invalid XML",),
            "not-authorized":
                ("Not authorized",),
            "not-well-formed":
                ("XML sent by client is not well formed",),
            "policy-violation":
                ("Local policy violation",),
            "remote-connection-failed":
                ("Remote connection failed",),
            "reset":
                ("Stream reset",),
            "resource-constraint":
                ("Remote connection failed",),
            "restricted-xml":
                ("Restricted XML received",),
            "see-other-host":
                ("Redirection required",),
            "system-shutdown":
                ("The server is being shut down",),
            "undefined-condition":
                ("Unknown error",),
            "unsupported-encoding":
                ("Unsupported encoding",),
            "unsupported-feature":
                ("Unsupported feature",),
            "unsupported-stanza-type":
                ("Unsupported stanza type",),
            "unsupported-version":
                ("Unsupported protocol version",),
    }

STREAM_ERRORS_Q = dict([( "{{{0}}}{1}".format(STREAM_ERROR_NS, x[0]), x[1])
                                            for x in list(STREAM_ERRORS.items())])

UNDEFINED_STREAM_CONDITION = \
        "{urn:ietf:params:xml:ns:xmpp-streams}undefined-condition"
UNDEFINED_STANZA_CONDITION = \
        "{urn:ietf:params:xml:ns:xmpp-stanzas}undefined-condition"

STANZA_ERRORS = {
            "bad-request":
                ("Bad request",
                "modify"),
            "conflict":
                ("Named session or resource already exists",
                "cancel"),
            "feature-not-implemented":
                ("Feature requested is not implemented",
                "cancel"),
            "forbidden":
                ("You are forbidden to perform requested action",
                "auth"),
            "gone":
                ("Recipient or server can no longer be contacted"
                                                        " at this address",
                "modify"),
            "internal-server-error":
                ("Internal server error",
                "wait"),
            "item-not-found":
                ("Item not found"
                ,"cancel"),
            "jid-malformed":
                ("JID malformed",
                "modify"),
            "not-acceptable":
                ("Requested action is not acceptable",
                "modify"),
            "not-allowed":
                ("Requested action is not allowed",
                "cancel"),
            "not-authorized":
                ("Not authorized",
                "auth"),
            "policy-violation":
                ("Policy violation",
                "cancel"),
            "recipient-unavailable":
                ("Recipient is not available",
                "wait"),
            "redirect":
                ("Redirection",
                "modify"),
            "registration-required":
                ("Registration required",
                "auth"),
            "remote-server-not-found":
                ("Remote server not found",
                "cancel"),
            "remote-server-timeout":
                ("Remote server timeout",
                "wait"),
            "resource-constraint":
                ("Resource constraint",
                "wait"),
            "service-unavailable":
                ("Service is not available",
                "cancel"),
            "subscription-required":
                ("Subscription is required",
                "auth"),
            "undefined-condition":
                ("Unknown error",
                "cancel"),
            "unexpected-request":
                ("Unexpected request",
                "wait"),
    }

STANZA_ERRORS_Q = dict([( "{{{0}}}{1}".format(STANZA_ERROR_NS, x[0]), x[1])
                                            for x in list(STANZA_ERRORS.items())])

OBSOLETE_CONDITIONS = {
            # changed between RFC 3920 and RFC 6120
            "{urn:ietf:params:xml:ns:xmpp-streams}xml-not-well-formed": 
                    "{urn:ietf:params:xml:ns:xmpp-streams}not-well-formed",
            "{urn:ietf:params:xml:ns:xmpp-streams}invalid-id": 
                                                UNDEFINED_STREAM_CONDITION,
            "{urn:ietf:params:xml:ns:xmpp-stanzas}payment-required": 
                                                UNDEFINED_STANZA_CONDITION,
}

class ErrorElement(object):
    """Base class for both XMPP stream and stanza errors
   
    :Ivariables:
        - `condition`: the condition element
        - `text`: human-readable error description
        - `custom_condition`: list of custom condition elements
        - `language`: xml:lang of the error element
    :Types:
        - `condition_name`: `str`
        - `condition`: `str`
        - `text`: `str`
        - `custom_condition`: `list` of :etree:`ElementTree.Element`
        - `language`: `str`

    """
    error_qname = "{unknown}error"
    text_qname = "{unknown}text"
    cond_qname_prefix = "{unknown}"
    def __init__(self, element_or_cond, text = None, language = None):
        """Initialize an StanzaErrorElement object.

        :Parameters:
            - `element_or_cond`: XML <error/> element to decode or an error
              condition name or element.
            - `text`: optional description to override the default one
            - `language`: RFC 3066 language tag for the description
        :Types:
            - `element_or_cond`: :etree:`ElementTree.Element` or `str`
            - `text`: `str`
            - `language`: `str`
        """
        self.text = None
        self.custom_condition = []
        self.language = language
        if isinstance(element_or_cond, str):
            self.condition = ElementTree.Element(self.cond_qname_prefix 
                                                        + element_or_cond)
        elif not isinstance(element_or_cond, ElementClass):
            raise TypeError("Element or unicode string expected")
        else:
            self._from_xml(element_or_cond)

        if text:
            self.text = text

    def _from_xml(self, element):
        """Initialize an ErrorElement object from an XML element.

        :Parameters:
            - `element`: XML element to be decoded.
        :Types:
            - `element`: :etree:`ElementTree.Element`
        """
        # pylint: disable-msg=R0912
        if element.tag != self.error_qname:
            raise ValueError("{0!r} is not a {1!r} element".format(
                                                    element, self.error_qname))
        lang = element.get(XML_LANG_QNAME, None)
        if lang:
            self.language = lang
        self.condition = None
        for child in element:
            if child.tag.startswith(self.cond_qname_prefix):
                if self.condition is not None:
                    logger.warning("Multiple conditions in XMPP error element.")
                    continue
                self.condition = deepcopy(child)
            elif child.tag == self.text_qname:
                lang = child.get(XML_LANG_QNAME, None)
                if lang:
                    self.language = lang
                self.text = child.text.strip()
            else:
                bad = False
                for prefix in (STREAM_QNP, STANZA_CLIENT_QNP, STANZA_SERVER_QNP,
                                            STANZA_ERROR_QNP, STREAM_ERROR_QNP):
                    if child.tag.startswith(prefix):
                        logger.warning("Unexpected stream-namespaced"
                                                        " element in error.")
                        bad = True
                        break
                if not bad:
                    self.custom_condition.append( deepcopy(child) )
        if self.condition is None:
            self.condition = ElementTree.Element(self.cond_qname_prefix
                                                    + "undefined-condition")
        if self.condition.tag in OBSOLETE_CONDITIONS:
            new_cond_name = OBSOLETE_CONDITIONS[self.condition.tag]
            self.condition = ElementTree.Element(new_cond_name)

    @property
    def condition_name(self):
        """Return the condition name (condition element name without the
        namespace)."""
        return self.condition.tag.split("}", 1)[1]

    def add_custom_condition(self, element):
        """Add custom condition element to the error.

        :Parameters:
            - `element`: XML element
        :Types:
            - `element`: :etree:`ElementTree.Element`

        """
        self.custom_condition.append(element)

    def serialize(self):
        """Serialize the stanza into a Unicode XML string.

        :return: serialized element.
        :returntype: `str`"""
        return serialize(self.as_xml())

    def as_xml(self):
        """Return the XML error representation.

        :returntype: :etree:`ElementTree.Element`"""
        result = ElementTree.Element(self.error_qname)
        result.append(deepcopy(self.condition))
        if self.text:
            text = ElementTree.SubElement(result, self.text_qname)
            if self.language:
                text.set(XML_LANG_QNAME, self.language)
            text.text = self.text
        return result

class StreamErrorElement(ErrorElement):
    """Stream error element."""
    error_qname = STREAM_QNP + "error"
    text_qname = STREAM_QNP + "text"
    cond_qname_prefix = STREAM_ERROR_QNP
    def __init__(self, element_or_cond, text = None, language = None):
        """Initialize an StreamErrorElement object.

        :Parameters:
            - `element_or_cond`: XML <error/> element to decode or an error
              condition name or element.
            - `text`: optional description to override the default one
            - `language`: RFC 3066 language tag for the description
        :Types:
            - `element_or_cond`: :etree:`ElementTree.Element` or `str`
            - `text`: `str`
            - `language`: `str`
        """
        if isinstance(element_or_cond, str):
            if element_or_cond not in STREAM_ERRORS:
                raise ValueError("Bad error condition")
        ErrorElement.__init__(self, element_or_cond, text, language)

    def get_message(self):
        """Get the standard English message for the error.

        :return: the error message.
        :returntype: `str`"""
        cond = self.condition_name
        if cond in STREAM_ERRORS:
            return STREAM_ERRORS[cond][0]
        else:
            return None

class StanzaErrorElement(ErrorElement):
    """Stanza error element.
    
    :Ivariables:
        - `error_type`: 'type' of the error, one of: 'auth', 'cancel',
          'continue', 'modify', 'wait'
    :Types:
        - `error_type`: `str`
    """
    error_qname = STANZA_CLIENT_QNP + "error"
    text_qname = STANZA_CLIENT_QNP + "text"
    cond_qname_prefix = STANZA_ERROR_QNP
    def __init__(self, element_or_cond, text = None, language = None,
                                                            error_type = None):
        """Initialize an StanzaErrorElement object.

        :Parameters:
            - `element_or_cond`: XML <error/> element to decode or an error
              condition name or element.
            - `text`: optional description to override the default one
            - `language`: RFC 3066 language tag for the description
            - `error_type`: 'type' of the error, one of: 'auth', 'cancel',
              'continue', 'modify', 'wait'
        :Types:
            - `element_or_cond`: :etree:`ElementTree.Element` or `str`
            - `text`: `str`
            - `language`: `str`
            - `error_type`: `str`
        """
        self.error_type = None
        if isinstance(element_or_cond, str):
            if element_or_cond not in STANZA_ERRORS:
                raise ValueError("Bad error condition")
        elif element_or_cond.tag.startswith("{"):
            namespace = element_or_cond.tag[1:].split("}", 1)[0]
            if namespace not in STANZA_NAMESPACES:
                raise ValueError("Bad error namespace {0!r}".format(namespace))
            self.error_qname = "{{{0}}}error".format(namespace)
            self.text_qname = "{{{0}}}text".format(namespace)
        else:
            raise ValueError("Bad error namespace - no namespace")
        ErrorElement.__init__(self, element_or_cond, text, language)
        if error_type is not None:
            self.error_type = error_type
        if self.condition.tag in STANZA_ERRORS_Q:
            cond = self.condition.tag
        else:
            cond = UNDEFINED_STANZA_CONDITION
        if not self.error_type:
            self.error_type = STANZA_ERRORS_Q[cond][1]

    def _from_xml(self, element):
        """Initialize an ErrorElement object from an XML element.

        :Parameters:
            - `element`: XML element to be decoded.
        :Types:
            - `element`: :etree:`ElementTree.Element`
        """
        ErrorElement._from_xml(self, element)
        error_type = element.get("type")
        if error_type:
            self.error_type = error_type
 
    def get_message(self):
        """Get the standard English message for the error.

        :return: the error message.
        :returntype: `str`"""
        cond = self.condition_name
        if cond in STANZA_ERRORS:
            return STANZA_ERRORS[cond][0]
        else:
            return None

    def as_xml(self, stanza_namespace = None): # pylint: disable-msg=W0221
        """Return the XML error representation.
        
        :Parameters:
            - `stanza_namespace`: namespace URI of the containing stanza
        :Types:
            - `stanza_namespace`: `str`
        
        :returntype: :etree:`ElementTree.Element`"""
        if stanza_namespace:
            self.error_qname = "{{{0}}}error".format(stanza_namespace)
            self.text_qname = "{{{0}}}text".format(stanza_namespace)
        result = ErrorElement.as_xml(self)
        result.set("type", self.error_type)
        return result

# vi: sts=4 et sw=4
