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

"""Base interfaces of PyXMPP2.

:Variables:
    - `NO_CHANGE`: constant used as the default for some function arguments
"""
# pylint: disable-msg=R0201



__docformat__ = "restructuredtext en"

import logging

from abc import ABCMeta, abstractmethod

try:
    # pylint: disable=E0611
    from abc import abstractclassmethod
except ImportError:
    # pylint: disable=C0103
    abstractclassmethod = classmethod

from copy import deepcopy

# pylint: disable=W0611
from .mainloop.interfaces import Event, QUIT, EventHandler, event_handler
# pylint: disable=W0611
from .mainloop.interfaces import TimeoutHandler, timeout_handler

class Resolver(metaclass=ABCMeta):
    """Abstract base class for asynchronous DNS resolvers to be used
    with PyxMPP.
    """

    @abstractmethod
    def resolve_srv(self, domain, service, protocol, callback):
        """Start looking up an SRV record for `service` at `domain`.

        `callback` will be called with a properly sorted list of (hostname,
        port) pairs on success. The list will be empty on error and it will
        contain only (".", 0) when the service is explicitely disabled.

        :Parameters:
            - `domain`: domain name to look up
            - `service`: service name e.g. 'xmpp-client'
            - `protocol`: protocol name, e.g. 'tcp'
            - `callback`: a function to be called with a list of received
              addresses
        :Types:
            - `domain`: `str`
            - `service`: `str`
            - `protocol`: `str`
            - `callback`: function accepting a single argument
        """
        raise NotImplementedError

    @abstractmethod
    def resolve_address(self, hostname, callback, allow_cname = True):
        """Start looking up an A or AAAA record.

        `callback` will be called with a list of IPv4 or IPv6 address literals
        on success. The list will be empty on error.

        :Parameters:
            - `hostname`: the host name to look up
            - `callback`: a function to be called with a list of received
              addresses
            - `allow_cname`: `True` if CNAMEs should be followed
        :Types:
            - `hostname`: `str`
            - `callback`: function accepting a single argument
            - `allow_cname`: `bool`
        """
        raise NotImplementedError

class XMPPTransport(metaclass=ABCMeta):
    """Abstract base class for XMPP transport implementations."""
    
    @abstractmethod
    def set_target(self, stream):
        """Make the `stream` the target for this transport instance.

        The 'stream_start', 'stream_end' and 'stream_element' methods
        of the target will be called when appropriate content is received.

        :Parameters:
            - `stream`: the stream handler to receive stream content
              from the transport
        :Types:
            - `stream`: `StreamBase`
        """
        pass

    @abstractmethod
    def send_stream_head(self, stanza_namespace, stream_from, stream_to,
                        stream_id = None, version = '1.0', language = None):
        """
        Send stream head via the transport.

        :Parameters:
            - `stanza_namespace`: namespace of stream stanzas (e.g.
              'jabber:client')
            - `stream_from`: the 'from' attribute of the stream. May be `None`.
            - `stream_to`: the 'to' attribute of the stream. May be `None`.
            - `version`: the 'version' of the stream.
            - `language`: the 'xml:lang' of the stream
        :Types:
            - `stanza_namespace`: `str`
            - `stream_from`: `str`
            - `stream_to`: `str`
            - `version`: `str`
            - `language`: `str`
        """
        # pylint: disable-msg=R0913
        pass
    
    @abstractmethod
    def restart(self):
        """Restart the stream after SASL or StartTLS handshake.
        
        For the initiator a new call to `send_stream_head` is required too."""
        pass

    @abstractmethod
    def send_stream_tail(self):
        """
        Send stream tail via the transport.
        """
        pass

    @abstractmethod
    def send_element(self, element):
        """
        Send an element via the transport.
        """
        pass

    @abstractmethod
    def is_connected(self):
        """
        Check if the transport is connected.

        :Return: `True` if is connected.
        """
        return False

    @abstractmethod
    def disconnect(self):
        """
        Gracefully disconnect the connection.
        """
        pass

class StanzaRoute:
    """Base class for objects that can send and receive stanzas."""
    # pylint: disable=W0232
    @abstractmethod
    def send(self, stanza):
        """Send stanza through this route."""
        pass

    @abstractmethod
    def uplink_receive(self, stanza):
        """Handle stanza received from 'uplink'."""
        pass

class XMPPFeatureHandler(metaclass=ABCMeta):
    """Base class for objects handling incoming stanzas.

    The subclasses should provide methods decorated with one of:

      - `iq_get_stanza_handler`: for methods handling ``<iq type="get"/>``
        stanzas.
      - `iq_set_stanza_handler`: for methods handling ``<iq type="set"/>``
        stanzas.
      - `message_stanza_handler`: for methods handling ``<message />`` stanzas
      - `presence_stanza_handler`: for methods handling ``<presence />``
        stanzas

    :Ivariables:
        - `stanza_processor`: a stanza processor where this object was
          registered most recently (injected by `StanzaProcessor`)
    :Types:
        - `stanza_processor`: `StanzaProcessor`
    """
    stanza_processor = None

def _iq_handler(iq_type, payload_class, payload_key, usage_restriction):
    """Method decorator generator for decorating <iq type='get'/> stanza
    handler methods in `XMPPFeatureHandler` subclasses.
    
    :Parameters:
        - `payload_class`: payload class expected
        - `payload_key`: payload class specific filtering key
        - `usage_restriction`: optional usage restriction: "pre-auth" or
          "post-auth"
    :Types:
        - `payload_class`: subclass of `StanzaPayload`
        - `usage_restriction`: `str`
    """
    def decorator(func):
        """The decorator"""
        func._pyxmpp_stanza_handled = ("iq", iq_type)
        func._pyxmpp_payload_class_handled = payload_class
        func._pyxmpp_payload_key = payload_key
        func._pyxmpp_usage_restriction = usage_restriction
        return func
    return decorator


def iq_get_stanza_handler(payload_class, payload_key = None, 
                                            usage_restriction = "post-auth"):
    """Method decorator generator for decorating <iq type='get'/> stanza
    handler methods in `XMPPFeatureHandler` subclasses.
    
    :Parameters:
        - `payload_class`: payload class expected
        - `payload_key`: payload class specific filtering key
        - `usage_restriction`: optional usage restriction: "pre-auth" or
          "post-auth"
    :Types:
        - `payload_class`: subclass of `StanzaPayload`
        - `usage_restriction`: `str`
    """
    return _iq_handler("get", payload_class, payload_key, usage_restriction)

def iq_set_stanza_handler(payload_class, payload_key = None, 
                                            usage_restriction = "post-auth"):
    """Method decorator generator for decorating <iq type='set'/> stanza
    handler methods in `XMPPFeatureHandler` subclasses.
    
    :Parameters:
        - `payload_class`: payload class expected
        - `payload_key`: payload class specific filtering key
        - `usage_restriction`: optional usage restriction: "pre-auth" or
          "post-auth"
    :Types:
        - `payload_class`: subclass of `StanzaPayload`
        - `usage_restriction`: `str`
    """
    return _iq_handler("set", payload_class, payload_key, usage_restriction)

def _stanza_handler(element_name, stanza_type, payload_class, payload_key,
                                                            usage_restriction):
    """Method decorator generator for decorating <message/> or <presence/>
    stanza handler methods in `XMPPFeatureHandler` subclasses.
    
    :Parameters:
        - `element_name`: "message" or "presence"
        - `stanza_type`: expected value of the 'type' attribute of the stanza
        - `payload_class`: payload class expected
        - `payload_key`: payload class specific filtering key
        - `usage_restriction`: optional usage restriction: "pre-auth" or
          "post-auth"
    :Types:
        - `element_name`: `str`
        - `stanza_type`: `str`
        - `payload_class`: subclass of `StanzaPayload`
        - `usage_restriction`: `str`
    """
    def decorator(func):
        """The decorator"""
        func._pyxmpp_stanza_handled = (element_name, stanza_type)
        func._pyxmpp_payload_class_handled = payload_class
        func._pyxmpp_payload_key = payload_key
        func._pyxmpp_usage_restriction = usage_restriction
        return func
    return decorator

def message_stanza_handler(stanza_type = None, payload_class = None,
                        payload_key = None, usage_restriction = "post-auth"):
    """Method decorator generator for decorating <message/> 
    stanza handler methods in `XMPPFeatureHandler` subclasses.
    
    :Parameters:
        - `payload_class`: payload class expected
        - `stanza_type`: expected value of the 'type' attribute of the stanza.
          `None` means all types except 'error'
        - `payload_key`: payload class specific filtering key
        - `usage_restriction`: optional usage restriction: "pre-auth" or
          "post-auth"
    :Types:
        - `payload_class`: subclass of `StanzaPayload`
        - `stanza_type`: `str`
        - `usage_restriction`: `str`
    """
    if stanza_type is None:
        stanza_type = "normal"
    return _stanza_handler("message", stanza_type, payload_class, payload_key,
                                                            usage_restriction)
 
def presence_stanza_handler(stanza_type = None, payload_class = None,
                        payload_key = None, usage_restriction = "post-auth"):
    """Method decorator generator for decorating <presence/> 
    stanza handler methods in `XMPPFeatureHandler` subclasses.
    
    :Parameters:
        - `payload_class`: payload class expected
        - `stanza_type`: expected value of the 'type' attribute of the stanza.
        - `payload_key`: payload class specific filtering key
        - `usage_restriction`: optional usage restriction: "pre-auth" or
          "post-auth"
    :Types:
        - `payload_class`: subclass of `StanzaPayload`
        - `stanza_type`: `str`
        - `usage_restriction`: `str`
    """
    return _stanza_handler("presence", stanza_type, payload_class, payload_key,
                                                            usage_restriction)

class StanzaPayload(metaclass=ABCMeta):
    """Abstract base class for stanza payload objects.

    Subclasses are used to encapsulate stanza payload data
    and to reference payload type in stanza handlers or when
    requesting particular payload from a stanza.
    """

    @abstractclassmethod
    def from_xml(cls, element):
        """Create a `cls` instance from an XML element.

        :Parameters:
            - `element`: the XML element
        :Types:
            - `element`: :etree:`ElementTree.Element`
        """
        # pylint: disable=E0213
        raise NotImplementedError

    @abstractmethod
    def as_xml(self):
        """Return the XML representation of the payload.

        :returntype: :etree:`ElementTree.Element`
        """
        raise NotImplementedError

    def copy(self):
        """Return a deep copy of self."""
        return deepcopy(self)

    @property
    def handler_key(self):
        """Defines a key which may be used when registering handlers
        for stanzas with this payload."""
        # pylint: disable-msg=R0201
        return None

def payload_element_name(element_name):
    """Class decorator generator for decorationg
    `StanzaPayload` subclasses.
    
    :Parameters:
        - `element_name`: XML element qname handled by the class
    :Types:
        - `element_name`: `str`
    """
    def decorator(klass):
        """The payload_element_name decorator."""
        # pylint: disable-msg=W0212,W0404
        from .stanzapayload import STANZA_PAYLOAD_CLASSES
        from .stanzapayload import STANZA_PAYLOAD_ELEMENTS
        if hasattr(klass, "_pyxmpp_payload_element_name"):
            klass._pyxmpp_payload_element_name.append(element_name)
        else:
            klass._pyxmpp_payload_element_name = [element_name]
        if element_name in STANZA_PAYLOAD_CLASSES:
            logger = logging.getLogger('pyxmpp.payload_element_name')
            logger.warning("Overriding payload class for {0!r}".format(
                                                                element_name))
        STANZA_PAYLOAD_CLASSES[element_name] = klass
        STANZA_PAYLOAD_ELEMENTS[klass].append(element_name)
        return klass
    return decorator


class StreamFeatureHandled(object):
    """Object returned by a stream feature handler for recognized and handled
    features.
    """
    # pylint: disable-msg=R0903
    def __init__(self, feature_name, mandatory = False):
        self.feature_name = feature_name
        self.mandatory = mandatory
    def __repr__(self):
        if self.mandatory:
            return "StreamFeatureHandled({0!r}, mandatory = True)".format(
                                                            self.feature_name)
        else:
            return "StreamFeatureHandled({0!r})".format(self.feature_name)
    def __str__(self):
        return self.feature_name

class StreamFeatureNotHandled(object):
    """Object returned by a stream feature handler for recognized,
    but unhandled features.
    """
    # pylint: disable-msg=R0903
    def __init__(self, feature_name, mandatory = False):
        self.feature_name = feature_name
        self.mandatory = mandatory
    def __repr__(self):
        if self.mandatory:
            return "StreamFeatureNotHandled({0!r}, mandatory = True)".format(
                                                            self.feature_name)
        else:
            return "StreamFeatureNotHandled({0!r})".format(self.feature_name)
    def __str__(self):
        return self.feature_name

class StreamFeatureHandler(metaclass=ABCMeta):
    """Base class for stream feature handlers.

    The `handle_stream_features` and `make_stream_features` should
    process and populate the ``<stream::features/>`` element as needed.

    Other methods, decorated with the `stream_element_handler` decorated,
    will be called to handle matching stream element.
    """
    def handle_stream_features(self, stream, features):
        """Handle features announced by the stream peer.

        [initiator only]

        :Parameters:
            - `stream`: the stream
            - `features`: the features element just received
        :Types:
            - `stream`: `StreamBase`
            - `features`: :etree:`ElementTree.Element`

        :Return: 
            - `StreamFeatureHandled` instance if a feature was recognized and
              handled
            - `StreamFeatureNotHandled` instance if a feature was recognized
              but not handled
            - `None` if no feature was recognized
        """
        # pylint: disable-msg=W0613,R0201
        return False

    def make_stream_features(self, stream, features):
        """Update the features element announced by the stream.

        [receiver only]

        :Parameters:
            - `stream`: the stream
            - `features`: the features element about to be sent
        :Types:
            - `stream`: `StreamBase`
            - `features`: :etree:`ElementTree.Element`
        """
        # pylint: disable-msg=W0613,R0201
        return False

def stream_element_handler(element_name, usage_restriction = None):
    """Method decorator generator for decorating stream element
    handler methods in `StreamFeatureHandler` subclasses.
    
    :Parameters:
        - `element_name`: stream element QName
        - `usage_restriction`: optional usage restriction: "initiator" or
          "receiver"
    :Types:
        - `element_name`: `str`
        - `usage_restriction`: `str`
    """
    def decorator(func):
        """The decorator"""
        func._pyxmpp_stream_element_handled = element_name
        func._pyxmpp_usage_restriction = usage_restriction
        return func
    return decorator

class _NO_CHANGE(object):
    """Class for the `NO_CHANGE` constant.
    """
    # pylint: disable=C0103,R0903
    def __str__(self):
        return "NO_CHANGE"
    def __repr__(self):
        return "NO_CHANGE"

NO_CHANGE = _NO_CHANGE()
del _NO_CHANGE

# vi: sts=4 et sw=4
