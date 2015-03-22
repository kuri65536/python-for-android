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

"""General XMPP Stanza handling.

Normative reference:
  - `RFC 6120 <http://www.ietf.org/rfc/rfc6120.txt>`__
"""



__docformat__ = "restructuredtext en"

from .etree import ElementTree, ElementClass
import random
import weakref

from .exceptions import BadRequestProtocolError, JIDMalformedProtocolError
from .jid import JID
from .stanzapayload import XMLPayload, payload_factory
from .stanzapayload import payload_class_for_element_name
from .xmppserializer import serialize
from .constants import STANZA_NAMESPACES, STANZA_CLIENT_NS, XML_LANG_QNAME
from .error import StanzaErrorElement
from .interfaces import StanzaPayload

random.seed()

class Stanza(object):
    """Base class for all XMPP stanzas.

    :Ivariables:
        - `_payload`: the stanza payload
        - `_error`: error associated a stanza of type "error"
        - `_namespace`: namespace of this stanza element
        - `_return_path`: weak reference to the return route object
    :Types:
        - `_payload`: `list` of (`str`, `StanzaPayload`) 
        - `_error`: `pyxmpp2.error.StanzaErrorElement`
        - `_namespace`: `str`
        - `_return_path`: weakref to `StanzaRoute`
    """
    # pylint: disable-msg=R0902
    element_name = "Unknown"
    def __init__(self, element, from_jid = None, to_jid = None,
                            stanza_type = None, stanza_id = None,
                            error = None, error_cond = None,
                            return_path = None, language = None): 
        """Initialize a Stanza object.

        :Parameters:
            - `element`: XML element of this stanza, or element name for a new
              stanza. If element is given it must not be modified later,
              unless `decode_payload()` and `mark_dirty()` methods are called
              first (the element changes won't affec the stanza then).
            - `from_jid`: sender JID.
            - `to_jid`: recipient JID.
            - `stanza_type`: staza type: one of: "get", "set", "result" or
              "error".
            - `stanza_id`: stanza id -- value of stanza's "id" attribute. If
              not given, then unique for the session value is generated.
            - `error`: error object. Ignored if `stanza_type` is not "error".
            - `error_cond`: error condition name. Ignored if `stanza_type` is
              not "error" or `error` is not None.
            - `return_path`: route for sending responses to this stanza. Will
              be weakly referenced.
            - `language`: default language for the stanza content
        :Types:
            - `element`: `str` or :etree:`ElementTree.Element`
            - `from_jid`: `JID`
            - `to_jid`: `JID`
            - `stanza_type`: `str`
            - `stanza_id`: `str`
            - `error`: `pyxmpp.error.StanzaErrorElement`
            - `error_cond`: `str`
            - `return_path`: `StanzaRoute`
            - `language`: `str`
        """
        # pylint: disable-msg=R0913
        self._error = None
        self._from_jid = None
        self._to_jid = None
        self._stanza_type = None
        self._stanza_id = None
        self._language = language
        if isinstance(element, ElementClass):
            self._element = element
            self._dirty = False
            self._decode_attributes()
            if not element.tag.startswith("{"):
                raise ValueError("Element has no namespace")
            else:
                self._namespace, self.element_name = element.tag[1:].split("}")
                if self._namespace not in STANZA_NAMESPACES:
                    raise BadRequestProtocolError("Wrong stanza namespace")
            self._payload = None
        else:
            self._element = None
            self._dirty = True
            self.element_name = str(element)
            self._namespace = STANZA_CLIENT_NS
            self._payload = []

        self._ns_prefix = "{{{0}}}".format(self._namespace)
        self._element_qname = self._ns_prefix + self.element_name

        if from_jid is not None:
            self.from_jid = from_jid

        if to_jid is not None:
            self.to_jid = to_jid

        if stanza_type:
            self.stanza_type = stanza_type

        if stanza_id:
            self.stanza_id = stanza_id

        if self.stanza_type == "error":
            if error:
                self._error = StanzaErrorElement(error)
            elif error_cond:
                self._error = StanzaErrorElement(error_cond)
            else:
                self._decode_error()

        if return_path is not None:
            self._return_path = weakref.ref(return_path)
    
    def _decode_attributes(self):
        """Decode attributes of the stanza XML element
        and put them into the stanza properties."""
        try:
            from_jid = self._element.get('from')
            if from_jid:
                self._from_jid = JID(from_jid)
            to_jid = self._element.get('to')
            if to_jid:
                self._to_jid = JID(to_jid)
        except ValueError:
            raise JIDMalformedProtocolError
        self._stanza_type = self._element.get('type')
        self._stanza_id = self._element.get('id')
        lang = self._element.get(XML_LANG_QNAME)
        if lang:
            self._language = lang

    def _decode_error(self):
        """Decode error element of the stanza."""
        error_qname = self._ns_prefix + "error"
        for child in self._element:
            if child.tag == error_qname:
                self._error = StanzaErrorElement(child)
                return
        raise BadRequestProtocolError("Error element missing in"
                                                            " an error stanza")

    def copy(self):
        """Create a deep copy of the stanza.

        :returntype: `Stanza`"""
        result = Stanza(self.element_name, self.from_jid, self.to_jid, 
                        self.stanza_type, self.stanza_id, self.error,
                        self._return_path())
        if self._payload is None:
            self.decode_payload()
        for payload in self._payload:
            result.add_payload(payload.copy())
        return result

    def serialize(self):
        """Serialize the stanza into a Unicode XML string.

        :return: serialized stanza.
        :returntype: `str`"""
        return serialize(self.get_xml())

    def as_xml(self):
        """Return the XML stanza representation.

        Always return an independent copy of the stanza XML representation,
        which can be freely modified without affecting the stanza.

        :returntype: :etree:`ElementTree.Element`"""
        attrs = {}
        if self._from_jid:
            attrs['from'] = str(self._from_jid)
        if self._to_jid:
            attrs['to'] = str(self._to_jid)
        if self._stanza_type:
            attrs['type'] = self._stanza_type
        if self._stanza_id:
            attrs['id'] = self._stanza_id
        if self._language:
            attrs[XML_LANG_QNAME] = self._language
        element = ElementTree.Element(self._element_qname, attrs)
        if self._payload is None:
            self.decode_payload()
        for payload in self._payload:
            element.append(payload.as_xml())
        if self._error:
            element.append(self._error.as_xml(
                                        stanza_namespace = self._namespace))
        return element

    def get_xml(self):
        """Return the XML stanza representation.

        This returns the original or cached XML representation, which
        may be much more efficient than `as_xml`. 
        
        Result of this function should never be modified.

        :returntype: :etree:`ElementTree.Element`"""
        if not self._dirty:
            return self._element
        element = self.as_xml()
        self._element = element
        self._dirty = False
        return element

    def decode_payload(self, specialize = False):
        """Decode payload from the element passed to the stanza constructor.

        Iterates over stanza children and creates StanzaPayload objects for
        them. Called automatically by `get_payload()` and other methods that
        access the payload.
        
        For the `Stanza` class stanza namespace child elements will also be
        included as the payload. For subclasses these are no considered
        payload."""
        if self._payload is not None:
            # already decoded
            return
        if self._element is None:
            raise ValueError("This stanza has no element to decode""")
        payload = []
        if specialize:
            factory = payload_factory
        else:
            factory = XMLPayload
        for child in self._element:
            if self.__class__ is not Stanza:
                if child.tag.startswith(self._ns_prefix):
                    continue
            payload.append(factory(child))
        self._payload = payload

    @property
    def from_jid(self): # pylint: disable-msg=E0202
        """Source JID of the stanza.

        :returntype: `JID`
        """
        return self._from_jid

    @from_jid.setter # pylint: disable-msg=E1101
    def from_jid(self, from_jid): # pylint: disable-msg=E0202,E0102,C0111
        if from_jid is None:
            self._from_jid = None
        else:
            self._from_jid = JID(from_jid)
        self._dirty = True

    @property
    def to_jid(self): # pylint: disable-msg=E0202
        """Destination JID of the stanza.

        :returntype: `JID`
        """
        return self._to_jid

    @to_jid.setter # pylint: disable-msg=E1101
    def to_jid(self, to_jid): # pylint: disable-msg=E0202,E0102,C0111
        if to_jid is None:
            self._to_jid = None
        else:
            self._to_jid = JID(to_jid)
        self._dirty = True

    @property
    def stanza_type(self): # pylint: disable-msg=C0111,E0202
        """Stanza type, one of: "get", "set", "result" or "error".

        :returntype: `str`
        """
        return self._stanza_type

    @stanza_type.setter # pylint: disable-msg=E1101
    def stanza_type(self, stanza_type): # pylint: disable-msg=E0202,E0102,C0111
        self._stanza_type = str(stanza_type)
        self._dirty = True

    @property
    def stanza_id(self): # pylint: disable-msg=C0111,E0202
        """Stanza id.

        :returntype: `str`
        """
        return self._stanza_id

    @stanza_id.setter # pylint: disable-msg=E1101
    def stanza_id(self, stanza_id): # pylint: disable-msg=E0202,E0102,C0111
        self._stanza_id = str(stanza_id)
        self._dirty = True

    @property
    def error(self): # pylint: disable-msg=E0202
        """Stanza error element.

        :returntype: `StanzaErrorElement`
        """
        return self._error

    @error.setter # pylint: disable-msg=E1101
    def error(self, error): # pylint: disable-msg=E0202,E0102,C0111
        self._error = error
        self._dirty = True

    @property
    def return_path(self): # pylint: disable-msg=E0202
        """Stream the stanza was received from.

        :returntype: `StanzaRoute`
        """
        return self._return_path()

    def mark_dirty(self):
        """Mark the stanza 'dirty' so the XML representation will be
        re-built the next time it is requested.
        
        This should be called each time the payload attached to the stanza is
        modifed."""
        self._dirty = True

    def set_payload(self, payload):
        """Set stanza payload to a single item. 
        
        All current stanza content of will be dropped.
        Marks the stanza dirty.

        :Parameters:
            - `payload`: XML element or stanza payload object to use
        :Types:
            - `payload`: :etree:`ElementTree.Element` or `StanzaPayload`
        """
        if isinstance(payload, ElementClass):
            self._payload = [ XMLPayload(payload) ]
        elif isinstance(payload, StanzaPayload):
            self._payload = [ payload ]
        else:
            raise TypeError("Bad payload type")
        self._dirty = True

    def add_payload(self, payload):
        """Add new the stanza payload.
        
        Marks the stanza dirty.

        :Parameters:
            - `payload`: XML element or stanza payload object to add
        :Types:
            - `payload`: :etree:`ElementTree.Element` or `StanzaPayload`
        """
        if self._payload is None:
            self.decode_payload()
        if isinstance(payload, ElementClass):
            self._payload.append(XMLPayload(payload))
        elif isinstance(payload, StanzaPayload):
            self._payload.append(payload)
        else:
            raise TypeError("Bad payload type")
        self._dirty = True

    def get_all_payload(self, specialize = False):
        """Return list of stanza payload objects.

        :Parameters:
            - `specialize`: If `True`, then return objects of specialized
              `StanzaPayload` classes whenever possible, otherwise the
              representation already available will be used (often
              `XMLPayload`)
       
        :Returntype: `list` of `StanzaPayload`
        """
        if self._payload is None:
            self.decode_payload(specialize)
        elif specialize:
            for i, payload in enumerate(self._payload):
                if isinstance(payload, XMLPayload):
                    klass = payload_class_for_element_name(
                                                        payload.element.tag)
                    if klass is not XMLPayload:
                        payload = klass.from_xml(payload.element)
                        self._payload[i] = payload
        return list(self._payload)

    def get_payload(self, payload_class, payload_key = None,
                                                        specialize = False):
        """Get the first payload item matching the given class
        and optional key.

        Payloads may be addressed using a specific payload class or 
        via the generic `XMLPayload` element, though the `XMLPayload`
        representation is available only as long as the element is not
        requested by a more specific type.

        :Parameters:
            - `payload_class`: requested payload class, a subclass of
              `StanzaPayload`. If `None` get the first payload in whatever
              class is available.
            - `payload_key`: optional key for additional match. When used
              with `payload_class` = `XMLPayload` this selects the element to
              match
            - `specialize`: If `True`, and `payload_class` is `None` then
              return object of a specialized `StanzaPayload` subclass whenever
              possible
        :Types:
            - `payload_class`: `StanzaPayload`
            - `specialize`: `bool`
      
        :Return: payload element found or `None`
        :Returntype: `StanzaPayload`
        """
        if self._payload is None:
            self.decode_payload()
        if payload_class is None:
            if self._payload:
                payload = self._payload[0]
                if specialize and isinstance(payload, XMLPayload):
                    klass = payload_class_for_element_name(
                                                        payload.element.tag)
                    if klass is not XMLPayload:
                        payload = klass.from_xml(payload.element)
                        self._payload[0] = payload
                return payload
            else:
                return None
        # pylint: disable=W0212
        elements = payload_class._pyxmpp_payload_element_name
        for i, payload in enumerate(self._payload):
            if isinstance(payload, XMLPayload):
                if payload_class is not XMLPayload:
                    if payload.xml_element_name not in elements:
                        continue
                    payload = payload_class.from_xml(payload.element)
            elif not isinstance(payload, payload_class):
                continue
            if payload_key is not None and payload_key != payload.handler_key():
                continue
            self._payload[i] = payload
            return payload
        return None

    last_id = random.randrange(1000000)

    @classmethod
    def gen_id(cls):
        """Generate stanza id unique for the session.

        :return: the new id."""
        cls.last_id += 1
        return str(cls.last_id)

# vi: sts=4 et sw=4
