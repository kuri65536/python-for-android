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

"""Utility functions for the pyxmpp package."""



__docformat__ = "restructuredtext en"

def xml_elements_equal(element1, element2, ignore_level1_cdata = False):
    """Check if two XML elements are equal.

    :Parameters:
        - `element1`: the first element to compare
        - `element2`: the other element to compare
        - `ignore_level1_cdata`: if direct text children of the elements
          should be ignored for the comparision
    :Types:
        - `element1`: :etree:`ElementTree.Element`
        - `element2`: :etree:`ElementTree.Element`
        - `ignore_level1_cdata`: `bool`

    :Returntype: `bool`
    """
    # pylint: disable-msg=R0911
    if None in (element1, element2) or element1.tag != element2.tag:
        return False
    attrs1 = list(element1.items())
    attrs1.sort()
    attrs2 = list(element2.items())
    attrs2.sort()

    if not ignore_level1_cdata:
        if element1.text != element2.text:
            return False

    if attrs1 != attrs2:
        return False

    if len(element1) != len(element2):
        return False
    for child1, child2 in zip(element1, element2):
        if child1.tag != child2.tag:
            return False
        if not ignore_level1_cdata:
            if element1.text != element2.text:
                return False
        if not xml_elements_equal(child1, child2):
            return False
    return True

import time
import datetime

_MINUTE = datetime.timedelta(minutes = 1)
_NULLDELTA = datetime.timedelta()

def datetime_utc_to_local(utc):
    """
    An ugly hack to convert naive :std:`datetime.datetime` object containing
    UTC time to a naive :std:`datetime.datetime` object with local time.
    It seems standard Python 2.3 library doesn't provide any better way to
    do that.
    """
    # pylint: disable-msg=C0103
    ts = time.time()
    cur = datetime.datetime.fromtimestamp(ts)
    cur_utc = datetime.datetime.utcfromtimestamp(ts)

    offset = cur - cur_utc
    t = utc

    d = datetime.timedelta(hours = 2)
    while d > _MINUTE:
        local = t + offset
        tm = local.timetuple()
        tm = tm[0:8] + (0, )
        ts = time.mktime(tm)
        u = datetime.datetime.utcfromtimestamp(ts)
        diff = u - utc
        if diff < _MINUTE and diff > -_MINUTE:
            break
        if diff > _NULLDELTA:
            offset -= d
        else:
            offset += d
        d //= 2
    return local

def datetime_local_to_utc(local):
    """
    Simple function to convert naive :std:`datetime.datetime` object containing
    local time to a naive :std:`datetime.datetime` object with UTC time.
    """
    timestamp = time.mktime(local.timetuple())
    return datetime.datetime.utcfromtimestamp(timestamp)

# vi: sts=4 et sw=4
