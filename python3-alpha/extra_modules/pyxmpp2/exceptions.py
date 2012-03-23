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

"""PyXMPP exceptions.

This module defines all exceptions raised by PyXMPP.
"""
# pylint: disable-msg=R0901



__docformat__ = "restructuredtext en"

import logging


class Error(Exception):
    """Base class for all PyXMPP exceptions."""
    pass

class JIDError(Error, ValueError):
    "Exception raised when invalid JID is used"
    pass

class PyXMPPIOError(Error):
    """Exception raised on I/O error."""
    pass

class StreamError(Error):
    """Base class for all stream errors."""
    pass

class StreamEncryptionRequired(StreamError):
    """Exception raised when stream encryption is requested, but not used."""
    pass

class HostMismatch(StreamError):
    """Exception raised when the connected host name is other then requested."""
    pass

class FatalStreamError(StreamError):
    """Base class for all fatal Stream exceptions.

    When `FatalStreamError` is raised the stream is no longer usable."""
    pass

class StreamParseError(FatalStreamError):
    """Raised when invalid XML is received in an XMPP stream."""
    pass

class DNSError(FatalStreamError):
    """Raised when no host name could be resolved for the target."""
    pass

class UnexpectedCNAMEError(DNSError):
    """Raised when CNAME record was found when A or AAAA was expected."""
    pass

class StreamAuthenticationError(FatalStreamError):
    """Raised when stream authentication fails."""
    pass

class TLSNegotiationFailed(FatalStreamError):
    """Raised when stream TLS negotiation fails."""
    pass

class TLSError(FatalStreamError):
    """Raised on TLS error during stream processing."""
    pass

class SASLNotAvailable(StreamAuthenticationError):
    """Raised when SASL authentication is requested, but not available."""
    pass

class SASLMechanismNotAvailable(StreamAuthenticationError):
    """Raised when none of SASL authentication mechanisms requested is
    available."""
    pass

class SASLAuthenticationFailed(StreamAuthenticationError):
    """Raised when stream SASL authentication fails."""
    pass

class StringprepError(Error):
    """Exception raised when string preparation results in error."""
    pass

class ClientError(Error):
    """Raised on a client error."""
    pass

class NoRouteError(Error):
    """Raised when a stanza cannot be routed internally."""
    pass

class FatalClientError(ClientError):
    """Raised on a fatal client error."""
    pass

class ClientStreamError(StreamError):
    """Raised on a client stream error."""
    pass

class FatalClientStreamError(FatalStreamError):
    """Raised on a fatal client stream error."""
    pass

class LegacyAuthenticationError(ClientStreamError):
    """Raised on a legacy authentication error."""
    pass

class RegistrationError(ClientStreamError):
    """Raised on a in-band registration error."""
    pass

class ComponentStreamError(StreamError):
    """Raised on a component error."""
    pass

class FatalComponentStreamError(ComponentStreamError, FatalStreamError):
    """Raised on a fatal component error."""
    pass

########################
# Protocol Errors

class ProtocolError(Error):
    """Raised when there is something wrong with a stanza processed.

    When not processed earlier by an application, the exception will be catched
    by the stanza dispatcher to return XMPP error to the stanza sender, when
    allowed.

    ProtocolErrors handled internally by PyXMPP will be logged via the logging
    interface. Errors reported to the sender will be logged using
    "pyxmpp2.ProtocolError.reported" channel and the ignored errors using
    "pyxmpp2.ProtocolError.ignored" channel. Both with the "debug" level.
    
    """

    logger_reported = logging.getLogger("pyxmpp2.ProtocolError.reported")
    logger_ignored = logging.getLogger("pyxmpp2.ProtocolError.ignored")

    def __init__(self, xmpp_name, message):
        Error.__init__(self, xmpp_name, message)

    @property
    def xmpp_name(self):
        """XMPP error name which should be reported"""
        return self.args[0]
    @property
    def message(self):
        """The error message."""
        return self.args[1]
    def log_reported(self):
        """Log message via the "pyxmpp.ProtocolError.reported" logger."""
        self.logger_reported.debug("Protocol error detected: {0}"
                                                        .format(self.message))
    def log_ignored(self):
        """Log message via the "pyxmpp.ProtocolError.ignored" logger."""
        self.logger_ignored.debug("Protocol error detected: {0}"
                                                        .format(self.message))
    def __str__(self):
        return str(self.args[1])
    def __repr__(self):
        return "<ProtocolError %r %r>" % (self.xmpp_name, self.message)

class BadRequestProtocolError(ProtocolError):
    """Raised when invalid stanza is processed and 'bad-request' error should
    be reported."""
    def __init__(self, message):
        ProtocolError.__init__(self, "bad-request", message)

class NotAcceptableProtocolError(ProtocolError):
    """Raised when invalid stanza is processed and 'not-acceptable' error
    should be reported."""
    def __init__(self, message):
        ProtocolError.__init__(self, "not-acceptable", message)

class JIDMalformedProtocolError(ProtocolError, JIDError):
    """Raised when invalid JID is encountered."""
    def __init__(self, message):
        JIDError.__init__(self)
        ProtocolError.__init__(self, "jid-malformed", message)

class FeatureNotImplementedProtocolError(ProtocolError):
    """Raised when stanza requests a feature which is not (yet) implemented."""
    def __init__(self, message):
        ProtocolError.__init__(self, "feature-not-implemented", message)

class ServiceUnavailableProtocolError(ProtocolError):
    """Raised when stanza requests a feature which is not (yet) implemented."""
    def __init__(self, message):
        ProtocolError.__init__(self, "service-unavailable", message)

class ResourceConstraintProtocolError(ProtocolError):
    """Raised when stanza requests a feature which is not (yet) implemented."""
    def __init__(self, message):
        ProtocolError.__init__(self, "resource-constraint", message)

# vi: sts=4 et sw=4
