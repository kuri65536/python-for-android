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
# pylint treats "import stringprep" like depreciated "import string"
# pylint: disable-msg=W0402

"""Nodeprep and resourceprep stringprep profiles.

Normative reference:
  - `RFC 6122 <http://xmpp.org/rfcs/rfc6122.html>`__
  - `RFC 3454 <http://tools.ietf.org/html/rfc3454>`__
"""



__docformat__ = "restructuredtext en"

import stringprep
import unicodedata
from .exceptions import StringprepError

def b1_mapping(char):
    """Do RFC 3454 B.1 table mapping.

    :Parameters:
        - `char`: Unicode character to map.

    :returns: u"" if there is `char` code in the table, `None` otherwise.
    """
    if stringprep.in_table_b1(char):
        return ""
    else:
        return None

def nfkc(data):
    """Do NFKC normalization of Unicode data.

    :Parameters:
        - `data`: list of Unicode characters or Unicode string.

    :return: normalized Unicode string."""
    if isinstance(data, list):
        data = "".join(data)
    return unicodedata.normalize("NFKC", data)

class Profile(object):
    """Base class for stringprep profiles.
    """
    cache_items = []
    def __init__(self, unassigned, mapping, normalization, prohibited,
                                                                bidi = True):
        """Initialize Profile object.

        :Parameters:
            - `unassigned`: the lookup table with unassigned codes
            - `mapping`: the lookup table with character mappings
            - `normalization`: the normalization function
            - `prohibited`: the lookup table with prohibited characters
            - `bidi`: if True then bidirectional checks should be done
        :Types:
            - `unassigned`: tuple of functions
            - `mapping`: tuple of functions
            - `normalization`: tuple of functions
            - `prohibited`: tuple of functions
            - `bidi`: `bool`
        """
        # pylint: disable-msg=R0913
        self.unassigned = unassigned
        self.mapping = mapping
        self.normalization = normalization
        self.prohibited = prohibited
        self.bidi = bidi
        self.cache = {}

    def prepare(self, data):
        """Complete string preparation procedure for 'stored' strings.
        (includes checks for unassigned codes)

        :Parameters:
            - `data`: Unicode string to prepare.

        :return: prepared string

        :raise StringprepError: if the preparation fails
        """
        ret = self.cache.get(data)
        if ret is not None:
            return ret
        result = self.map(data)
        if self.normalization:
            result = self.normalization(result)
        result = self.prohibit(result)
        result = self.check_unassigned(result)
        if self.bidi:
            result = self.check_bidi(result)
        if isinstance(result, list):
            result = "".join()
        if len(self.cache_items) >= _stringprep_cache_size:
            remove = self.cache_items[: -_stringprep_cache_size // 2]
            for profile, key in remove:
                try:
                    del profile.cache[key]
                except KeyError:
                    pass
            self.cache_items[:] = self.cache_items[
                                                -_stringprep_cache_size // 2 :]
        self.cache_items.append((self, data))
        self.cache[data] = result
        return result

    def prepare_query(self, data):
        """Complete string preparation procedure for 'query' strings.
        (without checks for unassigned codes)

        :Parameters:
            - `data`: Unicode string to prepare.

        :return: prepared string

        :raise StringprepError: if the preparation fails
        """
        data = self.map(data)
        if self.normalization:
            data = self.normalization(data)
        data = self.prohibit(data)
        if self.bidi:
            data = self.check_bidi(data)
        if isinstance(data, list):
            data = "".join(data)
        return data

    def map(self, data):
        """Mapping part of string preparation."""
        result = []
        for char in data:
            ret = None
            for lookup in self.mapping:
                ret = lookup(char)
                if ret is not None:
                    break
            if ret is not None:
                result.append(ret)
            else:
                result.append(char)
        return result

    def prohibit(self, data):
        """Checks for prohibited characters."""
        for char in data:
            for lookup in self.prohibited:
                if lookup(char):
                    raise StringprepError("Prohibited character: {0!r}"
                                                                .format(char))
        return data

    def check_unassigned(self, data):
        """Checks for unassigned character codes."""
        for char in data:
            for lookup in self.unassigned:
                if lookup(char):
                    raise StringprepError("Unassigned character: {0!r}"
                                                                .format(char))
        return data

    @staticmethod
    def check_bidi(data):
        """Checks if sting is valid for bidirectional printing."""
        has_l = False
        has_ral = False
        for char in data:
            if stringprep.in_table_d1(char):
                has_ral = True
            elif stringprep.in_table_d2(char):
                has_l = True
        if has_l and has_ral:
            raise StringprepError("Both RandALCat and LCat characters present")
        if has_ral and (not stringprep.in_table_d1(data[0])
                                    or not stringprep.in_table_d1(data[-1])):
            raise StringprepError("The first and the last character must"
                                                                " be RandALCat")
        return data

NODEPREP_PROHIBITED = set(['"', '&', "'", "/", ":", "<", ">", "@"])

NODEPREP = Profile(
    unassigned = (stringprep.in_table_a1,),
    mapping = (b1_mapping, stringprep.map_table_b2),
    normalization = nfkc,
    prohibited = (  stringprep.in_table_c11, stringprep.in_table_c12, 
                    stringprep.in_table_c21, stringprep.in_table_c22, 
                    stringprep.in_table_c3, stringprep.in_table_c4, 
                    stringprep.in_table_c5, stringprep.in_table_c6, 
                    stringprep.in_table_c7, stringprep.in_table_c8, 
                    stringprep.in_table_c9,
                    lambda x: x in NODEPREP_PROHIBITED ),
    bidi = True)

RESOURCEPREP = Profile(
    unassigned = (stringprep.in_table_a1,),
    mapping = (b1_mapping,),
    normalization = nfkc,
    prohibited = (  stringprep.in_table_c12, stringprep.in_table_c21,
                    stringprep.in_table_c22, stringprep.in_table_c3, 
                    stringprep.in_table_c4, stringprep.in_table_c5, 
                    stringprep.in_table_c6, stringprep.in_table_c7, 
                    stringprep.in_table_c8, stringprep.in_table_c9 ),
    bidi = True)

_stringprep_cache_size = 1000 # pylint: disable-msg=C0103

def set_stringprep_cache_size(size):
    """Modify stringprep cache size.

    :Parameters:
        - `size`: new cache size
    """
    # pylint: disable-msg=W0603
    global _stringprep_cache_size
    _stringprep_cache_size = size
    if len(Profile.cache_items) > size:
        remove = Profile.cache_items[:-size]
        for profile, key in remove:
            try:
                del profile.cache[key]
            except KeyError:
                pass
        Profile.cache_items = Profile.cache_items[-size:]

# vi: sts=4 et sw=4
