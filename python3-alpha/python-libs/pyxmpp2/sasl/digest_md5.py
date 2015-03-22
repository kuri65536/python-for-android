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
"""DIGEST-MD5 authentication mechanism for PyXMPP SASL implementation.

Normative reference:
  - `RFC 2831 <http://www.ietf.org/rfc/rfc2831.txt>`__
"""



__docformat__ = "restructuredtext en"

from binascii import b2a_hex, a2b_hex
import re
import logging

import hashlib

from .core import ClientAuthenticator, ServerAuthenticator
from .core import Failure, Response, Challenge, Success, Failure
from .core import sasl_mechanism
        
logger = logging.getLogger("pyxmpp2.sasl.digest_md5")

QUOTE_RE = re.compile(br"(?<!\\)\\(.)")
PARAM_RE = re.compile(br'^(?P<var>[^=]+)\=(?P<val>(\"(([^"\\]+)|(\\\")'
                            br'|(\\\\))+\")|([^",]+))(\s*\,\s*(?P<rest>.*))?$')

def _unquote(data):
    """Unquote quoted value from DIGEST-MD5 challenge or response.

    If `data` doesn't start or doesn't end with '"' then return it unchanged,
    remove the quotes and escape backslashes otherwise.

    :Parameters:
        - `data`: a quoted string.
    :Types:
        - `data`: `bytes`

    :return: the unquoted string.
    :returntype: `bytes`
    """
    if not data.startswith(b'"') or not data.endswith(b'"'):
        return data
    return QUOTE_RE.sub(b"\\1", data[1:-1])

def _quote(data):
    """Prepare a string for quoting for DIGEST-MD5 challenge or response.

    Don't add the quotes, only escape '"' and "\\" with backslashes.

    :Parameters:
        - `data`: a raw string.
    :Types:
        - `data`: `bytes`

    :return: `data` with '"' and "\\" escaped using "\\".
    :returntype: `bytes`
    """
    data = data.replace(b'\\', b'\\\\')
    data = data.replace(b'"', b'\\"')
    return data

def _h_value(data):
    """H function of the DIGEST-MD5 algorithm (MD5 sum).

    :Parameters:
        - `data`: a byte string.
    :Types:
        - `data`: `bytes`

    :return: MD5 sum of the string.
    :returntype: `bytes`"""
    # pylint: disable-msg=E1101
    return hashlib.md5(data).digest()

def _kd_value(k_val, s_val):
    """KD function of the DIGEST-MD5 algorithm.

    :Parameters:
        - `k_val`: a byte string.
        - `s_val`: a byte string.
    :Types:
        - `k_val`: `bytes`
        - `s_val`: `bytes`

    :return: MD5 sum of the strings joined with ':'.
    :returntype: `bytes`"""
    return _h_value(b":".join((k_val, s_val)))

def _make_urp_hash(username, realm, passwd):
    """Compute MD5 sum of username:realm:password.

    :Parameters:
        - `username`: a username.
        - `realm`: a realm.
        - `passwd`: a password.
    :Types:
        - `username`: `bytes`
        - `realm`: `bytes`
        - `passwd`: `bytes`

    :return: the MD5 sum of the parameters joined with ':'.
    :returntype: `bytes`"""
    if realm is None:
        realm = b""
    return _h_value(b":".join((username, realm, passwd)))

def _compute_response(urp_hash, nonce, cnonce, nonce_count, authzid,
                                                                    digest_uri):
    """Compute DIGEST-MD5 response value.

    :Parameters:
        - `urp_hash`: MD5 sum of username:realm:password.
        - `nonce`: nonce value from a server challenge.
        - `cnonce`: cnonce value from the client response.
        - `nonce_count`: nonce count value.
        - `authzid`: authorization id.
        - `digest_uri`: digest-uri value.
    :Types:
        - `urp_hash`: `bytes`
        - `nonce`: `bytes`
        - `nonce_count`: `int`
        - `authzid`: `bytes`
        - `digest_uri`: `bytes`

    :return: the computed response value.
    :returntype: `bytes`"""
    # pylint: disable-msg=C0103,R0913
    if authzid:
        a1 = b":".join((urp_hash, nonce, cnonce, authzid))
    else:
        a1 = b":".join((urp_hash, nonce, cnonce))
    a2 = b"AUTHENTICATE:" + digest_uri
    return b2a_hex(_kd_value(b2a_hex(_h_value(a1)), b":".join((
            nonce, nonce_count, cnonce, b"auth", b2a_hex(_h_value(a2))))))

def _compute_response_auth(urp_hash, nonce, cnonce, nonce_count, authzid,
                                                                    digest_uri):
    """Compute DIGEST-MD5 rspauth value.

    :Parameters:
        - `urp_hash`: MD5 sum of username:realm:password.
        - `nonce`: nonce value from a server challenge.
        - `cnonce`: cnonce value from the client response.
        - `nonce_count`: nonce count value.
        - `authzid`: authorization id.
        - `digest_uri`: digest-uri value.
    :Types:
        - `urp_hash`: `bytes`
        - `nonce`: `bytes`
        - `nonce_count`: `int`
        - `authzid`: `bytes`
        - `digest_uri`: `bytes`

    :return: the computed rspauth value.
    :returntype: `bytes`"""
    # pylint: disable-msg=C0103,R0913
    if authzid:
        a1 = b":".join((urp_hash, nonce, cnonce, authzid))
    else:
        a1 = b":".join((urp_hash, nonce, cnonce))
    a2 = b":" + digest_uri
    return b2a_hex(_kd_value(b2a_hex(_h_value(a1)), b":".join((
            nonce, nonce_count, cnonce, b"auth", b2a_hex(_h_value(a2))))))

@sasl_mechanism("DIGEST-MD5", 70)
class DigestMD5ClientAuthenticator(ClientAuthenticator):
    """Provides PLAIN SASL authentication for a client.

    :Ivariables:
        - `password`: current authentication password
        - `pformat`: current authentication password format
        - `realm`: current authentication realm
    """
    # pylint: disable-msg=R0902
    def __init__(self, password_manager):
        """Initialize a `DigestMD5ClientAuthenticator` object.

        :Parameters:
            - `password_manager`: name of the password manager object providing
              authentication credentials.
        :Types:
            - `password_manager`: `PasswordManager`"""
        ClientAuthenticator.__init__(self, password_manager)
        self.username = None
        self.rspauth_checked = None
        self.response_auth = None
        self.authzid = None
        self.pformat = None
        self.realm = None
        self.password = None
        self.nonce_count = None

    def start(self, username, authzid):
        """Start the authentication process initializing client state.

        :Parameters:
            - `username`: username (authentication id).
            - `authzid`: authorization id.
        :Types:
            - `username`: `str`
            - `authzid`: `str`

        :return: the (empty) initial response
        :returntype: `sasl.Response` or `sasl.Failure`"""
        self.username = username
        if authzid:
            self.authzid = authzid
        else:
            self.authzid = ""
        self.password = None
        self.pformat = None
        self.nonce_count = 0
        self.response_auth = None
        self.rspauth_checked = False
        self.realm = None
        return Response()

    def challenge(self, challenge):
        """Process a challenge and return the response.

        :Parameters:
            - `challenge`: the challenge from server.
        :Types:
            - `challenge`: `bytes`

        :return: the response or a failure indicator.
        :returntype: `sasl.Response` or `sasl.Failure`"""
        # pylint: disable-msg=R0911,R0912
        if not challenge:
            logger.debug("Empty challenge")
            return Failure("bad-challenge")

        # workaround for some buggy implementations
        challenge = challenge.split(b'\x00')[0] 

        if self.response_auth:
            return self._final_challenge(challenge)
        realms = []
        nonce = None
        charset = "iso-8859-1"
        while challenge:
            match = PARAM_RE.match(challenge)
            if not match:
                logger.debug("Challenge syntax error: {0!r}".format(challenge))
                return Failure("bad-challenge")
            challenge = match.group("rest")
            var = match.group("var")
            val = match.group("val")
            logger.debug("{0!r}: {1!r}".format(var, val))
            if var == b"realm":
                realms.append(_unquote(val))
            elif var == b"nonce":
                if nonce:
                    logger.debug("Duplicate nonce")
                    return Failure("bad-challenge")
                nonce = _unquote(val)
            elif var == b"qop":
                qopl = _unquote(val).split(b",")
                if b"auth" not in qopl:
                    logger.debug("auth not supported")
                    return Failure("not-implemented")
            elif var == b"charset":
                if val != b"utf-8":
                    logger.debug("charset given and not utf-8")
                    return Failure("bad-challenge")
                charset = "utf-8"
            elif var == b"algorithm":
                if val != b"md5-sess":
                    logger.debug("algorithm given and not md5-sess")
                    return Failure("bad-challenge")
        if not nonce:
            logger.debug("nonce not given")
            return Failure("bad-challenge")
        self._get_password()
        return self._make_response(charset, realms, nonce)

    def _get_password(self):
        """Retrieve user's password from the password manager.

        Set `self.password` to the password and `self.pformat`
        to its format name ('plain' or 'md5:user:realm:pass')."""
        if self.password is None:
            self.password, self.pformat = self.password_manager.get_password(
                        self.username, ["plain","md5:user:realm:pass"])
        if not self.password or self.pformat not in (
                                            "plain", "md5:user:realm:pass"):
            logger.debug("Couldn't get plain password."
                            " Password: {0!} Format: {0!r}".format(
                                                self.password, self.pformat))
            return Failure("password-unavailable")

    def _make_response(self, charset, realms, nonce):
        """Make a response for the first challenge from the server.

        :Parameters:
            - `charset`: charset name from the challenge.
            - `realms`: realms list from the challenge.
            - `nonce`: nonce value from the challenge.
        :Types:
            - `charset`: `bytes`
            - `realms`: `bytes`
            - `nonce`: `bytes`

        :return: the response or a failure indicator.
        :returntype: `sasl.Response` or `sasl.Failure`"""
        # pylint: disable-msg=R0914,R0915
        params = []
        realm = self._get_realm(realms, charset)
        if isinstance(realm, Failure):
            return realm
        elif realm:
            realm = _quote(realm)
            params.append(b'realm="' + realm + b'"')

        try:
            username = self.username.encode(charset)
        except UnicodeError:
            logger.debug("Couldn't encode username to {0!r}".format(charset))
            return Failure("incompatible-charset")

        username = _quote(username)
        params.append(b'username="' + username + b'"')

        cnonce = self.password_manager.generate_nonce().encode(charset)
        cnonce = _quote(cnonce)
        params.append(b'cnonce="' + cnonce + b'"')

        params.append(b'nonce="' + nonce + b'"')

        self.nonce_count += 1

        nonce_count = "{0:08x}".format(self.nonce_count).encode("us-ascii")
        params.append(b'nc=' + nonce_count)

        params.append(b'qop=auth')

        serv_type = self.password_manager.get_serv_type().encode("us-ascii")
        host = self.password_manager.get_serv_host().encode("idna")
        serv_name = self.password_manager.get_serv_name().encode("idna")

        if serv_name and serv_name != host:
            digest_uri = b"/".join((serv_type, host, serv_name))
        else:
            digest_uri = b"/".join((serv_type, host))

        digest_uri = _quote(digest_uri)
        params.append(b'digest-uri="' + digest_uri + b'"')

        if self.authzid:
            try:
                authzid = self.authzid.encode(charset)
            except UnicodeError:
                logger.debug("Couldn't encode authzid to {0!r}".format(charset))
                return Failure("incompatible-charset")
            authzid = _quote(authzid)
        else:
            authzid = b""

        if self.pformat == "md5:user:realm:pass":
            urp_hash = a2b_hex(self.password)
        else:
            try:
                epasswd = self.password.encode(charset)
            except UnicodeError:
                logger.debug("Couldn't encode password to {0!r}" 
                                                            .format(charset))
                return Failure("incompatible-charset")
            logger.debug("Encoded password: {0!r}".format(epasswd))
            urp_hash = _make_urp_hash(username, realm, epasswd)

        response = _compute_response(urp_hash, nonce, cnonce, nonce_count,
                                                        authzid, digest_uri)
        self.response_auth = _compute_response_auth(urp_hash, nonce, cnonce,
                                            nonce_count, authzid, digest_uri)
        params.append(b'response=' + response)
        if authzid:
            params.append(b'authzid="' + authzid + b'"')
        return Response(b",".join(params))

    def _get_realm(self, realms, charset):
        """Choose a realm from the list specified by the server.

        :Parameters:
            - `realms`: the realm list.
            - `charset`: encoding of realms on the list.
        :Types:
            - `realms`: `list` of `bytes`
            - `charset`: `bytes`

        :return: the realm chosen or a failure indicator.
        :returntype: `bytes` or `Failure`"""
        if realms:
            realms = [str(r, charset) for r in realms]
            realm = self.password_manager.choose_realm(realms)
        else:
            realm = self.password_manager.choose_realm([])
        if realm is not None:
            self.realm = realm
            try:
                realm = realm.encode(charset)
            except UnicodeError:
                logger.debug("Couldn't encode realm from utf-8 to {0!r}"
                                                            .format(charset))
                return Failure("incompatible-charset")
        return realm

    def _final_challenge(self, challenge):
        """Process the second challenge from the server and return the response.

        :Parameters:
            - `challenge`: the challenge from server.
        :Types:
            - `challenge`: `bytes`

        :return: the response or a failure indicator.
        :returntype: `sasl.Response` or `sasl.Failure`"""
        if self.rspauth_checked:
            return Failure("extra-challenge")
        challenge = challenge.split(b'\x00')[0]
        rspauth = None
        while challenge:
            match = PARAM_RE.match(challenge)
            if not match:
                logger.debug("Challenge syntax error: {0!r}".format(challenge))
                return Failure("bad-challenge")
            challenge = match.group("rest")
            var = match.group("var")
            val = match.group("val")
            logger.debug("{0!r}: {1!r}".format(var, val))
            if var == b"rspauth":
                rspauth = val
        if not rspauth:
            logger.debug("Final challenge without rspauth")
            return Failure("bad-success")
        if rspauth == self.response_auth:
            self.rspauth_checked = True
            return Response(b"")
        else:
            logger.debug("Wrong rspauth value - peer is cheating?")
            logger.debug("my rspauth: {0!r}".format(self.response_auth))
            return Failure("bad-success")

    def finish(self, data):
        """Process success indicator from the server.

        Process any addiitional data passed with the success.
        Fail if the server was not authenticated.

        :Parameters:
            - `data`: an optional additional data with success.
        :Types:
            - `data`: `bytes`

        :return: success or failure indicator.
        :returntype: `sasl.Success` or `sasl.Failure`"""
        if not self.response_auth:
            logger.debug("Got success too early")
            return Failure("bad-success")
        if self.rspauth_checked:
            return Success(self.username, self.realm, self.authzid)
        else:
            ret = self._final_challenge(data)
            if isinstance(ret, Failure):
                return ret
            if self.rspauth_checked:
                return Success(self.username, self.realm, self.authzid)
            else:
                logger.debug("Something went wrong when processing additional"
                                                        " data with success?")
                return Failure("bad-success")

@sasl_mechanism("DIGEST-MD5", 70)
class DigestMD5ServerAuthenticator(ServerAuthenticator):
    """Provides DIGEST-MD5 SASL authentication for a server.
    """
    def __init__(self, password_manager):
        """Initialize a `DigestMD5ServerAuthenticator` object.

        :Parameters:
            - `password_manager`: name of the password manager object providing
              authentication credential verification.
        :Types:
            - `password_manager`: `PasswordManager`"""
        ServerAuthenticator.__init__(self, password_manager)
        self.nonce = None
        self.username = None
        self.realm = None
        self.authzid = None
        self.done = None
        self.last_nonce_count = None

    def start(self, response):
        """Start the authentication process.

        :Parameters:
            - `response`: the initial response from the client (empty for
              DIGEST-MD5).
        :Types:
            - `response`: `bytes`

        :return: a challenge, a success indicator or a failure indicator.
        :returntype: `sasl.Challenge`, `sasl.Success` or `sasl.Failure`"""
        _unused = response
        self.last_nonce_count = 0
        params = []
        realms = self.password_manager.get_realms()
        if realms:
            self.realm = _quote(realms[0])
            for realm in realms:
                realm = _quote(realm)
                params.append(b'realm="' + realm + b'"')
        else:
            self.realm = None
        nonce = _quote(self.password_manager.generate_nonce())
        self.nonce = nonce
        params.append(b'nonce="' + nonce + b'"')
        params.append(b'qop="auth"')
        params.append(b'charset=utf-8')
        params.append(b'algorithm=md5-sess')
        self.authzid = None
        self.done = False
        return Challenge(b",".join(params))

    def response(self, response):
        """Process a client reponse.

        :Parameters:
            - `response`: the response from the client.
        :Types:
            - `response`: `bytes`

        :return: a challenge, a success indicator or a failure indicator.
        :returntype: `sasl.Challenge`, `sasl.Success` or `sasl.Failure`"""
        if self.done:
            return Success(self.username, self.realm, self.authzid)
        if not response:
            return Failure("not-authorized")
        return self._parse_response(response)

    def _parse_response(self, response):
        """Parse a client reponse and pass to further processing.

        :Parameters:
            - `response`: the response from the client.
        :Types:
            - `response`: `bytes`

        :return: a challenge, a success indicator or a failure indicator.
        :returntype: `sasl.Challenge`, `sasl.Success` or `sasl.Failure`"""
        # pylint: disable-msg=R0912
        
        # workaround for some SASL implementations
        response = response.split(b'\x00')[0]

        if self.realm:
            realm = self.realm.encode("utf-8")
            realm = _quote(realm)
        else:
            realm = None

        username = None
        cnonce = None
        digest_uri = None
        response_val = None
        authzid = None
        nonce_count = None
        while response:
            match = PARAM_RE.match(response)
            if not match:
                logger.debug("Response syntax error: {0!r}".format(response))
                return Failure("not-authorized")
            response = match.group("rest")
            var = match.group("var")
            val = match.group("val")
            logger.debug("{0!r}: {0!r}".format(var, val))
            if var == b"realm":
                realm = val[1:-1].decode("utf-8")
            elif var == b"cnonce":
                if cnonce:
                    logger.debug("Duplicate cnonce")
                    return Failure("not-authorized")
                cnonce = val[1:-1]
            elif var == b"qop":
                if val != b'auth':
                    logger.debug("qop other then 'auth'")
                    return Failure("not-authorized")
            elif var == b"digest-uri":
                digest_uri = val[1:-1]
            elif var == b"authzid":
                authzid = val[1:-1].decode("utf-8")
            elif var == b"username":
                username = val[1:-1].decode("utf-8")
            elif var == b"response":
                response_val = val
            elif var == b"nc":
                nonce_count = val
                self.last_nonce_count += 1
                if int(nonce_count) != self.last_nonce_count:
                    logger.debug("bad nonce: {0!r} != {1!r}"
                            .format(nonce_count, self.last_nonce_count))
                    return Failure("not-authorized")
        return self._check_params(username, realm, cnonce, digest_uri,
                                        response_val, authzid, nonce_count)

    def _check_params(self, username, realm, cnonce, digest_uri, response_val,
                                                        authzid, nonce_count):
        """Check parameters of a client reponse and pass them to further
        processing.

        :Parameters:
            - `username`: user name.
            - `realm`: realm.
            - `cnonce`: cnonce value.
            - `digest_uri`: digest-uri value.
            - `response_val`: response value computed by the client.
            - `authzid`: authorization id.
            - `nonce_count`: nonce count value.
        :Types:
            - `username`: `bytes`
            - `realm`: `bytes`
            - `cnonce`: `bytes`
            - `digest_uri`: `bytes`
            - `response_val`: `bytes`
            - `authzid`: `bytes`
            - `nonce_count`: `int`

        :return: a challenge, a success indicator or a failure indicator.
        :returntype: `sasl.Challenge`, `sasl.Success` or `sasl.Failure`"""
        # pylint: disable-msg=R0913
        if not cnonce:
            logger.debug("Required 'cnonce' parameter not given")
            return Failure("not-authorized")
        if not response_val:
            logger.debug("Required 'response' parameter not given")
            return Failure("not-authorized")
        if not username:
            logger.debug("Required 'username' parameter not given")
            return Failure("not-authorized")
        if not digest_uri:
            logger.debug("Required 'digest_uri' parameter not given")
            return Failure("not-authorized")
        if not nonce_count:
            logger.debug("Required 'nc' parameter not given")
            return Failure("not-authorized")
        return self._make_final_challenge(username, realm, cnonce, digest_uri,
                response_val, authzid, nonce_count)

    def _make_final_challenge(self, username, realm, cnonce, digest_uri,
                                        response_val, authzid, nonce_count):
        """Send the second challenge in reply to the client response.

        :Parameters:
            - `username`: user name.
            - `realm`: realm.
            - `cnonce`: cnonce value.
            - `digest_uri`: digest-uri value.
            - `response_val`: response value computed by the client.
            - `authzid`: authorization id.
            - `nonce_count`: nonce count value.
        :Types:
            - `username`: `str`
            - `realm`: `str`
            - `cnonce`: `bytes`
            - `digest_uri`: `bytes`
            - `response_val`: `bytes`
            - `authzid`: `str`
            - `nonce_count`: `int`

        :return: a challenge, a success indicator or a failure indicator.
        :returntype: `sasl.Challenge`, `sasl.Success` or `sasl.Failure`"""
        # pylint: disable-msg=R0912,R0913,R0914
        username_uq = username.replace('\\', '')
        if authzid:
            authzid_uq = authzid.replace('\\', '')
        else:
            authzid_uq = None
        if realm:
            realm_uq = realm.replace('\\', '')
        else:
            realm_uq = None
        digest_uri_uq = digest_uri.replace('\\','')
        self.username = username_uq
        self.realm = realm_uq
        password, pformat = self.password_manager.get_password(
                    username_uq, realm_uq, ("plain", "md5:user:realm:pass"))
        if pformat == "md5:user:realm:pass":
            urp_hash = password.a2b_hex()
        elif pformat == "plain":
            urp_hash = _make_urp_hash(username.encode("utf-8"),
                                        realm.encode("utf-8"),
                                        password.encode("utf-8"))
        else:
            logger.debug("Couldn't get password.")
            return Failure("not-authorized")
        valid_response = _compute_response(urp_hash, self.nonce, cnonce,
                                            nonce_count, authzid, digest_uri)
        if response_val != valid_response:
            logger.debug("Response mismatch: {0!r} != {1!r}".format(
                                                response_val, valid_response))
            return Failure("not-authorized")
        fields = digest_uri_uq.split(b"/")
        if len(fields) == 3:
            serv_type, host, serv_name = fields
        elif len(fields) == 2:
            serv_type, host = fields
            serv_name = None
        else:
            logger.debug("Bad digest_uri: {0!r}".format(digest_uri_uq))
            return Failure("not-authorized")
        info = {}
        info["mechanism"] = "DIGEST-MD5"
        info["username"] = username_uq
        info["serv-type"] = serv_type.decode("utf-8")
        info["host"] = host.decode("idna")
        if serv_name is not None:
            info["serv-name"] = serv_name.decode("idna")
        else:
            info["serv-name"] = None
        if self.password_manager.check_authzid(authzid_uq, info):
            rspauth = _compute_response_auth(urp_hash, self.nonce, cnonce,
                                            nonce_count, authzid, digest_uri)
            self.authzid = authzid
            self.done = True
            return Challenge(b"rspauth=" + rspauth)
        else:
            logger.debug("Authzid check failed")
            return Failure("invalid_authzid")

# vi: sts=4 et sw=4
