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

"Common XMPP constants."""

XML_NS = "http://www.w3.org/XML/1998/namespace"
XML_QNP = "{{{0}}}".format(XML_NS)

STREAM_NS = "http://etherx.jabber.org/streams"
STREAM_QNP = "{{{0}}}".format(STREAM_NS)
STREAM_ROOT_TAG = STREAM_QNP + "stream"

BIND_NS = "urn:ietf:params:xml:ns:xmpp-bind"
BIND_QNP = "{{{0}}}".format(BIND_NS)

SESSION_NS = "urn:ietf:params:xml:ns:xmpp-session"
SESSION_QNP = "{{{0}}}".format(SESSION_NS)

STANZA_CLIENT_NS = "jabber:client"
STANZA_CLIENT_QNP = "{{{0}}}".format(STANZA_CLIENT_NS)

STANZA_SERVER_NS = "jabber:server"
STANZA_SERVER_QNP = "{{{0}}}".format(STANZA_SERVER_NS)

STANZA_NAMESPACES = (STANZA_CLIENT_NS, STANZA_SERVER_NS)

STANZA_ERROR_NS = 'urn:ietf:params:xml:ns:xmpp-stanzas'
STANZA_ERROR_QNP = "{{{0}}}".format(STANZA_ERROR_NS)

STREAM_ERROR_NS = 'urn:ietf:params:xml:ns:xmpp-streams'
STREAM_ERROR_QNP = "{{{0}}}".format(STREAM_ERROR_NS)

PYXMPP_ERROR_NS = 'http://pyxmpp.jajcus.net/xmlns/errors'
PYXMPP_ERROR_QNP = "{{{0}}}".format(PYXMPP_ERROR_NS)

SASL_NS = "urn:ietf:params:xml:ns:xmpp-sasl"
SASL_QNP = "{{{0}}}".format(SASL_NS)

TLS_NS = "urn:ietf:params:xml:ns:xmpp-tls"
TLS_QNP = "{{{0}}}".format(TLS_NS)


XML_LANG_QNAME = XML_QNP + "lang"
