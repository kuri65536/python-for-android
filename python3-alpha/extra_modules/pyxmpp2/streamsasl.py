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
# pylint: disable-msg=W0201

"""SASL support XMPP streams.

Normative reference:
  - `RFC 6120 <http://www.ietf.org/rfc/rfc3920.txt>`__
"""



__docformat__ = "restructuredtext en"

import base64
import logging
from .etree import ElementTree, element_to_unicode

from .jid import JID
from . import sasl
from .exceptions import SASLNotAvailable, FatalStreamError
from .exceptions import SASLMechanismNotAvailable, SASLAuthenticationFailed
from .constants import SASL_QNP
from .settings import XMPPSettings
from .interfaces import StreamFeatureHandler
from .interfaces import StreamFeatureHandled, StreamFeatureNotHandled
from .interfaces import stream_element_handler

logger = logging.getLogger("pyxmpp2.streamsasl")

class DefaultPasswordManager(sasl.PasswordManager):
    """Default password manager."""
    def __init__(self, settings):
        self.settings = settings
        self.stream = None

    def set_stream(self, stream):
        """Set a stream associated with this password manager.

        :Parameters:
            - `stream`: the stream object
        :Types:
            - `stream`: `StreamBase`
        """
        self.stream = stream

    def get_password(self, username, realm = None, acceptable_formats = (
                                                                    "plain",)):
        """Get the password for user authentication.

        [both client or server]

        If stream initiator: return the value of the "password" setting
        if `username` patches the "username" setting or local jid localpart.

        If stream receiver - lookup the password in the "user_passwords"
        setting.

        :Parameters:
            - `username`: the username for which the password is requested.
            - `realm`: the authentication realm for which the password is
              requested.
            - `acceptable_formats`: a sequence of acceptable formats of the
              password data. Could be "plain", "md5:user:realm:password" or any
              other mechanism-specific encoding. This allows non-plain-text
              storage of passwords. But only "plain" format will work with
              all password authentication mechanisms.
        :Types:
            - `username`: `str`
            - `realm`: `str`
            - `acceptable_formats`: sequence of `str`

        :return: the password and its encoding (format).
        :returntype: `str`,`str` tuple."""
        _unused = realm
        if "plain" not in acceptable_formats:
            return
        stream = self.stream
        if stream:
            if stream.initiator:
                our_name = self.settings.get("username")
                if our_name is None and self.stream and self.stream.me:
                    our_name = self.stream.me.local
                if our_name == username:
                    password = self.settings["password"]
                else:
                    password = None
            else:
                try:
                    password = self.settings["user_passwords"].get(username)
                except KeyError:
                    password = None
        else:
            password = self.settings["password"]
        if password is not None:
            return password, "plain"
        else:
            return None, None

    def check_authzid(self, authzid, extra_info = None):
        """Check authorization id provided by the client.

        [server only]

        Allow only no authzid or authzid equal to current username@domain

        :Parameters:
            - `authzid`: authorization id provided.
            - `extra_info`: additional information about the user
              from the authentication backend. This mapping will
              usually contain at least 'username' item.
        :Types:
            - `authzid`: `str`
            - `extra_info`: mapping

        :return: `True` if user is authorized to use that `authzid`.
        :returntype: `bool`"""
        if not extra_info:
            extra_info = {}
        if not authzid:
            return True
        if self.stream and self.stream.initiator:
            return False
        if self.stream and not self.stream.initiator:
            jid = JID(authzid)
            if "username" not in extra_info:
                ret = False
            elif jid.local != extra_info["username"]:
                ret = False
            elif jid.domain != self.stream.me.domain:
                ret = False
            elif not jid.resource:
                ret = False
            else:
                ret = True
        else:
            ret = False
        return ret

    def get_realms(self):
        """Get realms available for client authentication.

        [server only]

        :return: list of realms.
        :returntype: `list` of `str`"""
        if self.stream:
            return [self.stream.me.domain]
        else:
            return []

    def choose_realm(self, realm_list):
        """Choose authentication realm from the list provided by the server.

        [client only]

        Use domain of the own JID if no realm list was provided or the domain
        is on the list or the first realm on the list otherwise.

        :Parameters:
            - `realm_list`: realm list provided by the server.
        :Types:
            - `realm_list`: `list` of `str`

        :return: the realm chosen.
        :returntype: `str`"""
        if not self.stream:
            if realm_list:
                return realm_list[0]
            else:
                return None
        jid = self.stream.me
        if not realm_list:
            return jid.domain
        if jid.domain in realm_list:
            return jid.domain
        return realm_list[0]

    def get_serv_type(self):
        """Get the server name for SASL authentication.

        :return: 'xmpp'."""
        return "xmpp"

    def get_serv_name(self):
        """Get the service name for SASL authentication.

        :return: domain of the own JID."""
        if self.stream:
            return self.stream.me.domain
        else:
            return "unknown"

    def get_serv_host(self):
        """Get the service host name for SASL authentication.

        :return: domain of the own JID."""
        if self.stream:
            transport = self.stream.transport
            if transport._dst_hostname:
                return transport.selected_host
        return self.get_serv_name()


MECHANISMS_TAG = SASL_QNP + "mechanisms"
MECHANISM_TAG = SASL_QNP + "mechanism"
CHALLENGE_TAG = SASL_QNP + "challenge"
SUCCESS_TAG = SASL_QNP + "success"
FAILURE_TAG = SASL_QNP + "failure"
AUTH_TAG = SASL_QNP + "auth"
RESPONSE_TAG = SASL_QNP + "response"
ABORT_TAG = SASL_QNP + "abort"

class StreamSASLHandler(StreamFeatureHandler):
    """SASL authentication handler XMPP streams.

    :Ivariables:
        - `peer_sasl_mechanisms`: SASL mechanisms offered by peer
        - `authenticator`: the authenticator object
    :Types:
        - `peer_sasl_mechanisms`: `list` of `str`
        - `authenticator`: `sasl.ClientAuthenticator` or
          `sasl.ServerAuthenticator`
    """
    def __init__(self, settings = None):
        """Initialize the SASL handler"""
        if settings is None:
            settings = XMPPSettings()
        self.settings = settings
        self.password_manager = settings["password_manager"]
        self.peer_sasl_mechanisms = None
        self.authenticator = None
        self._username = None

    def make_stream_features(self, stream, features):
        """Add SASL features to the <features/> element of the stream.

        [receving entity only]

        :returns: update <features/> element."""
        mechs = self.settings['sasl_mechanisms'] 
        if mechs and not stream.authenticated:
            sub = ElementTree.SubElement(features, MECHANISMS_TAG)
            for mech in mechs:
                if mech in sasl.SERVER_MECHANISMS:
                    ElementTree.SubElement(sub, MECHANISM_TAG).text = mech
        return features

    def handle_stream_features(self, stream, features):
        """Process incoming <stream:features/> element.

        [initiating entity only]
        """
        element = features.find(MECHANISMS_TAG)
        self.peer_sasl_mechanisms = []
        if element is None:
            return None
        for sub in element:
            if sub.tag != MECHANISM_TAG:
                continue
            self.peer_sasl_mechanisms.append(sub.text)

        if stream.authenticated or not self.peer_sasl_mechanisms:
            return StreamFeatureNotHandled("SASL", mandatory = True)

        username = self.settings.get("username")
        if not username:
            if stream.me.local:
                username = stream.me.local
            else:
                username = stream.me.domain
        self._sasl_authenticate(stream, username, self.settings["authzid"])
        return StreamFeatureHandled("SASL", mandatory = True)

    @stream_element_handler(AUTH_TAG, "receiver")
    def process_sasl_auth(self, stream, element):
        """Process incoming <sasl:auth/> element.

        [receiving entity only]
        """
        if self.authenticator:
            logger.debug("Authentication already started")
            return False
        if hasattr(self.password_manager, "set_stream"):
            self.password_manager.set_stream(stream)
        mechanism = element.get("mechanism")
        if not mechanism:
            stream.send_stream_error("bad-format")
            raise FatalStreamError("<sasl:auth/> with no mechanism")

        stream.auth_method_used = mechanism
        self.authenticator = sasl.server_authenticator_factory(mechanism, 
                                                        self.password_manager)
        
        content = element.text.encode("us-ascii")
        ret = self.authenticator.start(base64.decodestring(content))

        if isinstance(ret, sasl.Success):
            element = ElementTree.Element(SUCCESS_TAG)
            element.text = ret.encode()
        elif isinstance(ret, sasl.Challenge):
            element = ElementTree.Element(CHALLENGE_TAG)
            element.text = ret.encode()
        else:
            element = ElementTree.Element(FAILURE_TAG)
            ElementTree.SubElement(element, SASL_QNP + ret.reason)

        stream.write_element(element)

        if isinstance(ret, sasl.Success):
            if ret.authzid:
                peer = JID(ret.authzid)
            else:
                peer = JID(ret.username, stream.me.domain)
            stream.set_peer_authenticated(peer, True)
        elif isinstance(ret, sasl.Failure):
            raise SASLAuthenticationFailed("SASL authentication failed: {0}"
                                                            .format(ret.reason))
        return True

    @stream_element_handler(CHALLENGE_TAG, "initiator")
    def _process_sasl_challenge(self, stream, element):
        """Process incoming <sasl:challenge/> element.

        [initiating entity only]
        """
        if not self.authenticator:
            logger.debug("Unexpected SASL challenge")
            return False

        content = element.text.encode("us-ascii")
        ret = self.authenticator.challenge(base64.decodestring(content))
        if isinstance(ret, sasl.Response):
            element = ElementTree.Element(RESPONSE_TAG)
            element.text = ret.encode()
        else:
            element = ElementTree.Element(ABORT_TAG)

        stream.write_element(element)

        if isinstance(ret, sasl.Failure):
            stream.disconnect()
            raise SASLAuthenticationFailed("SASL authentication failed")

        return True

    @stream_element_handler(RESPONSE_TAG, "receiver")
    def _process_sasl_response(self, stream, element):
        """Process incoming <sasl:response/> element.

        [receiving entity only]
        """
        if not self.authenticator:
            logger.debug("Unexpected SASL response")
            return False

        content = element.text.encode("us-ascii")
        ret = self.authenticator.response(base64.decodestring(content))
        if isinstance(ret, sasl.Success):
            element = ElementTree.Element(SUCCESS_TAG)
            element.text = ret.encode()
        elif isinstance(ret, sasl.Challenge):
            element = ElementTree.Element(CHALLENGE_TAG)
            element.text = ret.encode()
        else:
            element = ElementTree.Element(FAILURE_TAG)
            ElementTree.SubElement(element, SASL_QNP + ret.reason)

        stream.write_element(element)

        if isinstance(ret, sasl.Success):
            authzid = ret.authzid
            if authzid:
                peer = JID(ret.authzid)
            else:
                peer = JID(ret.username, stream.me.domain)
            stream.set_peer_authenticated(peer, True)
        elif isinstance(ret, sasl.Failure):
            raise SASLAuthenticationFailed("SASL authentication failed: {0!r}"
                                                            .format(ret.reson))
        return True

    @stream_element_handler(SUCCESS_TAG, "initiator")
    def _process_sasl_success(self, stream, element):
        """Process incoming <sasl:success/> element.

        [initiating entity only]

        """
        if not self.authenticator:
            logger.debug("Unexpected SASL response")
            return False

        content = element.text

        if content:
            data = base64.decodestring(content.encode("us-ascii"))
        else:
            data = None
        ret = self.authenticator.finish(data)
        if isinstance(ret, sasl.Success):
            logger.debug("SASL authentication succeeded")
            if ret.authzid:
                me = JID(ret.authzid)
            else:
                me = JID(ret.username, ret.realm)
            stream.set_authenticated(me, True)
        else:
            logger.debug("SASL authentication failed")
            raise SASLAuthenticationFailed("Additional success data"
                                                        " procesing failed")
        return True

    @stream_element_handler(FAILURE_TAG, "initiator")
    def _process_sasl_failure(self, stream, element):
        """Process incoming <sasl:failure/> element.

        [initiating entity only]
        """
        _unused = stream
        if not self.authenticator:
            logger.debug("Unexpected SASL response")
            return False

        logger.debug("SASL authentication failed: {0!r}".format(
                                                element_to_unicode(element)))
        raise SASLAuthenticationFailed("SASL authentication failed")

    @stream_element_handler(ABORT_TAG, "receiver")
    def _process_sasl_abort(self, stream, element):
        """Process incoming <sasl:abort/> element.

        [receiving entity only]"""
        _unused, _unused = stream, element
        if not self.authenticator:
            logger.debug("Unexpected SASL response")
            return False

        self.authenticator = None
        logger.debug("SASL authentication aborted")
        return True

    def _sasl_authenticate(self, stream, username, authzid, mechanism = None):
        """Start SASL authentication process.

        [initiating entity only]

        :Parameters:
            - `username`: user name.
            - `authzid`: authorization ID.
            - `mechanism`: SASL mechanism to use."""
        if not stream.initiator:
            raise SASLAuthenticationFailed("Only initiating entity start"
                                                        " SASL authentication")
        if stream.features is None or not self.peer_sasl_mechanisms:
            raise SASLNotAvailable("Peer doesn't support SASL")

        if hasattr(self.password_manager, "set_stream"):
            self.password_manager.set_stream(stream)

        mechs = self.settings['sasl_mechanisms'] 
        if not mechanism:
            mechanism = None
            for mech in mechs:
                if mech in self.peer_sasl_mechanisms:
                    mechanism = mech
                    break
            if not mechanism:
                raise SASLMechanismNotAvailable("Peer doesn't support any of"
                                                        " our SASL mechanisms")
            logger.debug("Our mechanism: {0!r}".format(mechanism))
        else:
            if mechanism not in self.peer_sasl_mechanisms:
                raise SASLMechanismNotAvailable("{0!r} is not available"
                                                            .format(mechanism))

        stream.auth_method_used = mechanism
        self.authenticator = sasl.client_authenticator_factory(mechanism,
                                                        self.password_manager)
        initial_response = self.authenticator.start(username, authzid)
        self._username = username
        if not isinstance(initial_response, sasl.Response):
            raise SASLAuthenticationFailed("SASL initiation failed")

        element = ElementTree.Element(AUTH_TAG)
        element.set("mechanism", mechanism)
        if initial_response.data:
            if initial_response.encode:
                element.text = initial_response.encode()
            else:
                element.text = initial_response.data
        stream.write_element(element)

XMPPSettings.add_setting("username", type = str, default = None,
        cmdline_help = "Username to use instead of the JID local part",
        doc = """The username to use instead of the JID local part."""
    )
XMPPSettings.add_setting("password", type = str, basic = True,
        default = None,
        cmdline_help = "User password",
        doc = """A password for password-based SASL mechanisms."""
    )
XMPPSettings.add_setting("authzid", type = str, default = None,
        cmdline_help = "Authorization id for SASL",
        doc = """The authorization-id (alternative JID) to request during the
SASL authentication."""
    )
XMPPSettings.add_setting("sasl_mechanisms",
        type = 'list of ``unicode``',
        validator = XMPPSettings.validate_string_list,
        default = ["DIGEST-MD5", "PLAIN"],
        cmdline_help = "SASL mechanism to enable",
        doc = """SASL mechanism that can be used for stream authentication."""
    )
XMPPSettings.add_setting("password_manager", type = sasl.PasswordManager,
        factory = DefaultPasswordManager,
        default_d = "A `DefaultPasswordManager` instance",
        doc = """Object providing or checking user password and other
SASL authentication properties."""
    )

# vi: sts=4 et sw=4
