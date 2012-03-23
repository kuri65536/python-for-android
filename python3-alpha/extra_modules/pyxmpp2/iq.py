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

"""Iq XMPP stanza handling

Normative reference:
  - `RFC 3920 <http://www.ietf.org/rfc/rfc3920.txt>`__
"""



__docformat__ = "restructuredtext en"


from .etree import ElementClass

from .stanza import Stanza

IQ_TYPES = ("get", "set", "result", "error")

class Iq(Stanza):
    """<message /> stanza class."""
    # pylint: disable-msg=R0902
    element_name = "message"
    def __init__(self, element = None, from_jid = None, to_jid = None, 
                            stanza_type = None, stanza_id = None, 
                            error = None, error_cond=None, return_path = None,
                            language = None):
        """Initialize an `Iq` object.

        :Parameters:
            - `element`: XML element of this stanza.
            - `from_jid`: sender JID.
            - `to_jid`: recipient JID.
            - `stanza_type`: staza type: one of: "get", "set", "response"
              or "error".
            - `stanza_id`: stanza id -- value of stanza's "id" attribute. If
              not given, then unique for the session value is generated.
            - `error_cond`: error condition name. Ignored if `stanza_type` 
              is not "error".
            - `language`: default language for the stanza content
        :Types:
            - `element`: :etree:`ElementTree.Element`
            - `from_jid`: `JID`
            - `to_jid`: `JID`
            - `stanza_type`: `str`
            - `stanza_id`: `str`
            - `error`: `pyxmpp.error.StanzaErrorElement`
            - `error_cond`: `str`
            - `language`: `str`
        """
        # pylint: disable-msg=R0913

        if stanza_type is None:
            if element is None:
                raise ValueError("Missing iq type")
        elif stanza_type not in IQ_TYPES:
            raise ValueError("Bad iq type")
        
        if element is None and stanza_id is None and stanza_type in (
                                                                "get", "set"):
            stanza_id = self.gen_id()

        if element is None:
            element = "iq"
        elif not isinstance(element, ElementClass):
            raise TypeError("Couldn't make Iq from " + repr(element))
        
        Stanza.__init__(self, element, from_jid = from_jid, to_jid = to_jid,
                        stanza_type = stanza_type, stanza_id = stanza_id,
                        error = error, error_cond = error_cond, 
                        return_path = return_path, language = language)
        
        
        if self.element_name != "iq":
            raise ValueError("The element is not <iq/>")

    def copy(self):
        """Create a deep copy of the stanza.

        :returntype: `Iq`"""
        result = Iq(None, self.from_jid, self.to_jid, 
                        self.stanza_type, self.stanza_id, self.error,
                        self._return_path())
        if self._payload is None:
            self.decode_payload()
        for payload in self._payload:
            # use Stanza.add_payload to skip the payload length check
            Stanza.add_payload(result, payload)
        return result

    def make_error_response(self, cond):
        """Create error response for the a "get" or "set" iq stanza.

        :Parameters:
            - `cond`: error condition name, as defined in XMPP specification.

        :return: new `Iq` object with the same "id" as self, "from" and "to"
            attributes swapped, type="error" and containing <error /> element
            plus payload of `self`.
        :returntype: `Iq`"""

        if self.stanza_type in ("result", "error"):
            raise ValueError("Errors may not be generated for"
                                                " 'result' and 'error' iq")

        stanza = Iq(stanza_type="error", from_jid = self.to_jid, 
                        to_jid = self.from_jid, stanza_id = self.stanza_id,
                        error_cond = cond)
        if self._payload is None:
            self.decode_payload()
        for payload in self._payload:
            # use Stanza.add_payload to skip the payload length check
            Stanza.add_payload(stanza, payload)
        return stanza

    def make_result_response(self):
        """Create result response for the a "get" or "set" iq stanza.

        :return: new `Iq` object with the same "id" as self, "from" and "to"
            attributes replaced and type="result".
        :returntype: `Iq`"""

        if self.stanza_type not in ("set", "get"):
            raise ValueError("Results may only be generated for"
                                                        " 'set' or 'get' iq")
        stanza = Iq(stanza_type = "result", from_jid = self.to_jid,
                        to_jid = self.from_jid, stanza_id = self.stanza_id)
        return stanza
    
    def add_payload(self, payload):
        """Add new the stanza payload. Fails if there is already some
        payload element attached (<iq/> stanza can contain only one payload
        element)
        
        Marks the stanza dirty.

        :Parameters:
            - `payload`: XML element or stanza payload object to add
        :Types:
            - `payload`: :etree:`ElementTree.Element` or
              `interfaces.StanzaPayload`
        """
        if self._payload is None:
            self.decode_payload()
        if len(self._payload) >= 1:
            raise ValueError("Cannot add more payload to Iq stanza")
        return Stanza.add_payload(self, payload)

# vi: sts=4 et sw=4
