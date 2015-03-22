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

"""jid -- XMPP address handling

Normative reference:
  - `RFC 6122 <http://xmpp.org/rfcs/rfc6122.html>`__
"""



__docformat__ = "restructuredtext en"

import weakref
import warnings
import socket

from encodings import idna

from .xmppstringprep import NODEPREP, RESOURCEPREP
from .exceptions import JIDError

def are_domains_equal(domain1, domain2):
    """Compare two International Domain Names.

    :Parameters:
        - `domain1`: domains name to compare
        - `domain2`: domains name to compare
    :Types:
        - `domain1`: `str`
        - `domain2`: `str`
    
    :return: True `domain1` and `domain2` are equal as domain names."""

    domain1 = domain1.encode("idna")
    domain2 = domain2.encode("idna")
    return domain1.lower() == domain2.lower()

class JID(object):
    """JID.

    :Ivariables:
        - `local`: localpart of the JID
        - `domain`: domainpart of the JID
        - `resource`: resourcepart of the JID

    JID objects are immutable. They are also cached for better performance.
    """
    cache = weakref.WeakValueDictionary()
    __slots__ = ("local", "domain", "resource", "__weakref__",)
    def __new__(cls, local_or_jid = None, domain = None, resource = None,
                                                                check = True):
        """Create a new JID object or take one from the cache.

        :Parameters:
            - `local_or_jid`: localpart of the JID, JID object to copy, or
              Unicode representation of the JID.
            - `domain`: domain part of the JID
            - `resource`: resource part of the JID
            - `check`: if `False` then JID is not checked for specifiaction
              compliance.
        """

        if isinstance(local_or_jid, JID):
            return local_or_jid

        if domain is None and resource is None:
            obj = cls.cache.get(str(local_or_jid))
            if obj:
                return obj
            
        obj = object.__new__(cls)

        if local_or_jid:
            local_or_jid = str(local_or_jid)
        if (local_or_jid and not domain and not resource):
            local, domain, resource = cls.__from_unicode(local_or_jid)
            cls.cache[local_or_jid] = obj
        else:
            if domain is None and resource is None:
                raise JIDError("At least domain must be given")
            if check:
                local = cls.__prepare_local(local_or_jid)
                domain = cls.__prepare_domain(domain)
                resource = cls.__prepare_resource(resource)
            else:
                local = local_or_jid
        object.__setattr__(obj, "local", local)
        object.__setattr__(obj, "domain", domain)
        object.__setattr__(obj, "resource", resource)
        return obj
    
    def __setattr__(self, name, value):
        raise RuntimeError("JID objects are immutable!")

    def __attribute_declarations__(self):
        # to make pylint happy
        self.local = ""
        self.domain = ""
        self.resource = ""

    @classmethod
    def __from_unicode(cls, data, check = True):
        """Return jid tuple from an Unicode string.

        :Parameters:
            - `data`: the JID string
            - `check`: when `False` then the JID is not checked for
              specification compliance.
              
        :Return: (localpart, domainpart, resourcepart) tuple"""
        parts1 = data.split("/", 1)
        parts2 = parts1[0].split("@", 1)
        if len(parts2) == 2:
            local = parts2[0]
            domain = parts2[1]
            if check:
                local = cls.__prepare_local(local)
                domain = cls.__prepare_domain(domain)
        else:
            local = None
            domain = parts2[0]
            if check:
                domain = cls.__prepare_domain(domain)
        if len(parts1) == 2:
            resource = parts1[1]
            if check:
                resource = cls.__prepare_resource(parts1[1])
        else:
            resource = None
        if not domain:
            raise JIDError("Domain is required in JID.")
        return (local, domain, resource)

    @staticmethod
    def __prepare_local(data):
        """Prepare localpart of the JID

        :Parameters:
            - `data`: localpart of the JID
        :Types:
            - `data`: `str`

        :raise JIDError: if the local name is too long.
        :raise pyxmpp.xmppstringprep.StringprepError: if the
            local name fails Nodeprep preparation."""
        if not data:
            return None
        data = str(data)
        local = NODEPREP.prepare(data)
        if len(local.encode("utf-8")) > 1023:
            raise JIDError("Node name too long")
        return local

    @staticmethod
    def __prepare_domain(data):
        """Prepare domainpart of the JID.

        :Parameters:
            - `data`: Domain part of the JID
        :Types:
            - `data`: `str`

        :raise JIDError: if the domain name is too long."""
        if not data:
            raise JIDError("Domain must be given")
        data = data.rstrip(".")
        if not data:
            raise JIDError("Domain must be given")
        if '[' in data:
            if data[0] == '[' and data[-1] == ']':
                try:
                    # decode...
                    addr = socket.inet_pton(socket.AF_INET6, data[1:-1])
                    # ...and normalize
                    return "[{0}]".format(
                                    socket.inet_ntop(socket.AF_INET6, addr))
                except socket.error:
                    raise JIDError("Invalid IPv6 literal in JID domainpart")
            else:
                raise JIDError("Invalid use of '[' or ']' in JID domainpart")
        elif data[0].isdigit() and data[-1].isdigit():
            try:
                # try to decode as IPv4...
                addr = socket.inet_pton(socket.AF_INET, data)
                # ...and normalize
                return socket.inet_ntop(socket.AF_INET, addr)
            except socket.error:
                pass
        data = str(data)
        labels = data.split(".")
        labels = [idna.nameprep(label) for label in labels]
        domain = ".".join(labels)
        if len(domain.encode("utf-8")) > 1023:
            raise JIDError("Domain name too long")
        return domain

    @staticmethod
    def __prepare_resource(data):
        """Prepare the resourcepart of the JID.

        :Parameters:
            - `data`: Resourcepart of the JID

        :raise JIDError: if the resource name is too long.
        :raise pyxmpp.xmppstringprep.StringprepError: if the
            resourcepart fails Resourceprep preparation."""
        if not data:
            return None
        data = str(data)
        resource = RESOURCEPREP.prepare(data)
        if len(resource.encode("utf-8")) > 1023:
            raise JIDError("Resource name too long")
        return resource

    def __str__(self):
        return self.as_unicode()

    def __repr__(self):
        return "JID(%r)" % (self.as_unicode())

    def as_utf8(self):
        """UTF-8 encoded JID representation.

        :return: UTF-8 encoded JID."""
        return self.as_unicode().encode("utf-8")

    def as_string(self):
        """UTF-8 encoded JID representation.

        *Deprecated* Always use Unicode objects, or `as_utf8` if you really want.

        :return: UTF-8 encoded JID."""
        warnings.warn("JID.as_string() is deprecated. Use unicode()"
                " or `as_utf8` instead.", DeprecationWarning, stacklevel=1)
        return self.as_utf8()

    def as_unicode(self):
        """Unicode string JID representation.

        :return: JID as Unicode string."""
        result = self.domain
        if self.local:
            result = self.local + '@' + result
        if self.resource:
            result = result + '/' + self.resource
        if result not in JID.cache:
            JID.cache[result] = self
        return result

    def bare(self):
        """Make bare JID made by removing resource from current `self`.

        :return: new JID object without resource part."""
        return JID(self.local, self.domain, check = False)

    def __eq__(self, other):
        if other is None:
            return False
        elif type(other) in (str, str):
            try:
                other = JID(other)
            except Exception:
                return False
        elif not isinstance(other, JID):
            return False

        return (self.local == other.local
            and are_domains_equal(self.domain, other.domain)
            and self.resource == other.resource)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        uni = self.as_unicode()
        return cmp(uni, other)

    def __hash__(self):
        return hash(self.local) ^ hash(self.domain) ^ hash(self.resource)

# vi: sts=4 et sw=4
