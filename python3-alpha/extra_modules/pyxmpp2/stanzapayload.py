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

"""XMPP payload classes."""

import logging
from collections import defaultdict

from .etree import ElementClass
from .interfaces import StanzaPayload

STANZA_PAYLOAD_CLASSES = {}
STANZA_PAYLOAD_ELEMENTS = defaultdict(list)

logger = logging.getLogger("pyxmpp2.stanzapayload")

class XMLPayload(StanzaPayload):
    """Transparent XML payload for stanza.
    
    This object can be used for any stanza payload.
    It doesn't decode the XML element, but instead keeps it in the ElementTree
    format.
    
    :Ivariables:
        - `xml_element_name`: qualified name of the wrapped element
        - `element`: the wrapped element
    :Types:
        - `xml_element_name`: `str`
        - `element`: :etree:`ElementTree.Element`
    """
    def __init__(self, data):
        if isinstance(data, StanzaPayload):
            data = data.as_xml()
        if not isinstance(data, ElementClass):
            raise TypeError("ElementTree.Element required")
        self.xml_element_name = data.tag
        self.element = data

    @classmethod
    def from_xml(cls, element):
        return cls(element)

    def as_xml(self):
        return self.element

    @property
    def handler_key(self):
        """Return `xml_element_name` as the extra key for stanza
        handlers."""
        return self.xml_element_name

def payload_class_for_element_name(element_name):
    """Return a payload class for given element name."""
    logger.debug(" looking up payload class for element: {0!r}".format(
                                                                element_name))
    logger.debug("  known: {0!r}".format(STANZA_PAYLOAD_CLASSES))
    if element_name in STANZA_PAYLOAD_CLASSES:
        return STANZA_PAYLOAD_CLASSES[element_name]
    else:
        return XMLPayload

def payload_element_names_for_class(klass):
    """Return a payload element name for given class."""
    return STANZA_PAYLOAD_ELEMENTS[klass]

def payload_factory(element):
    """Return a specialized `StanzaPayload` object for given element.
    """
    return payload_class_for_element_name(element.tag).from_xml(element)
