#
# (C) Copyright 2003-2010 Jacek Konieczny <jajcus@jajcus.net>
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
"""XMPP stream support with fallback to legacy non-SASL Jabber authentication.

Normative reference:
  - `JEP 78 <http://www.jabber.org/jeps/jep-0078.html>`__
"""



__docformat__="restructuredtext en"

raise ImportError("{0} is not yet rewritten for PyXMPP2".format(__name__))

import hashlib
import logging

from ..iq import Iq
from ..utils import to_utf8,from_utf8
from ..jid import JID
from ..clientstream import ClientStream
from .register import Register

from ..exceptions import ClientStreamError, LegacyAuthenticationError, RegistrationError

class LegacyClientStream(ClientStream):
    """Handles Jabber (both XMPP and legacy protocol) client connection stream.

    Both client and server side of the connection is supported. This class handles
    client SASL and legacy authentication, authorisation and XMPP resource binding.
    """
    def __init__(self, jid, password = None, server = None, port = 5222,
            auth_methods = ("sasl:DIGEST-MD5", "digest"),
            tls_settings = None, keepalive = 0, owner = None):
        """Initialize a LegacyClientStream object.

        :Parameters:
            - `jid`: local JID.
            - `password`: user's password.
            - `server`: server to use. If not given then address will be derived form the JID.
            - `port`: port number to use. If not given then address will be derived form the JID.
            - `auth_methods`: sallowed authentication methods. SASL authentication mechanisms
              in the list should be prefixed with "sasl:" string.
            - `tls_settings`: settings for StartTLS -- `TLSSettings` instance.
            - `keepalive`: keepalive output interval. 0 to disable.
            - `owner`: `Client`, `Component` or similar object "owning" this stream.
        :Types:
            - `jid`: `pyxmpp.JID`
            - `password`: `str`
            - `server`: `str`
            - `port`: `int`
            - `auth_methods`: sequence of `str`
            - `tls_settings`: `pyxmpp.TLSSettings`
            - `keepalive`: `int`
        """
        (self.authenticated, self.available_auth_methods, self.auth_stanza,
                self.peer_authenticated, self.auth_method_used,
                self.registration_callback, self.registration_form, self.__register) = (None,) * 8
        ClientStream.__init__(self, jid, password, server, port,
                            auth_methods, tls_settings, keepalive, owner)
        self.__logger=logging.getLogger("pyxmpp2.jabber.LegacyClientStream")

    def _reset(self):
        """Reset the `LegacyClientStream` object state, making the object ready
        to handle new connections."""
        ClientStream._reset(self)
        self.available_auth_methods = None
        self.auth_stanza = None
        self.registration_callback = None

    def _post_connect(self):
        """Initialize authentication when the connection is established
        and we are the initiator."""
        if not self.initiator:
            if "plain" in self.auth_methods or "digest" in self.auth_methods:
                self.set_iq_get_handler("query","jabber:iq:auth",
                            self.auth_in_stage1)
                self.set_iq_set_handler("query","jabber:iq:auth",
                            self.auth_in_stage2)
        elif self.registration_callback:
            iq = Iq(stanza_type = "get")
            iq.set_content(Register())
            self.set_response_handlers(iq, self.registration_form_received, self.registration_error)
            self.send(iq)
            return
        ClientStream._post_connect(self)

    def _post_auth(self):
        """Unregister legacy authentication handlers after successfull
        authentication."""
        ClientStream._post_auth(self)
        if not self.initiator:
            self.unset_iq_get_handler("query","jabber:iq:auth")
            self.unset_iq_set_handler("query","jabber:iq:auth")

    def _try_auth(self):
        """Try to authenticate using the first one of allowed authentication
        methods left.

        [client only]"""
        if self.authenticated:
            self.__logger.debug("try_auth: already authenticated")
            return
        self.__logger.debug("trying auth: %r" % (self._auth_methods_left,))
        if not self._auth_methods_left:
            raise LegacyAuthenticationError("No allowed authentication methods available")
        method=self._auth_methods_left[0]
        if method.startswith("sasl:"):
            return ClientStream._try_auth(self)
        elif method not in ("plain","digest"):
            self._auth_methods_left.pop(0)
            self.__logger.debug("Skipping unknown auth method: %s" % method)
            return self._try_auth()
        elif self.available_auth_methods is not None:
            if method in self.available_auth_methods:
                self._auth_methods_left.pop(0)
                self.auth_method_used=method
                if method=="digest":
                    self._digest_auth_stage2(self.auth_stanza)
                else:
                    self._plain_auth_stage2(self.auth_stanza)
                self.auth_stanza=None
                return
            else:
                self.__logger.debug("Skipping unavailable auth method: %s" % method)
        else:
            self._auth_stage1()

    def auth_in_stage1(self,stanza):
        """Handle the first stage (<iq type='get'/>) of legacy ("plain" or
        "digest") authentication.

        [server only]"""
        self.lock.acquire()
        try:
            if "plain" not in self.auth_methods and "digest" not in self.auth_methods:
                iq=stanza.make_error_response("not-allowed")
                self.send(iq)
                return

            iq=stanza.make_result_response()
            q=iq.new_query("jabber:iq:auth")
            q.newChild(None,"username",None)
            q.newChild(None,"resource",None)
            if "plain" in self.auth_methods:
                q.newChild(None,"password",None)
            if "digest" in self.auth_methods:
                q.newChild(None,"digest",None)
            self.send(iq)
            iq.free()
        finally:
            self.lock.release()

    def auth_in_stage2(self,stanza):
        """Handle the second stage (<iq type='set'/>) of legacy ("plain" or
        "digest") authentication.

        [server only]"""
        self.lock.acquire()
        try:
            if "plain" not in self.auth_methods and "digest" not in self.auth_methods:
                iq=stanza.make_error_response("not-allowed")
                self.send(iq)
                return

            username=stanza.xpath_eval("a:query/a:username",{"a":"jabber:iq:auth"})
            if username:
                username=from_utf8(username[0].getContent())
            resource=stanza.xpath_eval("a:query/a:resource",{"a":"jabber:iq:auth"})
            if resource:
                resource=from_utf8(resource[0].getContent())
            if not username or not resource:
                self.__logger.debug("No username or resource found in auth request")
                iq=stanza.make_error_response("bad-request")
                self.send(iq)
                return

            if stanza.xpath_eval("a:query/a:password",{"a":"jabber:iq:auth"}):
                if "plain" not in self.auth_methods:
                    iq=stanza.make_error_response("not-allowed")
                    self.send(iq)
                    return
                else:
                    return self._plain_auth_in_stage2(username,resource,stanza)
            if stanza.xpath_eval("a:query/a:digest",{"a":"jabber:iq:auth"}):
                if "plain" not in self.auth_methods:
                    iq=stanza.make_error_response("not-allowed")
                    self.send(iq)
                    return
                else:
                    return self._digest_auth_in_stage2(username,resource,stanza)
        finally:
            self.lock.release()

    def _auth_stage1(self):
        """Do the first stage (<iq type='get'/>) of legacy ("plain" or
        "digest") authentication.

        [client only]"""
        iq=Iq(stanza_type="get")
        q=iq.new_query("jabber:iq:auth")
        q.newTextChild(None,"username",to_utf8(self.my_jid.node))
        q.newTextChild(None,"resource",to_utf8(self.my_jid.resource))
        self.send(iq)
        self.set_response_handlers(iq,self.auth_stage2,self.auth_error,
                            self.auth_timeout,timeout=60)
        iq.free()

    def auth_timeout(self):
        """Handle legacy authentication timeout.

        [client only]"""
        self.lock.acquire()
        try:
            self.__logger.debug("Timeout while waiting for jabber:iq:auth result")
            if self._auth_methods_left:
                self._auth_methods_left.pop(0)
        finally:
            self.lock.release()

    def auth_error(self,stanza):
        """Handle legacy authentication error.

        [client only]"""
        self.lock.acquire()
        try:
            err=stanza.get_error()
            ae=err.xpath_eval("e:*",{"e":"jabber:iq:auth:error"})
            if ae:
                ae=ae[0].name
            else:
                ae=err.get_condition().name
            raise LegacyAuthenticationError("Authentication error condition: %s"
                        % (ae,))
        finally:
            self.lock.release()

    def auth_stage2(self,stanza):
        """Handle the first stage authentication response (result of the <iq
        type="get"/>).

        [client only]"""
        self.lock.acquire()
        try:
            self.__logger.debug("Procesing auth response...")
            self.available_auth_methods=[]
            if (stanza.xpath_eval("a:query/a:digest",{"a":"jabber:iq:auth"}) and self.stream_id):
                self.available_auth_methods.append("digest")
            if (stanza.xpath_eval("a:query/a:password",{"a":"jabber:iq:auth"})):
                self.available_auth_methods.append("plain")
            self.auth_stanza=stanza.copy()
            self._try_auth()
        finally:
            self.lock.release()

    def _plain_auth_stage2(self, _unused):
        """Do the second stage (<iq type='set'/>) of legacy "plain"
        authentication.

        [client only]"""
        iq=Iq(stanza_type="set")
        q=iq.new_query("jabber:iq:auth")
        q.newTextChild(None,"username",to_utf8(self.my_jid.node))
        q.newTextChild(None,"resource",to_utf8(self.my_jid.resource))
        q.newTextChild(None,"password",to_utf8(self.password))
        self.send(iq)
        self.set_response_handlers(iq,self.auth_finish,self.auth_error)
        iq.free()

    def _plain_auth_in_stage2(self, username, _unused, stanza):
        """Handle the second stage (<iq type='set'/>) of legacy "plain"
        authentication.

        [server only]"""
        password=stanza.xpath_eval("a:query/a:password",{"a":"jabber:iq:auth"})
        if password:
            password=from_utf8(password[0].getContent())
        if not password:
            self.__logger.debug("No password found in plain auth request")
            iq=stanza.make_error_response("bad-request")
            self.send(iq)
            return

        if self.check_password(username,password):
            iq=stanza.make_result_response()
            self.send(iq)
            self.peer_authenticated=True
            self.auth_method_used="plain"
            self.state_change("authorized",self.peer)
            self._post_auth()
        else:
            self.__logger.debug("Plain auth failed")
            iq=stanza.make_error_response("bad-request")
            e=iq.get_error()
            e.add_custom_condition('jabber:iq:auth:error',"user-unauthorized")
            self.send(iq)

    def _digest_auth_stage2(self, _unused):
        """Do the second stage (<iq type='set'/>) of legacy "digest"
        authentication.

        [client only]"""
        iq=Iq(stanza_type="set")
        q=iq.new_query("jabber:iq:auth")
        q.newTextChild(None,"username",to_utf8(self.my_jid.node))
        q.newTextChild(None,"resource",to_utf8(self.my_jid.resource))

        digest = hashlib.sha1(to_utf8(self.stream_id)+to_utf8(self.password)).hexdigest()

        q.newTextChild(None,"digest",digest)
        self.send(iq)
        self.set_response_handlers(iq,self.auth_finish,self.auth_error)
        iq.free()

    def _digest_auth_in_stage2(self, username, _unused, stanza):
        """Handle the second stage (<iq type='set'/>) of legacy "digest"
        authentication.

        [server only]"""
        digest=stanza.xpath_eval("a:query/a:digest",{"a":"jabber:iq:auth"})
        if digest:
            digest=digest[0].getContent()
        if not digest:
            self.__logger.debug("No digest found in digest auth request")
            iq=stanza.make_error_response("bad-request")
            self.send(iq)
            return

        password,pwformat=self.get_password(username)
        if not password or pwformat!="plain":
            iq=stanza.make_error_response("bad-request")
            e=iq.get_error()
            e.add_custom_condition('jabber:iq:auth:error',"user-unauthorized")
            self.send(iq)
            return

        mydigest = hashlib.sha1(to_utf8(self.stream_id)+to_utf8(password)).hexdigest()

        if mydigest==digest:
            iq=stanza.make_result_response()
            self.send(iq)
            self.peer_authenticated=True
            self.auth_method_used="digest"
            self.state_change("authorized",self.peer)
            self._post_auth()
        else:
            self.__logger.debug("Digest auth failed: %r != %r" % (digest,mydigest))
            iq=stanza.make_error_response("bad-request")
            e=iq.get_error()
            e.add_custom_condition('jabber:iq:auth:error',"user-unauthorized")
            self.send(iq)

    def auth_finish(self, _unused):
        """Handle success of the legacy authentication."""
        self.lock.acquire()
        try:
            self.__logger.debug("Authenticated")
            self.authenticated=True
            self.state_change("authorized",self.my_jid)
            self._post_auth()
        finally:
            self.lock.release()

    def registration_error(self, stanza):
        """Handle in-band registration error.

        [client only]

        :Parameters:
            - `stanza`: the error stanza received or `None` on timeout.
        :Types:
            - `stanza`: `pyxmpp.stanza.Stanza`"""
        self.lock.acquire()
        try:
            err=stanza.get_error()
            ae=err.xpath_eval("e:*",{"e":"jabber:iq:auth:error"})
            if ae:
                ae=ae[0].name
            else:
                ae=err.get_condition().name
            raise RegistrationError("Authentication error condition: %s" % (ae,))
        finally:
            self.lock.release()

    def registration_form_received(self, stanza):
        """Handle registration form received.

        [client only]

        Call self.registration_callback with the registration form received
        as the argument. Use the value returned by the callback will be a
        filled-in form.

        :Parameters:
            - `stanza`: the stanza received.
        :Types:
            - `stanza`: `pyxmpp.iq.Iq`"""
        self.lock.acquire()
        try:
            self.__register = Register(stanza.get_query())
            self.registration_callback(stanza, self.__register.get_form())
        finally:
            self.lock.release()

    def submit_registration_form(self, form):
        """Submit a registration form.

        [client only]

        :Parameters:
            - `form`: the filled-in form. When form is `None` or its type is
              "cancel" the registration is to be canceled.

        :Types:
            - `form`: `pyxmpp.jabber.dataforms.Form`"""
        self.lock.acquire()
        try:
            if form and form.type!="cancel":
                self.registration_form = form
                iq = Iq(stanza_type = "set")
                iq.set_content(self.__register.submit_form(form))
                self.set_response_handlers(iq, self.registration_success, self.registration_error)
                self.send(iq)
            else:
                self.__register = None
        finally:
            self.lock.release()

    def registration_success(self, stanza):
        """Handle registration success.

        [client only]

        Clean up registration stuff, change state to "registered" and initialize
        authentication.

        :Parameters:
            - `stanza`: the stanza received.
        :Types:
            - `stanza`: `pyxmpp.iq.Iq`"""
        _unused = stanza
        self.lock.acquire()
        try:
            self.state_change("registered", self.registration_form)
            if ('FORM_TYPE' in self.registration_form
                    and self.registration_form['FORM_TYPE'].value == 'jabber:iq:register'):
                if 'username' in self.registration_form:
                    self.my_jid = JID(self.registration_form['username'].value,
                            self.my_jid.domain, self.my_jid.resource)
                if 'password' in self.registration_form:
                    self.password = self.registration_form['password'].value
            self.registration_callback = None
            self._post_connect()
        finally:
            self.lock.release()

# vi: sts=4 et sw=4
