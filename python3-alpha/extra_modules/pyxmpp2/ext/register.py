#
# (C) Copyright 2005-2010 Jacek Konieczny <jajcus@jajcus.net>
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

"""In-band registration (jabber:iq:register) handling.

Normative reference:
  - `JEP 77 <http://www.jabber.org/jeps/jep-0077.html>`__
"""



__docformat__="restructuredtext en"

raise ImportError("{0} is not yet rewritten for PyXMPP2".format(__name__))

import libxml2
import logging

from ..utils import to_utf8,from_utf8
from ..xmlextra import get_node_ns_uri
from ..objects import StanzaPayloadObject
from ..xmlextra import xml_element_iter

from .dataforms import DATAFORM_NS, Form

REGISTER_NS="jabber:iq:register"

legacy_fields = {
        "username": ("text-single", "Account name associated with the user"),
        "nick": ("text-single", "Familiar name of the user"),
        "password": ("text-private", "Password or secret for the user"),
        "name": ("text-single", "Full name of the user"),
        "first": ("text-single", "First name or given name of the user"),
        "last": ("text-single", "Last name, surname, or family name of the user"),
        "email": ("text-single", "Email address of the user"),
        "address": ("text-single", "Street portion of a physical or mailing address"),
        "city": ("text-single", "Locality portion of a physical or mailing address"),
        "state": ("text-single", "Region portion of a physical or mailing address"),
        "zip": ("text-single", "Postal code portion of a physical or mailing address"),
        "phone": ("text-single", "Telephone number of the user"),
        "url": ("text-single", "URL to web page describing the user"),
        "date": ("text-single", "Some date (e.g., birth date, hire date, sign-up date)"),
        "misc": ("text-single", "Free-form text field (obsolete)"),
        "text": ("text-single", "Free-form text field (obsolete)"),
        "key": ("text-single", "Session key for transaction (obsolete)"),
        }

class Register(StanzaPayloadObject):
    """
    Delayed delivery tag.

    Represents 'jabber:iq:register' (JEP-0077) element of a Jabber <iq/> stanza.

    Please note that it is recommended to use `get_form` and `submit_form` records
    instead of accessing the `form` and legacy fields directly. This way both
    legacy and Data Forms registration would work transparently to the application.

    :Ivariables:
        - `form`: registration form (when available)
        - `registered`: `True` if entity is already registered
        - `instrutions`: Registration instructions (legacy protocol)
        - `username`: Username field (legacy protocol)
        - `nick`: Nickname (legacy protocol)
        - `password`: Password (legacy protocol)
        - `name`: Name field (legacy protocol)
        - `first`: First name field (legacy protocol)
        - `last`: Last name field (legacy protocol)
        - `email`: E-mail field (legacy protocol)
        - `address`: Address field (legacy protocol)
        - `city`: City field (legacy protocol)
        - `state`: State field (legacy protocol)
        - `zip`: ZIP code field (legacy protocol)
        - `phone`: Phone field (legacy protocol)
        - `url`: URL field (legacy protocol)
        - `date`: Date field (legacy protocol)
        - `misc`: Misc field (legacy protocol, obsolete)
        - `text`: Text field (legacy protocol, obsolete)
        - `key`: Key field (legacy protocol, obsolete)
        - `remove`: `True` when the account should be removed
    :Types:
        - `form`: `pyxmpp.jabber.dataforms.Form`
        - `registered`: `bool`
        - `instrutions`: `str`
        - `username`: `str`
        - `nick`: `str`
        - `password`: `str`
        - `name`: `str`
        - `first`: `str`
        - `last`: `str`
        - `email`: `str`
        - `address`: `str`
        - `city`: `str`
        - `state`: `str`
        - `zip`: `str`
        - `phone`: `str`
        - `url`: `str`
        - `date`: `str`
        - `misc`: `str`
        - `text`: `str`
        - `key`: `str`
        - `remove`: `True` when the account should be removed
    """

    xml_element_name = "query"
    xml_element_namespace = REGISTER_NS

    def __init__(self, xmlnode = None):
        """
        Initialize the `Register` object.

        :Parameters:
            - `xmlnode`: an optional XML node to parse.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`
        """
        self.__logger=logging.getLogger("pyxmpp2.jabber.Register")
        self.form = None
        self.registered = False
        self.instructions = None
        self.remove = False
        for f in legacy_fields:
            setattr(self, f, None)
        if isinstance(xmlnode,libxml2.xmlNode):
            self.__from_xml(xmlnode)

    def __from_xml(self, xmlnode):
        """Initialize `Register` from an XML node.

        :Parameters:
            - `xmlnode`: the jabber:x:register XML element.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`"""

        self.__logger.debug("Converting jabber:iq:register element from XML")
        if xmlnode.type!="element":
            raise ValueError("XML node is not a jabber:iq:register element (not an element)")
        ns=get_node_ns_uri(xmlnode)
        if ns and ns!=REGISTER_NS or xmlnode.name!="query":
            raise ValueError("XML node is not a jabber:iq:register element")

        for element in xml_element_iter(xmlnode.children):
            ns = get_node_ns_uri(element)
            if ns == DATAFORM_NS and element.name == "x" and not self.form:
                self.form = Form(element)
            elif ns != REGISTER_NS:
                continue
            name = element.name
            if name == "instructions" and not self.instructions:
                self.instructions = from_utf8(element.getContent())
            elif name == "registered":
                self.registered = True
            elif name == "remove":
                self.remove = True
            elif name in legacy_fields and not getattr(self, name):
                value = from_utf8(element.getContent())
                if value is None:
                    value = ""
                self.__logger.debug("Setting legacy field %r to %r" % (name, value))
                setattr(self, name, value)

    def complete_xml_element(self, xmlnode, doc):
        """Complete the XML node with `self` content.

        :Parameters:
            - `xmlnode`: XML node with the element being built. It has already
              right name and namespace, but no attributes or content.
            - `doc`: document to which the element belongs.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`
            - `doc`: `libxml2.xmlDoc`"""
        ns = xmlnode.ns()
        if self.instructions is not None:
            xmlnode.newTextChild(ns, "instructions", to_utf8(self.instructions))
        if self.form:
            self.form.as_xml(xmlnode, doc)
        if self.remove:
            xmlnode.newChild(ns, "remove", None)
        else:
            if self.registered:
                xmlnode.newChild(ns, "registered", None)
            for field in legacy_fields:
                value = getattr(self, field)
                if value is not None:
                    xmlnode.newTextChild(ns, field, to_utf8(value))

    def get_form(self, form_type = "form"):
        """Return Data Form for the `Register` object.

        Convert legacy fields to a data form if `self.form` is `None`, return `self.form` otherwise.

        :Parameters:
            - `form_type`: If "form", then a form to fill-in should be
              returned. If "sumbit", then a form with submitted data.
        :Types:
            - `form_type`: `str`

        :return: `self.form` or a form created from the legacy fields
        :returntype: `pyxmpp.jabber.dataforms.Form`"""

        if self.form:
            if self.form.type != form_type:
                raise ValueError("Bad form type in the jabber:iq:register element")
            return self.form

        form = Form(form_type, instructions = self.instructions)
        form.add_field("FORM_TYPE", ["jabber:iq:register"], "hidden")
        for field in legacy_fields:
            field_type, field_label = legacy_fields[field]
            value = getattr(self, field)
            if value is None:
                continue
            if form_type == "form":
                if not value:
                    value = None
                form.add_field(name = field, field_type = field_type, label = field_label,
                        value = value, required = True)
            else:
                form.add_field(name = field, value = value)
        return form

    def submit_form(self, form):
        """Make `Register` object for submitting the registration form.

        Convert form data to legacy fields if `self.form` is `None`.

        :Parameters:
            - `form`: The form to submit. Its type doesn't have to be "submit"
              (a "submit" form will be created here), so it could be the form
              obtained from `get_form` just with the data entered.

        :return: new registration element
        :returntype: `Register`"""

        result = Register()
        if self.form:
            result.form = form.make_submit()
            return result

        if "FORM_TYPE" not in form or "jabber:iq:register" not in form["FORM_TYPE"].values:
            raise ValueError("FORM_TYPE is not jabber:iq:register")

        for field in legacy_fields:
            self.__logger.debug("submitted field %r" % (field, ))
            value = getattr(self, field)
            try:
                form_value = form[field].value
            except KeyError:
                if value:
                    raise ValueError("Required field with no value!")
                continue
            setattr(result, field, form_value)

        return result


# vi: sts=4 et sw=4
