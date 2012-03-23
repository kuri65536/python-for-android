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
"""PLAIN authentication mechanism for PyXMPP SASL implementation.

Normative reference:
  - `RFC 4616 <http://www.ietf.org/rfc/rfc4616.txt>`__
"""



__docformat__ = "restructuredtext en"

import logging

from .core import ClientAuthenticator, ServerAuthenticator
from .core import Success, Failure, Challenge, Response
from .core import sasl_mechanism
        
logger = logging.getLogger("pyxmpp2.sasl.plain")

@sasl_mechanism("PLAIN", 10)
class PlainClientAuthenticator(ClientAuthenticator):
    """Provides PLAIN SASL authentication for a client."""
    def __init__(self, password_manager):
        """Initialize a `PlainClientAuthenticator` object.

        :Parameters:
            - `password_manager`: name of the password manager object providing
              authentication credentials.
        :Types:
            - `password_manager`: `PasswordManager`"""
        ClientAuthenticator.__init__(self, password_manager)
        self.username = None
        self.finished = None
        self.password = None
        self.authzid = None

    def start(self, username, authzid):
        """Start the authentication process and return the initial response.

        :Parameters:
            - `username`: username (authentication id).
            - `authzid`: authorization id.
        :Types:
            - `username`: `str`
            - `authzid`: `str`

        :return: the initial response or a failure indicator.
        :returntype: `sasl.Response` or `sasl.Failure`"""
        self.username = username
        if authzid:
            self.authzid = authzid
        else:
            self.authzid = ""
        self.finished = False
        return self.challenge(b"")

    def challenge(self, challenge):
        """Process the challenge and return the response.

        :Parameters:
            - `challenge`: the challenge.
        :Types:
            - `challenge`: `bytes`

        :return: the response or a failure indicator.
        :returntype: `sasl.Response` or `sasl.Failure`"""
        if self.finished:
            logger.debug("Already authenticated")
            return Failure("extra-challenge")
        self.finished = True
        if self.password is None:
            self.password, pformat = self.password_manager.get_password(
                                                                self.username)
        if self.password is None or pformat != "plain":
            logger.debug("Couldn't retrieve plain password")
            return Failure("password-unavailable")
        return Response(b"\000".join(( self.authzid.encode("utf-8"),
                            self.username.encode("utf-8"),
                            self.password.encode("utf-8"))))

    def finish(self, data):
        """Handle authentication succes information from the server.

        :Parameters:
            - `data`: the optional additional data returned with the success.
        :Types:
            - `data`: `bytes`

        :return: a success indicator.
        :returntype: `Success`"""
        return Success(self.username, None, self.authzid)

@sasl_mechanism("PLAIN", 10)
class PlainServerAuthenticator(ServerAuthenticator):
    """Provides PLAIN SASL authentication for a server.
    """
    def __init__(self, password_manager):
        """Initialize a `PlainServerAuthenticator` object.

        :Parameters:
            - `password_manager`: name of the password manager object providing
              authentication credential verification.
        :Types:
            - `password_manager`: `PasswordManager`
        """
        ServerAuthenticator.__init__(self, password_manager)

    def start(self, response):
        """Start the authentication process.

        :Parameters:
            - `response`: the initial response from the client.
        :Types:
            - `response`: `bytes`

        :return: a challenge, a success indicator or a failure indicator.
        :returntype: `sasl.Challenge`, `sasl.Success` or `sasl.Failure`"""
        if not response:
            return Challenge(b"")
        return self.response(response)

    def response(self, response):
        """Process a client reponse.

        :Parameters:
            - `response`: the response from the client.
        :Types:
            - `response`: `bytes`

        :return: a challenge, a success indicator or a failure indicator.
        :returntype: `sasl.Challenge`, `sasl.Success` or `sasl.Failure`"""
        fields = response.split(b"\000")
        if len(fields) != 3:
            logger.debug("Bad response: {0!r}".format(response))
            return Failure("not-authorized")
        authzid, username, password = fields
        authzid = authzid.decode("utf8")
        username = username.decode("utf8")
        password = password.decode("utf8")
        if not self.password_manager.check_password(username, password):
            logger.debug("Bad password. Response was: {0!r}".format(response))
            return Failure("not-authorized")
        info = {"mechanism": "PLAIN", "username": username}
        if self.password_manager.check_authzid(authzid, info):
            return Success(username, None, authzid)
        else:
            logger.debug("Authzid verification failed.")
            return Failure("invalid-authzid")

# vi: sts=4 et sw=4
