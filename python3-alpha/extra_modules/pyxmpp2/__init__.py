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

"""
PyXMPP2 - Jabber/XMPP protocol implementation
=============================================

Project Information
-------------------

PyXMPP2 is a Python implementation of the XMPP protocol (:RFC:`6120`,
:RFC:`6121`) and some of `XMPP Extensions`_


`PyXMPP`_ was first implemented by Jacek Konieczny in year 2003, using
`libxml2`_ as the XML framework, then it slowly evolved over years becoming
kind of monster full of 'smart' and legacy code. Also libxml2 proved to be
inadequate base for a Python library.

PyXMPP2 is a rewrite of the original PyXMPP aimed to replace libxml2 with
the more standard :etree:`ElementTree` API and to clean up the API. In fact the
API has completely changed, hopefully for better.

The PyXMPP2 project is hosted at GitHub: http://github.com/Jajcus/pyxmpp/

The API documentation is available at: http://jajcus.github.com/pyxmpp2/api/

The simple API
--------------

If you don't care about all the PyXMPP flexibility and features and just want
to send a Jabber message, please look at the 'Simple API': `pyxmpp2.simple`

Basic components
----------------

XMPP Data
---------

The basic functionality of the XMPP protocol is to send XML data between
entities using XML container elements called 'stanzas'. There are three
types of stanzas: 

  - ``<message />`` stanzas to send a unicast message to another entity
  - ``<iq />`` stanzas for simple request-response exchange
  - ``<presence />`` stanzas for broadcast of availability information

They are represented by the following PyXMPP2 classes: `message.Message`,
`iq.Iq` and `presence.Presence`.

The stanzas may carry arbitrary XML payload. It is bound to the stanzas
using the `stanzapayload.StanzaPayload` interface. It can be a generic
`stanzapayload.XMLPayload` implementation or any specialized
`interfaces.StanzaPayload` subclass decoding the XML element as required.

XMPP Streams
------------

The stanzas are sent over XML streams. In PyXMPP the stream functionality
is implemented by the `streambase.StreamBase` class. The class does not
implement actual I/O (see the next secition) or SASL/TLS (these are handled
by `streamsasl.StreamSASLHandler` and `streamtls.StreamTLSHandler`), but
provides the basic logic to handle stanzas and stream negotiation.

Transports
----------

The actual I/O (sending XML data over socket) has been separated from the
`streambase.StreamBase` for cleaner code and to allow alternate transport
implementations (like `BOSH`_). The interface is defined by the
`interfaces.XMPPTransport` abstract class and the standard TCP transport
(:RFC:`6120`) is implemented via `transport.TCPTransport`.

Main event loop
---------------

The transport objects react on I/O events (like data received from a socket)
and an XMPP application usually wants to react on various XMPP events, so
a mechanism to dispatch these events is required.  In PyXMPP2 the
`mainloop.interfaces.MainLoop` interface is defined to dispatch the events to
various components. There are also a few implementation of the interface
provided:

    - `mainloop.select.SelectMainLoop`: asynchronous I/O loop based on the
      :std:`select.select` call.
    - `mainloop.poll.PollMainLoop`: asynchronous I/O loop based on the
      :std:`select.poll` call. Not available on all platforms.
    - `mainloop.threads.ThreadPool`: a thread-based alternative to the above

The default implementation is available as `mainloop.main_loop_factory`.

Chains of responsibility
------------------------

Both `streambase.StreamBase` and main loop implementations constructors
expect a 'handlers' argument with a list of object to handle various events
or elements. Main loop handlers should implement one or more of these
interfaces:

    - `pyxmpp2.mainloop.interfaces.IOHandler`: provides a socket or file
      descriptor to poll and handles reads from and writes to it. Implemented
      e.g. by the `transport.TCPTransport` class.
    - `pyxmpp2.mainloop.interfaces.EventHandler`: specially decorated methods
      of its subclasess are called on events raise by other components (like
      the transport or stream). Also available as
      `pyxmpp2.interfaces.EventHandler`
    - `pyxmpp2.mainloop.interfaces.TimeoutHandler`: specially decorated methods
      of its subclasess are called on selected intervals. Also available as
      'pyxmpp2.interfaces.TimeoutHandler`

Stream handlers should implement one or more of:

    - `pyxmpp2.interfaces.XMPPFeatureHandler`: specially decorated methods of
      its subclasses are called for matching stanzas. The interface will also
      provide facilities for XMPP feature discovery and capability
      advertisement.
    - `pyxmpp2.interfaces.StreamFeatureHandler`: handle or generate
      ``<stream:features>`` subelement and handle other related stream
      elements. Implemented e.g.  by `streamsasl.StreamSASLHandler` and
      `streamtls.StreamTLSHandler`.

Component configuration
-----------------------

As many parameters may define an XMPP implementation behaviour, class
constructors or other methods would require lots of arguments to handle them
all. Instead, a special `settings.XMPPSettings` object is often used, which can
hold any parameter useful by any part of the PyXMPP2. It is also used as a
simple form of dependency injection.

The Client class
------------------

The `pyxmpp2.client.Client` joins a main loop, a client stream and some basic
handlers (for stream encryption, authentication, resource binding and roster
handling) together, so a client application has only to add its handlers to
make it work.

See the `pyxmpp2.client` module for details.  This should be the start point
for most XMPP client applications.

Logging
-------

PyXMPP2 does all it logging via the standard :std:`logging` module. Most
of the PyXMPP2 modules log via 'pyxmpp2.module-name' loggers. There are some
special cases though:

  * 'pyxmpp2.IN' logger, which is used for XML data (not parsed yet)
  * 'pyxmpp2.OUT' logger, which is used for XML data sent

Those two can be used to intercept the data for application-specific monitoring
(e.g. an 'XML console' in a client GUI).

Most of the log messages generated by PyXMPP have level 'DEBUG', no higher
level messages should appear during normal operation. Some 'WARNING' messages
may be emitted when a remote party misbehaves and 'ERROR' messages in case of
programming errors.

Module hierarchy
----------------

Base XMPP features (:RFC:`6120` and :RFC:`6121`) and core PyXMPP2 framework
features are implemented in direct submodules of `pyxmpp2` package.

`pyxmpp2.sasl` package provides the SASL protocol and mechanisms
implementation.

`pyxmpp2.mainloop` contains the main event loop and I/O framework.

`pyxmpp2.ext` contains `XMPP Extensions`_ implementations.

.. _XMPP Extensions: http://xmpp.org/xmpp-protocols/xmpp-extensions/
.. _PyXMPP: http://pyxmpp.jajcus.net/
.. _libxml2: http://xmlsoft.org/
.. _BOSH: http://xmpp.org/extensions/xep-0124.html
"""

__docformat__ = "restructuredtext en"

# vi: sts=4 et sw=4
