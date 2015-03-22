#
# (C) Copyright 2011 Jacek Konieczny <jajcus@jajcus.net>
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

"""ElementTree API selection.

The rest of PyXMPP2 package imports the ElementTree API from this module.

The actual API can be selected in one of two ways:

By importing this module (before anything else) its :etree:`ElementTree`
variable:

.. python::

    import pyxmpp2.etree
    import xml.etree.cElementTree
    pyxmpp2.etree.ElementTree = xml.etree.cElementTree

Or by setting the 'PYXMPP2_ETREE' environment variable, e.g.::

    $ PYXMPP2_ETREE="xml.etree"

By default the standard Python ElementTree implementation is used
(`xml.etree.ElementTree
<http://docs.python.org/library/xml.etree.elementtree.html>`__)
"""
# pylint: disable=C0103



__docformat__ = "restructuredtext en"

import os
import sys
from abc import ABCMeta

if "PYXMPP2_ETREE" in os.environ:
    ElementTree = __import__(os.environ["PYXMPP2_ETREE"], fromlist=[""])
else:
    from xml.etree import ElementTree # pylint: disable=W0404

class ElementClass(metaclass=ABCMeta):
    """Abstract class used to reference the :etree:`ElementTree.Element`
    object type of the selected Element Tree implementation.
    """
    element_type = None
    @classmethod
    def __subclasshook__(cls, other):
        if cls.element_type is None:
            cls.element_type = type(ElementTree.Element("x"))
        if cls is ElementClass:
            return other is cls.element_type or hasattr(other, "tag")
        return NotImplemented

def element_to_unicode(element):
    """Serialize an XML element into a unicode string.

    This should work the same on Python2 and Python3 and with all
    :etree:`ElementTree` implementations.

    :Parameters:
        - `element`: the XML element to serialize
    :Types:
        - `element`: :etree:`ElementTree.Element`
    """
    if hasattr(ElementTree, 'tounicode'):
        # pylint: disable=E1103
        return ElementTree.tounicode("element")
    elif sys.version_info.major < 3:
        return str(ElementTree.tostring(element))
    else:
        return ElementTree.tostring(element, encoding = "unicode")


