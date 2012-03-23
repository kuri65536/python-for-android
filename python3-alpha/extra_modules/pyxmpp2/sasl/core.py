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
"""Base classes for PyXMPP SASL implementation.

Normative reference:
  - `RFC 4422 <http://www.ietf.org/rfc/rfc4422.txt>`__
"""



__docformat__ = "restructuredtext en"

import uuid
import hashlib

from base64 import standard_b64encode

from abc import ABCMeta, abstractmethod

CLIENT_MECHANISMS_D = {}
CLIENT_MECHANISMS = []
SECURE_CLIENT_MECHANISMS = []

SERVER_MECHANISMS_D = {}
SERVER_MECHANISMS = []
SECURE_SERVER_MECHANISMS = []
        
class PasswordManager(metaclass=ABCMeta):
    """Base class for password managers.

    Password manager is an object responsible for providing or verification
    of authentication credentials.

    All the methods of `PasswordManager` class may be overriden in derived
    classes for specific authentication and authorization policy."""
    def get_password(self, username, realm = None,
                                            acceptable_formats = ("plain", )):
        """Get the password for user authentication.

        [both client or server]

        By default returns (None, None) providing no password. Should be
        overriden in derived classes unless only `check_password` functionality
        is available.

        :Parameters:
            - `username`: the username for which the password is requested.
            - `realm`: the authentication realm for which the password is
              requested.
            - `acceptable_formats`: a sequence of acceptable formats of the
              password data. Could be "plain" (plain text password),
              "md5:user:realm:password" (MD5 hex digest of user:realm:password)
              or any other mechanism-specific encoding. This allows
              non-plain-text storage of passwords. But only "plain" format will
              work with all password authentication mechanisms.
        :Types:
            - `username`: `str`
            - `realm`: `str`
            - `acceptable_formats`: sequence of `str`

        :return: the password and its encoding (format).
        :returntype: `str`,`str` tuple.
        """
        # pylint: disable-msg=W0613
        return None, None

    def check_password(self, username, password, realm = None):
        """Check the password validity.

        [server only]

        Used by plain-text authentication mechanisms.

        Default implementation: retrieve a "plain" password for the `username`
        and `realm` using `self.get_password` and compare it with the password
        provided.

        May be overrided e.g. to check the password against some external
        authentication mechanism (PAM, LDAP, etc.).

        :Parameters:
            - `username`: the username for which the password verification is
              requested.
            - `password`: the password to verify.
            - `realm`: the authentication realm for which the password
              verification is requested.
        :Types:
            - `username`: `str`
            - `password`: `str`
            - `realm`: `str`

        :return: `True` if the password is valid.
        :returntype: `bool`
        """
        pwd, pwd_format = self.get_password(username, realm, (
                                        "plain", "md5:user:realm:password"))
        if pwd_format == "plain":
            return pwd is not None and password == pwd
        elif pwd_format in ("md5:user:realm:password"):
            if realm is None:
                realm = ""
            else:
                realm = realm.encode("utf-8")
            username = username.encode("utf-8")
            password = password.encode("utf-8")

            # pylint: disable-msg=E1101
            urp_hash = hashlib.md5(b"%s:%s:%s").hexdigest()
            return urp_hash == pwd
        return False

    def get_realms(self):
        """Get available realms list.

        [server only]

        :return: a list of realms available for authentication. May be empty --
            the client may choose its own realm then or use no realm at all.
        :returntype: `list` of `str`
        """
        return []

    def choose_realm(self, realm_list):
        """Choose an authentication realm from the list provided by the server.

        [client only]

        By default return the first realm from the list or `None` if the list
        is empty.

        :Parameters:
            - `realm_list`: the list of realms provided by a server.
        :Types:
            - `realm_list`: sequence of `str`

        :return: the realm chosen.
        :returntype: `str`
        """
        if realm_list:
            return realm_list[0]
        else:
            return None

    def check_authzid(self, authzid, extra_info = None):
        """Check if the authenticated entity is allowed to use given
        authorization id.

        [server only]

        By default return `True` if the `authzid` is `None` or empty or it is
        equal to extra_info["username"] (if the latter is present).

        :Parameters:
            - `authzid`: an authorization id.
            - `extra_info`: information about an entity got during the
              authentication process. This is a mapping with arbitrary,
              mechanism-dependent items. Common keys are 'username' or
              'realm'.
        :Types:
            - `authzid`: `str`
            - `extra_info`: mapping

        :return: `True` if the authenticated entity is authorized to use
            the provided authorization id.
        :returntype: `bool`
        """
        if not extra_info:
            extra_info = {}
        return (not authzid
                or "username" in extra_info
                        and extra_info["username"] == authzid)

    def get_serv_type(self):
        """Return the service type for DIGEST-MD5 'digest-uri' field.

        Should be overriden in derived classes.

        :return: the service type ("unknown" by default)
        :returntype: `str`
        """
        return "unknown"

    def get_serv_host(self):
        """Return the host name for DIGEST-MD5 'digest-uri' field.

        Should be overriden in derived classes.

        :return: the host name ("unknown" by default)
        :returntype: `str`
        """
        return "unknown"

    def get_serv_name(self):
        """Return the service name for DIGEST-MD5 'digest-uri' field.

        Should be overriden in derived classes.

        :return: the service name or `None` (which is the default).
        :returntype: `str`
        """
        return None

    def generate_nonce(self):
        """Generate a random string for digest authentication challenges.

        The string should be cryptographicaly secure random pattern.

        :return: the string generated.
        :returntype: `bytes`
        """
        return uuid.uuid4().hex

class Reply(object):
    """Base class for SASL authentication reply objects.

    :Ivariables:
        - `data`: optional reply data.
        - `_encode`: whether to base64 encode the data or not
    :Types:
        - `data`: `bytes`
        - `_encode`: `bool`
    """
    # pylint: disable-msg=R0903
    def __init__(self, data = b"", encode = True):
        """Initialize the `Reply` object.

        :Parameters:
            - `data`: optional reply data.
            - `encode`: whether to base64 encode the data or not
        :Types:
            - `data`: `bytes`
            - `encode`: `bool`
        """
        self.data = data
        self._encode = encode

    def encode(self):
        """Base64-encode the data contained in the reply when appropriate.

        :return: encoded data.
        :returntype: `bytes`
        """
        if self.data is not None and self._encode:
            ret = standard_b64encode(self.data)
            return ret.decode("us-ascii")
        else:
            return self.data

class Challenge(Reply):
    """The challenge SASL message (server's challenge for the client)."""
    # pylint: disable-msg=R0903
    def __init__(self, data, encode = True):
        """Initialize the `Challenge` object."""
        Reply.__init__(self, data, encode)
    def __repr__(self):
        return "<sasl.Challenge: {0!r}>".format(self.data)

class Response(Reply):
    """The response SASL message (clients's reply the the server's
    challenge)."""
    # pylint: disable-msg=R0903
    def __init__(self, data = b"", encode = True):
        """Initialize the `Response` object."""
        Reply.__init__(self, data, encode)
    def __repr__(self):
        return "<sasl.Response: {0!r}>".format(self.data)

class Failure(Reply):
    """The failure SASL message.

    :Ivariables:
        - `reason`: the failure reason.
    :Types:
        - `reason`: `str`.
    """
    # pylint: disable-msg=R0903
    def __init__(self, reason):
        """Initialize the `Failure` object.

        :Parameters:
            - `reason`: the failure reason.
        :Types:
            - `reason`: `str`.
        """
        Reply.__init__(self, None)
        self.reason = reason
    def __repr__(self):
        return "<sasl.Failure: {0!r}>".format(self.reason)

class Success(Reply):
    """The success SASL message (sent by the server on authentication
    success).
    """
    # pylint: disable-msg=R0903
    def __init__(self, username, realm = None, authzid = None, data = None,
                                                                encode = True):
        """Initialize the `Success` object.

        :Parameters:
            - `username`: authenticated username (authentication id).
            - `realm`: authentication realm used.
            - `authzid`: authorization id.
            - `data`: the success data to be sent to the client.
            - `encode`: whether to base64 encode the data or not
        :Types:
            - `username`: `str`
            - `realm`: `str`
            - `authzid`: `str`
            - `data`: `bytes`
            - `encode`: `bool`
        """
        # pylint: disable-msg=R0913
        Reply.__init__(self, data, encode)
        self.username = username
        self.realm = realm
        self.authzid = authzid
    def __repr__(self):
        return "<sasl.Success: authzid: {0!r} data: {1!r}>".format(
                                                    self.authzid, self.data)

class ClientAuthenticator(metaclass=ABCMeta):
    """Base class for client authenticators.

    A client authenticator class is a client-side implementation of a SASL
    mechanism. One `ClientAuthenticator` object may be used for one
    client authentication process.
    """
    def __init__(self, password_manager):
        """Initialize a `ClientAuthenticator` object.

        :Parameters:
            - `password_manager`: a password manager providing authentication
              credentials.
        :Types:
            - `password_manager`: `PasswordManager`
        """
        self.password_manager = password_manager

    @abstractmethod
    def start(self, username, authzid):
        """Start the authentication process.

        :Parameters:
            - `username`: the username (authentication id).
            - `authzid`: the authorization id requester.
        :Types:
            - `username`: `str`
            - `authzid`: `str`

        :return: the initial response to send to the server or a failuer
            indicator.
        :returntype: `Response` or `Failure`"""
        raise NotImplementedError

    @abstractmethod
    def challenge(self, challenge):
        """Process the server's challenge.

        :Parameters:
            - `challenge`: the challenge.
        :Types:
            - `challenge`: `bytes`

        :return: the response or a failure indicator.
        :returntype: `Response` or `Failure`"""
        raise NotImplementedError

    @abstractmethod
    def finish(self, data):
        """Handle authentication succes information from the server.

        :Parameters:
            - `data`: the optional additional data returned with the success.
        :Types:
            - `data`: `bytes`

        :return: success or failure indicator.
        :returntype: `Success` or `Failure`"""
        raise NotImplementedError

class ServerAuthenticator(metaclass=ABCMeta):
    """Base class for server authenticators.

    A server authenticator class is a server-side implementation of a SASL
    mechanism. One `ServerAuthenticator` object may be used for one
    client authentication process.
    """
    def __init__(self, password_manager):
        """Initialize a `ServerAuthenticator` object.

        :Parameters:
            - `password_manager`: a password manager providing authentication
              credential verfication.
        :Types:
            - `password_manager`: `PasswordManager`"""
        self.password_manager = password_manager

    @abstractmethod
    def start(self, initial_response):
        """Start the authentication process.

        :Parameters:
            - `initial_response`: the initial response send by the client with
              the authentication request.

        :Types:
            - `initial_response`: `bytes`

        :return: a challenge, a success or a failure indicator.
        :returntype: `Challenge` or `Failure` or `Success`"""
        raise NotImplementedError

    @abstractmethod
    def response(self, response):
        """Process a response from a client.

        :Parameters:
            - `response`: the response from the client to our challenge.
        :Types:
            - `response`: `bytes`

        :return: a challenge, a success or a failure indicator.
        :returntype: `Challenge` or `Success` or `Failure`"""
        raise NotImplementedError

def _key_func(item):
    """Key function used for sorting SASL authenticator classes
    """
    # pylint: disable-msg=W0212
    klass = item[1]
    return (klass._pyxmpp_sasl_secure, klass._pyxmpp_sasl_preference)

def _register_client_authenticator(klass, name):
    """Add a client authenticator class to `CLIENT_MECHANISMS_D`,
    `CLIENT_MECHANISMS` and, optionally, to `SECURE_CLIENT_MECHANISMS`
    """
    # pylint: disable-msg=W0212
    CLIENT_MECHANISMS_D[name] = klass
    items = sorted(list(CLIENT_MECHANISMS_D.items()), key = _key_func, reverse = True)
    CLIENT_MECHANISMS[:] = [k for (k, v) in items ]
    SECURE_CLIENT_MECHANISMS[:] = [k for (k, v) in items 
                                                    if v._pyxmpp_sasl_secure]

def _register_server_authenticator(klass, name):
    """Add a client authenticator class to `SERVER_MECHANISMS_D`,
    `SERVER_MECHANISMS` and, optionally, to `SECURE_SERVER_MECHANISMS`
    """
    # pylint: disable-msg=W0212
    SERVER_MECHANISMS_D[name] = klass
    items = sorted(list(SERVER_MECHANISMS_D.items()), key = _key_func, reverse = True)
    SERVER_MECHANISMS[:] = [k for (k, v) in items ]
    SECURE_SERVER_MECHANISMS[:] = [k for (k, v) in items 
                                                    if v._pyxmpp_sasl_secure]

def sasl_mechanism(name, secure, preference = 50):
    """Class decorator generator for `ClientAuthenticator` or
    `ServerAuthenticator` subclasses. Adds the class to the pyxmpp.sasl
    mechanism registry.

    :Parameters:
        - `name`: SASL mechanism name
        - `secure`: if the mechanims can be considered secure - `True`
          if it can be used over plain-text channel
        - `preference`: mechanism preference level (the higher the better)
    :Types:
        - `name`: `str`
        - `secure`: `bool`
        - `preference`: `int`
    """
    # pylint: disable-msg=W0212
    def decorator(klass):
        """The decorator."""
        klass._pyxmpp_sasl_secure = secure
        klass._pyxmpp_sasl_preference = preference
        if issubclass(klass, ClientAuthenticator):
            _register_client_authenticator(klass, name)
        elif issubclass(klass, ServerAuthenticator):
            _register_server_authenticator(klass, name)
        else:
            raise TypeError("Not a ClientAuthenticator"
                                            " or ServerAuthenticator class")
        return klass
    return decorator

# vi: sts=4 et sw=4
