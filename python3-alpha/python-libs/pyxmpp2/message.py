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

"""Message XMPP stanza handling

Normative reference:
  - `RFC 3920 <http://www.ietf.org/rfc/rfc3920.txt>`__
"""



__docformat__ = "restructuredtext en"

from .etree import ElementTree, ElementClass
from .stanza import Stanza

MESSAGE_TYPES = ("normal", "chat", "headline", "error", "groupchat")

class Message(Stanza):
    """<message /> stanza class.
    """
    # pylint: disable-msg=R0902,R0904
    element_name = "message"
    def __init__(self, element = None, from_jid = None, to_jid = None,
                            stanza_type = None, stanza_id = None,
                            error = None, error_cond = None, return_path = None,
                            language = None,
                            subject = None, body = None, thread = None):
        """Initialize a `Message` object.

        :Parameters:
            - `element`: XML element of this stanza.
            - `from_jid`: sender JID.
            - `to_jid`: recipient JID.
            - `stanza_type`: staza type: one of: "normal", "chat", "headline",
              "error", "groupchat"
            - `stanza_id`: stanza id -- value of stanza's "id" attribute. If
              not given, then unique for the session value is generated.
            - `error_cond`: error condition name. Ignored if `stanza_type` 
              is not "error".
            - `language`: default language for the stanza content
            - `subject`: message subject,
            - `body`: message body.
            - `thread`: message thread id.
        :Types:
            - `element`: :etree:`ElementTree.Element`
            - `from_jid`: `JID`
            - `to_jid`: `JID`
            - `stanza_type`: `str`
            - `stanza_id`: `str`
            - `error`: `pyxmpp.error.StanzaErrorElement`
            - `error_cond`: `str`
            - `subject`: `str`
            - `body`: `str`
            - `thread`: `str`
            - `language`: `str`
        """
        # pylint: disable-msg=R0913
        self._subject = None
        self._body = None
        self._thread = None
        if element is None:
            element = "message"
        elif not isinstance(element, ElementClass):
            raise TypeError("Couldn't make Message from " + repr(element))

        Stanza.__init__(self, element, from_jid = from_jid, to_jid = to_jid,
                        stanza_type = stanza_type, stanza_id = stanza_id,
                        error = error, error_cond = error_cond,
                        return_path = return_path, language = language)

        if self.element_name != "message":
            raise ValueError("The element is not <message/>")

        self._subject_tag = self._ns_prefix + "subject"
        self._body_tag = self._ns_prefix + "body"
        self._thread_tag = self._ns_prefix + "thread"

        if self._element is not None:
            self._decode_subelements()

        if subject is not None:
            self.subject = subject
        if body is not None:
            self.body = body
        if thread is not None:
            self.thread = thread

    def _decode_subelements(self):
        """Decode the stanza subelements."""
        for child in self._element:
            if child.tag == self._subject_tag:
                self._subject = child.text
            elif child.tag == self._body_tag:
                self._body = child.text
            elif child.tag == self._thread_tag:
                self._thread = child.text

    def as_xml(self):
        """Return the XML stanza representation.

        Always return an independent copy of the stanza XML representation,
        which can be freely modified without affecting the stanza.

        :returntype: :etree:`ElementTree.Element`"""
        result = Stanza.as_xml(self)
        if self._subject:
            child = ElementTree.SubElement(result, self._subject_tag)
            child.text = self._subject
        if self._body:
            child = ElementTree.SubElement(result, self._body_tag)
            child.text = self._body
        if self._thread:
            child = ElementTree.SubElement(result, self._thread_tag)
            child.text = self._thread
        return result

    def copy(self):
        """Create a deep copy of the stanza.

        :returntype: `Message`"""
        result = Message(None, self.from_jid, self.to_jid, 
                        self.stanza_type, self.stanza_id, self.error,
                        self._return_path(), self._subject, self._body,
                                                            self._thread)
        for payload in self._payload:
            result.add_payload(payload.copy())
        return result

    @property
    def subject(self): # pylint: disable-msg=E0202
        """Message subject.

        :Returntype: `str`
        """
        return self._subject

    @subject.setter # pylint: disable-msg=E1101
    def subject(self, subject): # pylint: disable-msg=E0202,E0102,C0111
        self._subject = str(subject)
        self._dirty = True

    @property
    def body(self): # pylint: disable-msg=E0202
        """Message body.

        :Returntype: `str`
        """
        return self._body

    @body.setter # pylint: disable-msg=E1101
    def body(self, body): # pylint: disable-msg=E0202,E0102,C0111
        self._body = str(body)
        self._dirty = True

    @property
    def thread(self): # pylint: disable-msg=E0202
        """Thread id.

        :Returntype: `str`
        """
        return self._thread

    @thread.setter # pylint: disable-msg=E1101
    def thread(self, thread): # pylint: disable-msg=E0202,E0102,C0111
        self._thread = str(thread)
        self._dirty = True

    def make_error_response(self, cond):
        """Create error response for any non-error message stanza.

        :Parameters:
            - `cond`: error condition name, as defined in XMPP specification.

        :return: new message stanza with the same "id" as self, "from" and
            "to" attributes swapped, type="error" and containing <error />
            element plus payload of `self`.
        :returntype: `Message`"""

        if self.stanza_type == "error":
            raise ValueError("Errors may not be generated in response"
                                                                " to errors")

        msg = Message(stanza_type = "error", from_jid = self.to_jid, 
                        to_jid = self.from_jid, stanza_id = self.stanza_id,
                        error_cond = cond,
                        subject = self._subject, body = self._body,
                        thread = self._thread)

        if self._payload is None:
            self.decode_payload()
        for payload in self._payload:
            msg.add_payload(payload.copy())

        return msg

# vi: sts=4 et sw=4
