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

"""Software Version query and advertisement.

To advertise software version in your client or component add 
a `VersionProvider` instance to your payload.

To request a remote entity version information, use the
`request_software_version` function.

Normative reference:
  - `XEP-0092 <http://xmpp.org/extensions/xep-0092.html>`__
"""



__docformat__ = "restructuredtext en"

import os
import logging

from ..etree import ElementTree

from ..version import version as pyxmpp2_version # pylint: disable=E0611
from ..settings import XMPPSettings
from ..iq import Iq
from ..interfaces import XMPPFeatureHandler
from ..interfaces import iq_get_stanza_handler
from ..interfaces import StanzaPayload, payload_element_name

logger = logging.getLogger("pyxmpp2.ext.version")

_QNP = "{jabber:iq:version}"
QUERY_TAG = _QNP + "query"
NAME_TAG = _QNP + "name"
VERSION_TAG = _QNP + "version"
OS_TAG = _QNP + "os"

@payload_element_name(QUERY_TAG)
class VersionPayload(StanzaPayload):
    """Software version (XEP-0092) stanza payload.
    
    :Ivariables:
        - `name`: software name
        - `version`: software version
        - `os_name`: operating system name

    :Types:
        - `name`: `str`
        - `version`: `str`
        - `os_name`: `str`
    """
    def __init__(self, name = None, version = None, os_name = None):
        self.name = name
        self.version = version
        self.os_name = os_name

    @classmethod
    def from_xml(cls, element):
        name = None
        version = None
        os_name = None
        for child in element:
            if child.tag == NAME_TAG:
                name = child.text
            elif child.tag == VERSION_TAG:
                version = child.text
            elif child.tag == OS_TAG:
                os_name = child.text
        return cls(name, version, os_name)

    def as_xml(self):
        element = ElementTree.Element(QUERY_TAG)
        if self.name is None and self.version is None and self.os_name is None:
            return element
        sub = ElementTree.SubElement(element, NAME_TAG)
        sub.text = self.name
        sub = ElementTree.SubElement(element, VERSION_TAG)
        sub.text = self.version
        if self.os_name:
            sub = ElementTree.SubElement(element, OS_TAG)
            sub.text = self.os_name
        return element

class VersionProvider(XMPPFeatureHandler):
    """Provides the Software version (XEP-0092) service.

    Handles incoming software version queries with values from:

        - :r:`software_name setting`
        - :r:`software_version setting`
        - :r:`software_os setting`
    """
    # pylint: disable=R0903
    def __init__(self, settings = None):
        self.settings = settings if settings else XMPPSettings()

    @iq_get_stanza_handler(VersionPayload)
    def handle_version_iq_get(self, stanza):
        """Handler <iq type="get"/> for a software version query."""
        payload = VersionPayload(name = self.settings["software_name"],
                                 version = self.settings["software_version"],
                                 os_name = self.settings["software_os"]
                                 )
        response = stanza.make_result_response()
        response.set_payload(payload)
        return response

def request_software_version(stanza_processor, target_jid, callback,
                                                    error_callback = None):
    """Request software version information from a remote entity.

    When a valid response is received the `callback` will be handled
    with a `VersionPayload` instance as its only argument. The object will
    provide the requested infromation.

    In case of error stanza received or invalid response the `error_callback`
    (if provided) will be called with the offending stanza (which can
    be ``<iq type='error'/>`` or ``<iq type='result'>``) as its argument.

    The same function will be called on timeout, with the argument set to
    `None`.

    :Parameters:
        - `stanza_processor`: a object used to send the query and handle
          response. E.g. a `pyxmpp2.client.Client` instance
        - `target_jid`: the JID of the entity to query
        - `callback`: function to be called with a valid response
        - `error_callback`: function to be called on error
    :Types:
        - `stanza_processor`: `StanzaProcessor`
        - `target_jid`: `JID`
    """
    stanza = Iq(to_jid = target_jid, stanza_type = "get")
    payload = VersionPayload()
    stanza.set_payload(payload)
    def wrapper(stanza):
        """Wrapper for the user-provided `callback` that extracts the payload 
        from stanza received."""
        payload = stanza.get_payload(VersionPayload)
        if payload is None:
            if error_callback:
                error_callback(stanza)
            else:
                logger.warning("Invalid version query response.")
        else:
            callback(payload)
    stanza_processor.set_response_handlers(stanza, wrapper, error_callback)
    stanza_processor.send(stanza)

def _os_name_factory(settings):
    """Factory for the :r:`software_os setting` default.
    """
    # pylint: disable-msg=W0613,W0142
    uname = os.uname()
    return "{0} {2} {4}".format(*uname)
 
def _version_factory(settings):
    """Factory for the :r:`software_version setting` default.
    """
    # pylint: disable-msg=W0613
    if "software_name" not in settings:
        # plain version only if the default software_name is used
        return str(pyxmpp2_version)
    else:
        return "@PyXMPP2/{0}".format(pyxmpp2_version)
    
XMPPSettings.add_setting("software_name", type = str, basic = False,
    default = "PyXMPP2",
    cmdline_help = "Software name for XEP-0092 query.",
    doc = """Software name for XEP-0092 query."""
    )
XMPPSettings.add_setting("software_version", type = str, basic = False,
    factory = _version_factory,
#    default_d = "PyXMPP2 version",
    cmdline_help = "Software version for XEP-0092 query.",
    doc = """Software version for XEP-0092 query."""
    )

XMPPSettings.add_setting("software_os", type = str, basic = False,
    factory = _os_name_factory,
    default_d = "Operating system running this code",
    cmdline_help = "Operating system name for XEP-0092 query.",
    doc = """Operating system name for XEP-0092 query."""
    )

