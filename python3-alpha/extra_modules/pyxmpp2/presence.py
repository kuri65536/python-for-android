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

"""Presence XMPP stanza handling

Normative reference:
  - `RFC 3920 <http://www.ietf.org/rfc/rfc3920.txt>`__
"""



__docformat__ = "restructuredtext en"

from .etree import ElementTree, ElementClass

from .exceptions import BadRequestProtocolError
from .stanza import Stanza

PRESENCE_TYPES = ("available", "unavailable", "probe",
                    "subscribe", "unsubscribe", "subscribed", "unsubscribed",
                    "invisible", "error")

ACCEPT_RESPONSES = {
        "subscribe": "subscribed",
        "subscribed": "subscribe",
        "unsubscribe": "unsubscribed",
        "unsubscribed": "unsubscribe",
        }

DENY_RESPONSES = {
        "subscribe": "unsubscribed",
        "subscribed": "unsubscribe",
        "unsubscribe": "subscribed",
        "unsubscribed": "subscribe",
        }

class Presence(Stanza):
    """<presence /> stanza.
    
    """
    # pylint: disable-msg=R0902,R0904
    element_name = "presence"
    def __init__(self, element = None, from_jid = None, to_jid = None,
                            stanza_type = None, stanza_id = None,
                            error = None, error_cond = None, return_path = None,
                            language = None,
                            show = None, status = None, priority = None):
        """Initialize a `Presence` object.

        :Parameters:
            - `element`: XML element 
            - `from_jid`: sender JID.
            - `to_jid`: recipient JID.
            - `stanza_type`: staza type: one of: None, "available",
              "unavailable", "subscribe", "subscribed", "unsubscribe",
              "unsubscribed" or "error". "available" is automaticaly changed to
              None.
            - `stanza_id`: stanza id -- value of stanza's "id" attribute
            - `language`: default language for the stanza content
            - `show`: "show" field of presence stanza. One of: None, "away",
              "xa", "dnd", "chat".
            - `status`: descriptive text for the presence stanza.
            - `priority`: presence priority.
            - `error_cond`: error condition name. Ignored if `stanza_type` is
              not "error"
        :Types:
            - `element`: :etree:`ElementTree.Element`
            - `from_jid`: `JID`
            - `to_jid`: `JID`
            - `stanza_type`: `str`
            - `stanza_id`: `str`
            - `language`: `str`
            - `show`: `str`
            - `status`: `str`
            - `priority`: `int`
            - `error_cond`: `str`
        """
        # pylint: disable-msg=R0913
        self._show = None
        self._status = None
        self._priority = 0
        if element is None:
            element = "presence"
        elif not isinstance(element, ElementClass):
            raise TypeError("Couldn't make Presence from " + repr(element))

        if stanza_type is not None and stanza_type not in PRESENCE_TYPES:
            raise ValueError("Bad presence type")
        elif stanza_type == 'available':
            stanza_type = None
        
        Stanza.__init__(self, element, from_jid = from_jid, to_jid = to_jid,
                        stanza_type = stanza_type, stanza_id = stanza_id,
                        error = error, error_cond = error_cond,
                        return_path = return_path, language = language)

        if self.element_name != "presence":
            raise ValueError("The element is not <presence />")

        self._show_tag = self._ns_prefix + "show"
        self._status_tag = self._ns_prefix + "status"
        self._priority_tag = self._ns_prefix + "priority"

        if self._element is not None:
            self._decode_subelements()

        if show is not None:
            self.show = show
        if status is not None:
            self.status = status
        if priority is not None:
            self.priority = priority

    def _decode_subelements(self):
        """Decode the stanza subelements."""
        for child in self._element:
            if child.tag == self._show_tag:
                self._show = child.text
            elif child.tag == self._status_tag:
                self._status = child.text
            elif child.tag == self._priority_tag:
                try:
                    self._priority = int(child.text.strip())
                    if self._priority < -128 or self._priority > 127:
                        raise ValueError
                except ValueError:
                    raise BadRequestProtocolError(
                                            "Presence priority not an integer")

    def as_xml(self):
        """Return the XML stanza representation.

        Always return an independent copy of the stanza XML representation,
        which can be freely modified without affecting the stanza.

        :returntype: :etree:`ElementTree.Element`"""
        result = Stanza.as_xml(self)
        if self._show:
            child = ElementTree.SubElement(result, self._show_tag)
            child.text = self._show
        if self._status:
            child = ElementTree.SubElement(result, self._status_tag)
            child.text = self._status
        if self._priority:
            child = ElementTree.SubElement(result, self._priority_tag)
            child.text = str(self._priority)
        return result

    def copy(self):
        """Create a deep copy of the stanza.

        :returntype: `Presence`"""
        result = Presence(None, self.from_jid, self.to_jid, 
                        self.stanza_type, self.stanza_id, self.error,
                        self._return_path(), 
                        self._show, self._status, self._priority)
        if self._payload is None:
            self.decode_payload()
        for payload in self._payload:
            result.add_payload(payload.copy())
        return result

    @property
    def show(self): # pylint: disable-msg=E0202
        """Presence status type.

        :returntype: `str`
        """
        return self._show

    @show.setter # pylint: disable-msg=E1101
    def show(self, show): # pylint: disable-msg=E0202,E0102,C0111
        self._show = str(show)
        self._dirty = True

    @property
    def status(self): # pylint: disable-msg=E0202
        """Presence status message.

        :returntype: `str`
        """
        return self._status

    @status.setter # pylint: disable-msg=E1101
    def status(self, status): # pylint: disable-msg=E0202,E0102,C0111
        self._status = str(status)
        self._dirty = True

    @property
    def priority(self): # pylint: disable-msg=E0202
        """Presence priority.

        :returntype: `str`
        """
        return self._priority

    @priority.setter # pylint: disable-msg=E1101
    def priority(self, priority): # pylint: disable-msg=E0202,E0102,C0111
        priority = int(priority)
        if priority < -128 or priority > 127:
            raise ValueError("Priority must be in the (-128, 128) range")
        self._priority = priority
        self._dirty = True

    def make_accept_response(self):
        """Create "accept" response for the "subscribe" / "subscribed" /
        "unsubscribe" / "unsubscribed" presence stanza.

        :return: new stanza.
        :returntype: `Presence`
        """
        if self.stanza_type not in ("subscribe", "subscribed",
                                                "unsubscribe", "unsubscribed"):
            raise ValueError("Results may only be generated for 'subscribe',"
                "'subscribed','unsubscribe' or 'unsubscribed' presence")
        stanza = Presence(stanza_type = ACCEPT_RESPONSES[self.stanza_type],
                            from_jid = self.to_jid, to_jid = self.from_jid,
                                                    stanza_id = self.stanza_id)
        return stanza

    def make_deny_response(self):
        """Create "deny" response for the "subscribe" / "subscribed" /
        "unsubscribe" / "unsubscribed" presence stanza.

        :return: new presence stanza.
        :returntype: `Presence`
        """
        if self.stanza_type not in ("subscribe", "subscribed",
                                                "unsubscribe", "unsubscribed"):
            raise ValueError("Results may only be generated for 'subscribe',"
                "'subscribed','unsubscribe' or 'unsubscribed' presence")
        stanza = Presence(stanza_type = DENY_RESPONSES[self.stanza_type],
                            from_jid = self.to_jid, to_jid = self.from_jid,
                                                    stanza_id = self.stanza_id)
        return stanza

    def make_error_response(self, cond):
        """Create error response for the any non-error presence stanza.

        :Parameters:
            - `cond`: error condition name, as defined in XMPP specification.
        :Types:
            - `cond`: `str`

        :return: new presence stanza.
        :returntype: `Presence`
        """
        
        if self.stanza_type == "error":
            raise ValueError("Errors may not be generated in response"
                                                                " to errors")

        stanza = Presence(stanza_type = "error", from_jid = self.from_jid,
                            to_jid = self.to_jid, stanza_id = self.stanza_id,
                            status = self._status, show = self._show,
                            priority = self._priority, error_cond = cond)

        if self._payload is None:
            self.decode_payload()

        for payload in self._payload:
            stanza.add_payload(payload)

        return stanza

# vi: sts=4 et sw=4
