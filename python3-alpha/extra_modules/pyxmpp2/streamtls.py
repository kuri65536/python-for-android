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

"""TLS support for XMPP streams.

Normative reference:
  - `RFC 6120 <http://xmpp.org/rfcs/rfc6120.html>`__
"""



__docformat__ = "restructuredtext en"

import logging
import ssl

from ssl import SSLError

from .etree import ElementTree
from .constants import TLS_QNP
from .streambase import FatalStreamError
from .exceptions import TLSNegotiationFailed
from .exceptions import JIDError
from .jid import JID
from .settings import XMPPSettings
from .streamevents import TLSConnectedEvent

from .interfaces import StreamFeatureHandler
from .interfaces import StreamFeatureHandled, StreamFeatureNotHandled
from .interfaces import stream_element_handler
from .interfaces import EventHandler, event_handler

STARTTLS_TAG = TLS_QNP + "starttls"
REQUIRED_TAG = TLS_QNP + "required"
PROCEED_TAG = TLS_QNP + "proceed"
FAILURE_TAG = TLS_QNP + "failure"
        
logger = logging.getLogger("pyxmpp2.streamtls")

class StreamTLSHandler(StreamFeatureHandler, EventHandler):
    """Handler for stream TLS support.
    """
    def __init__(self, settings = None):
        """Initialize the TLS handler.

        :Parameters:
          - `settings`: settings for StartTLS.
        :Types:
          - `settings`: `XMPPSettings`
        """
        if settings is None:
            self.settings = XMPPSettings()
        else:
            self.settings = settings
        self.stream = None
        self.requested = False
        self.tls_socket = None

    def make_stream_tls_features(self, stream, features):
        """Update the <features/> element with StartTLS feature.

        [receving entity only]

        :Parameters:
            - `features`: the <features/> element of the stream.
        :Types:
            - `features`: :etree:`ElementTree.Element`

        :returns: update <features/> element.
        :returntype: :etree:`ElementTree.Element`
        """
        if self.stream and stream is not self.stream:
            raise ValueError("Single StreamTLSHandler instance can handle"
                                                            " only one stream")
        self.stream = stream
        if self.settings["starttls"] and not stream.tls_established:
            tls = ElementTree.SubElement(features, STARTTLS_TAG)
            if self.settings["tls_require"]:
                ElementTree.SubElement(tls, REQUIRED_TAG)
        return features

    def handle_stream_features(self, stream, features):
        """Process incoming StartTLS related element of <stream:features/>.

        [initiating entity only]

        """
        if self.stream and stream is not self.stream:
            raise ValueError("Single StreamTLSHandler instance can handle"
                                                            " only one stream")
        self.stream = stream
        logger.debug(" tls: handling features")
        element = features.find(STARTTLS_TAG)
        if element is None:
            logger.debug(" tls: no starttls feature found")
            if self.settings["tls_require"]:
                raise TLSNegotiationFailed("StartTLS required,"
                                                " but not supported by peer")
            return None
        if len(features) == 1:
            required = True
        else:
            required = element.find(REQUIRED_TAG) is not None
        if stream.tls_established:
            logger.warning("StartTLS offerred when already established")
            return StreamFeatureNotHandled("StartTLS", mandatory = required)
            
        if self.settings["starttls"]:
            logger.debug("StartTLS negotiated")
            self._request_tls()
            return StreamFeatureHandled("StartTLS", mandatory = required)
        else:
            logger.debug(" tls: not enabled")
            return StreamFeatureNotHandled("StartTLS", mandatory = required)

    def _request_tls(self):
        """Request a TLS-encrypted connection.

        [initiating entity only]"""
        self.requested = True
        element = ElementTree.Element(STARTTLS_TAG)
        self.stream.write_element(element)
    
    @stream_element_handler(FAILURE_TAG, "initiator")
    def _process_tls_failure(self, stream, element):
        """Handle the <failure /> element.
        """
        # pylint: disable-msg=R0201
        _unused, _unused = stream, element
        raise TLSNegotiationFailed("Peer failed to initialize TLS connection")

    @stream_element_handler(PROCEED_TAG, "initiator")
    def _process_tls_proceed(self, stream, element):
        """Handle the <proceed /> element.
        """
        # pylint: disable-msg=W0613
        if not self.requested:
            logger.debug("Unexpected TLS element: {0!r}".format(element))
            return False
        logger.debug(" tls: <proceed/> received")
        self.requested = False
        self._make_tls_connection()
        return True

    @stream_element_handler(STARTTLS_TAG, "receiver")
    def _process_tls_starttls(self, stream, element):
        """Handle <starttls/> element.
        """
        # pylint: disable-msg=R0201
        _unused, _unused = stream, element
        raise FatalStreamError("TLS not implemented for the receiving side yet")

    def _make_tls_connection(self):
        """Initiate TLS connection.

        [initiating entity only]
        """
        logger.debug("Preparing TLS connection")
        if self.settings["tls_verify_peer"]:
            cert_reqs = ssl.CERT_REQUIRED
        else:
            cert_reqs = ssl.CERT_NONE
        self.stream.transport.starttls(
                    keyfile = self.settings["tls_key_file"],
                    certfile = self.settings["tls_cert_file"],
                    server_side = not self.stream.initiator,
                    cert_reqs = cert_reqs,
                    ssl_version = ssl.PROTOCOL_TLSv1,
                    ca_certs = self.settings["tls_cacert_file"],
                    do_handshake_on_connect = False,
                    )

    @event_handler(TLSConnectedEvent)
    def handle_tls_connected_event(self, event):
        """Verify the peer certificate on the `TLSConnectedEvent`.
        """
        if self.settings["tls_verify_peer"]:
            valid = self.settings["tls_verify_callback"](event.stream,
                                                        event.peer_certificate)
            if not valid:
                raise SSLError("Certificate verification failed")
        event.stream.tls_established = True
        with event.stream.lock:
            event.stream._restart_stream() # pylint: disable-msg=W0212

    @staticmethod
    def is_certificate_valid(stream, cert):
        """Default certificate verification callback for TLS connections.

        :Parameters:
            - `cert`: certificate information, as returned by
              :std:`ssl.SSLSocket.getpeercert`

        :return: computed verification result."""
        try:
            logger.debug("tls_is_certificate_valid(cert = {0!r})".format(cert))
            if not cert:
                logger.warning("No TLS certificate information received.")
                return False
            valid_hostname_found = False
            logger.debug(" tls: checking peer name in the certificate"
                                    " should be: {0}".format(stream.peer))
            if 'subject' in cert:
                for rdns in cert['subject']:
                    for key, value in rdns:
                        if key != 'commonName':
                            continue
                        try:
                            value = JID(value)
                        except JIDError:
                            continue
                        if value == stream.peer:
                            logger.debug(" good commonName: {0}".format(value))
                            valid_hostname_found = True
                        else:
                            logger.debug(" {0} != {1}".format(value, 
                                                                stream.peer))
            if 'subjectAltName' in cert:
                for key, value in cert['subjectAltName']:
                    if key != 'DNS':
                        continue
                    try:
                        value = JID(value)
                    except JIDError:
                        continue
                    if value == stream.peer:
                        logger.debug(" good subjectAltName({0}): {1}"
                                                            .format(key, value))
                        valid_hostname_found = True
                    else:
                        logger.debug(" {0} != {1}".format(value, stream.peer))
            return valid_hostname_found
        except:
            logger.exception("Exception caught while checking a certificate")
            raise

XMPPSettings.add_setting("starttls", type = bool, default = False,
        basic = True,
        cmdline_help = "Enable StartTLS negotiation",
        doc = """Enable StartTLS negotiation."""
    )

XMPPSettings.add_setting("tls_require", type = bool, default = False,
        basic = True,
        cmdline_help = "Require TLS stream encryption",
        doc = """Require TLS stream encryption."""
    )

XMPPSettings.add_setting("tls_verify_peer", type = bool, default = True,
        basic = True,
        cmdline_help = "Verify the peer certificate",
        doc = """Verify the peer certificate."""
    )

XMPPSettings.add_setting("tls_cert_file", type = str,
        cmdline_help = "TLS certificate file",
        doc = """Path to the TLS certificate file. The file should contain
the certificate, any immediate certificates needed and it may optionally
contain the private key. All in the PEM format, concatenated."""
    )

XMPPSettings.add_setting("tls_key_file", type = str,
        cmdline_help = "TLS certificate private key file",
        doc = """Path to the TLS certificate private key file (in the PEM
format). Not needed if the key is included in the file pointed by the
:r:`tls_cert_file setting`."""
    )

XMPPSettings.add_setting("tls_cacert_file", type = str, basic = True,
        cmdline_help = "TLS CA certificates file",
        doc = """Path to the TLS CA certificates file. The file should contain
the trusted CA certificates in the PEM format, concatenated."""
    )

XMPPSettings.add_setting("tls_verify_callback", type = "callable",
        default = StreamTLSHandler.is_certificate_valid,
        doc = """A function to verify if a certificate is valid and if the
remote party presenting this certificate is authorized to use the stream.
The function must accept two arguments: a stream and the certificate 
to verify."""
    )

# vi: sts=4 et sw=4
