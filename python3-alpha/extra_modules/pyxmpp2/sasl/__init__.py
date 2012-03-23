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
"""SASL authentication implementaion for PyXMPP.

Normative reference:
  - `RFC 4422 <http://www.ietf.org/rfc/rfc4422.txt>`__
"""



__docformat__ = "restructuredtext en"

from .core import Reply, Response, Challenge, Success, Failure, PasswordManager
from .core import CLIENT_MECHANISMS, SECURE_CLIENT_MECHANISMS
from .core import SERVER_MECHANISMS, SECURE_SERVER_MECHANISMS
from .core import CLIENT_MECHANISMS_D, SERVER_MECHANISMS_D

from . import plain
from . import external
from . import digest_md5

try:
    from . import gssapi
except ImportError:
    pass # Kerberos not available

def client_authenticator_factory(mechanism, password_manager):
    """Create a client authenticator object for given SASL mechanism and
    password manager.

    :Parameters:
        - `mechanism`: name of the SASL mechanism ("PLAIN", "DIGEST-MD5" or
          "GSSAPI").
        - `password_manager`: name of the password manager object providing
          authentication credentials.
    :Types:
        - `mechanism`: `str`
        - `password_manager`: `PasswordManager`

    :raises `KeyError`: if no client authenticator is available for this
              mechanism

    :return: new authenticator.
    :returntype: `sasl.core.ClientAuthenticator`"""
    authenticator = CLIENT_MECHANISMS_D[mechanism]
    return authenticator(password_manager)

def server_authenticator_factory(mechanism, password_manager):
    """Create a server authenticator object for given SASL mechanism and
    password manager.

    :Parameters:
        - `mechanism`: name of the SASL mechanism ("PLAIN", "DIGEST-MD5" or "GSSAPI").
        - `password_manager`: name of the password manager object to be used
          for authentication credentials verification.
    :Types:
        - `mechanism`: `str`
        - `password_manager`: `PasswordManager`

    :raises `KeyError`: if no server authenticator is available for this
              mechanism

    :return: new authenticator.
    :returntype: `sasl.core.ServerAuthenticator`"""
    authenticator = SERVER_MECHANISMS_D[mechanism]
    return authenticator(password_manager)

# vi: sts=4 et sw=4
