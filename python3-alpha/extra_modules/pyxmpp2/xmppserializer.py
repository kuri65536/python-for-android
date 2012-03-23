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

"""XMPP serializer for ElementTree data.

XMPP has specific requirements for XML serialization. Predefined
namespace prefixes must be used, including no prefix for the stanza
namespace (which may be one of, at least, two different namespaces:
'jabber:client' and 'jabber:server')"""



import threading
import re
from xml.sax.saxutils import escape, quoteattr

from .constants import STANZA_NAMESPACES, STREAM_NS, XML_NS

__docformat__ = "restructuredtext en"

STANDARD_PREFIXES = {
        STREAM_NS: 'stream',
        XML_NS: 'xml',
    }

EVIL_CHARACTERS_RE = re.compile(r"[\000-\010\013\014\016-\037]", re.UNICODE)

def remove_evil_characters(data):
    """Remove control characters (not allowed in XML) from a string."""
    return EVIL_CHARACTERS_RE.sub("\ufffd", data)

class XMPPSerializer(object):
    """Implementation of the XMPP serializer.

    Single instance of this class should be used for a single stream and never
    reused. It will keep track of prefixes declared on the root element and 
    used later.
    
    :Ivariables:
        - `stanza_namespace`: the default namespace of the stream
        - `_prefixes`: mapping (prefix -> uri) of known namespace prefixes
        - `_root_prefixes`: prefixes declared on the root element
        - `_head_emitted`: `True` if the stream start tag has been emitted
        - `_next_id`: the next sequence number to be used in auto-generated
          prefixes.
    :Types:
        - `stanza_namespace`: `str`
        - `_prefixes`: `dict`
        - `_root_prefixes`: `dict`
        - `_head_emitted`: `bool`
        - `_next_id`: `int`
    """
    def __init__(self, stanza_namespace, extra_prefixes = None):
        """
        :Parameters:
            - `stanza_namespace`: the default namespace used for XMPP stanzas.
              E.g. 'jabber:client' for c2s connections.
            - `extra_prefixes`: mapping of namespaces to prefixes (not the
              other way) to be used on the stream. These prefixes will be
              declared on the root element and used in all descendants. That
              may be used to optimize the stream for size.
        :Types:
            - `stanza_namespace`: `str`
            - `extra_prefixes`: `str` to `str` mapping.
        """
        self.stanza_namespace = stanza_namespace
        self._prefixes = {}
        if extra_prefixes:
            self._prefixes.update(extra_prefixes)
        self._root_prefixes = None
        self._head_emitted = False
        self._next_id = 1

    def add_prefix(self, namespace, prefix):
        """Add a new namespace prefix.

        If the root element has not yet been emitted the prefix will
        be declared there, otherwise the prefix will be declared on the
        top-most element using this namespace in every stanza.

        :Parameters:
            - `namespace`: the namespace URI
            - `prefix`: the prefix string
        :Types:
            - `namespace`: `str`
            - `prefix`: `str`
        """
        if prefix == "xml" and namespace != XML_NS:
            raise ValueError("Cannot change 'xml' prefix meaning")
        self._prefixes[namespace] = prefix

    def emit_head(self, stream_from, stream_to, stream_id = None, 
                                            version = '1.0', language = None):
        """Return the opening tag of the stream root element.

        :Parameters:
            - `stream_from`: the 'from' attribute of the stream. May be `None`.
            - `stream_to`: the 'to' attribute of the stream. May be `None`.
            - `version`: the 'version' of the stream.
            - `language`: the 'xml:lang' of the stream
        :Types:
            - `stream_from`: `str`
            - `stream_to`: `str`
            - `version`: `str`
            - `language`: `str`
        """
        # pylint: disable-msg=R0913
        self._root_prefixes = dict(STANDARD_PREFIXES)
        self._root_prefixes[self.stanza_namespace] = None
        for namespace, prefix in list(self._root_prefixes.items()):
            if not prefix or prefix == "stream":
                continue
            if namespace in STANDARD_PREFIXES or namespace in STANZA_NAMESPACES:
                continue
            self._root_prefixes[namespace] = prefix
        tag = "<{0}:stream version={1}".format(STANDARD_PREFIXES[STREAM_NS],
                                                        quoteattr(version))
        if stream_from:
            tag += " from={0}".format(quoteattr(stream_from))
        if stream_to:
            tag += " to={0}".format(quoteattr(stream_to))
        if stream_id is not None:
            tag += " id={0}".format(quoteattr(stream_id))
        if language is not None:
            tag += " xml:lang={0}".format(quoteattr(language))
        for namespace, prefix in list(self._root_prefixes.items()):
            if prefix == "xml":
                continue
            if prefix:
                tag += ' xmlns:{0}={1}'.format(prefix, quoteattr(namespace))
            else:
                tag += ' xmlns={1}'.format(prefix, quoteattr(namespace))
        tag += ">"
        self._head_emitted = True
        return tag

    def emit_tail(self):
        """Return the end tag of the stream root element."""
        return "</{0}:stream>".format(self._root_prefixes[STREAM_NS])

    def _split_qname(self, name, is_element):
        """Split an element of attribute qname into namespace and local
        name.

        :Parameters:
            - `name`: element or attribute QName
            - `is_element`: `True` for an element, `False` for an attribute
        :Types:
            - `name`: `str`
            - `is_element`: `bool`
        
        :Return: namespace URI, local name
        :returntype: `str`, `str`"""
        if name.startswith("{"):
            namespace, name = name[1:].split("}", 1)
            if namespace in STANZA_NAMESPACES:
                namespace = self.stanza_namespace
        elif is_element:
            raise ValueError("Element with no namespace: {0!r}".format(name))
        else:
            namespace = None
        return namespace, name

    def _make_prefix(self, declared_prefixes):
        """Make up a new namespace prefix, which won't conflict
        with `_prefixes` and prefixes declared in the current scope.
        
        :Parameters:
            - `declared_prefixes`: namespace to prefix mapping for the current
              scope
        :Types:
            - `declared_prefixes`: `str` to `str` dictionary

        :Returns: a new prefix
        :Returntype: `str`
        """
        used_prefixes = set(self._prefixes.values()) 
        used_prefixes |= set(declared_prefixes.values())
        while True:
            prefix = "ns{0}".format(self._next_id)
            self._next_id += 1
            if prefix not in used_prefixes:
                break
        return prefix

    def _make_prefixed(self, name, is_element, declared_prefixes, declarations):
        """Return namespace-prefixed tag or attribute name.
        
        Add appropriate declaration to `declarations` when neccessary.

        If no prefix for an element namespace is defined, make the elements
        namespace default (no prefix). For attributes, make up a prefix in such
        case.
        
        :Parameters:
            - `name`: QName ('{namespace-uri}local-name')
              to convert
            - `is_element`: `True` for element, `False` for an attribute
            - `declared_prefixes`: mapping of prefixes already declared 
              at this scope
            - `declarations`: XMLNS declarations on the current element.
        :Types:
            - `name`: `str`
            - `is_element`: `bool`
            - `declared_prefixes`: `str` to `str` dictionary
            - `declarations`: `str` to `str` dictionary

        :Returntype: `str`"""
        namespace, name = self._split_qname(name, is_element)
        if namespace is None:
            prefix = None
        elif namespace in declared_prefixes:
            prefix = declared_prefixes[namespace]
        elif namespace in self._prefixes:
            prefix = self._prefixes[namespace]
            declarations[namespace] = prefix
            declared_prefixes[namespace] = prefix
        else:
            if is_element:
                prefix = None
            else:
                prefix = self._make_prefix(declared_prefixes)
            declarations[namespace] = prefix
            declared_prefixes[namespace] = prefix
        if prefix:
            return prefix + ":" + name
        else:
            return name

    @staticmethod
    def _make_ns_declarations(declarations, declared_prefixes):
        """Build namespace declarations and remove obsoleted mappings
        from `declared_prefixes`.

        :Parameters:
            - `declarations`: namespace to prefix mapping of the new
              declarations
            - `declared_prefixes`: namespace to prefix mapping of already
              declared prefixes.
        :Types:
            - `declarations`: `str` to `str` dictionary
            - `declared_prefixes`: `str` to `str` dictionary

        :Return: string of namespace declarations to be used in a start tag
        :Returntype: `str`
        """
        result = []
        for namespace, prefix in list(declarations.items()):
            if prefix:
                result.append(' xmlns:{0}={1}'.format(prefix, quoteattr(
                                                                namespace)))
            else:
                result.append(' xmlns={1}'.format(prefix, quoteattr(
                                                                namespace)))
            for d_namespace, d_prefix in list(declared_prefixes.items()):
                if (not prefix and not d_prefix) or d_prefix == prefix:
                    if namespace != d_namespace:
                        del declared_prefixes[d_namespace]
        return " ".join(result)

    def _emit_element(self, element, level, declared_prefixes):
        """"Recursive XML element serializer.

        :Parameters:
            - `element`: the element to serialize
            - `level`: nest level (0 - root element, 1 - stanzas, etc.)
            - `declared_prefixes`: namespace to prefix mapping of already
              declared prefixes.
        :Types:
            - `element`: :etree:`ElementTree.Element`
            - `level`: `int`
            - `declared_prefixes`: `str` to `str` dictionary

        :Return: serialized element
        :Returntype: `str`
        """
        declarations = {}
        declared_prefixes = dict(declared_prefixes)
        name = element.tag
        prefixed = self._make_prefixed(name, True, declared_prefixes,
                                                                declarations)
        start_tag = "<{0}".format(prefixed)
        end_tag = "</{0}>".format(prefixed)
        for name, value in list(element.items()):
            prefixed = self._make_prefixed(name, False, declared_prefixes,
                                                                declarations)
            start_tag += ' {0}={1}'.format(prefixed, quoteattr(value))

        declarations = self._make_ns_declarations(declarations, 
                                                        declared_prefixes)
        if declarations:
            start_tag += " " + declarations
        children = []
        for child in element:
            children.append(self._emit_element(child, level +1,
                                                        declared_prefixes))
        if not children and not element.text:
            start_tag += "/>"
            end_tag = ""
            text = ""
        else:
            start_tag += ">"
            if level > 0 and element.text:
                text = escape(element.text)
            else:
                text = ""
        if level > 1 and element.tail:
            tail = escape(element.tail)
        else:
            tail = ""
        return start_tag + text + ''.join(children) + end_tag + tail

    def emit_stanza(self, element):
        """"Serialize a stanza.

        Must be called after `emit_head`.

        :Parameters:
            - `element`: the element to serialize
        :Types:
            - `element`: :etree:`ElementTree.Element`

        :Return: serialized element
        :Returntype: `str`
        """
        if not self._head_emitted:
            raise RuntimeError(".emit_head() must be called first.")
        string = self._emit_element(element, level = 1, 
                                    declared_prefixes = self._root_prefixes)
        return remove_evil_characters(string)


# thread local data to store XMPPSerializer instance used by the `serialize`
# function
_THREAD = threading.local()
_THREAD.serializer = None

def serialize(element):
    """Serialize an XMPP element.

    Utility function for debugging or logging.

        :Parameters:
            - `element`: the element to serialize
        :Types:
            - `element`: :etree:`ElementTree.Element`

        :Return: serialized element
        :Returntype: `str`
    """
    if _THREAD.serializer is None:
        _THREAD.serializer = XMPPSerializer("jabber:client")
        _THREAD.serializer.emit_head(None, None)
    return _THREAD.serializer.emit_stanza(element)

# vi: sts=4 et sw=4
