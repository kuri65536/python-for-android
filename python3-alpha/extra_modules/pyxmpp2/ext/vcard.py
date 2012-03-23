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
# pylint: disable-msg=W0302
"""Jabber vCard and MIME (RFC 2426) vCard implementation.

Normative reference:
  - `JEP 54 <http://www.jabber.org/jeps/jep-0054.html>`__
  - `RFC 2425 <http://www.ietf.org/rfc/rfc2425.txt>`__
  - `RFC 2426 <http://www.ietf.org/rfc/rfc2426.txt>`__
"""




__docformat__="restructuredtext en"

raise ImportError("{0} is not yet rewritten for PyXMPP2".format(__name__))

import base64
import binascii
import libxml2
import re

import pyxmpp.jid
from ..utils import to_utf8,from_utf8
from ..xmlextra import get_node_ns
from ..objects import StanzaPayloadObject
from ..exceptions import BadRequestProtocolError, JIDMalformedProtocolError, JIDError

VCARD_NS="vcard-temp"

class Empty(Exception):
    """Exception raised when parsing empty vcard element. Such element will
    be ignored."""
    pass

valid_string_re=re.compile(r"^[\w\d \t]*$")
non_quoted_semicolon_re=re.compile(r'(?<!\\);')

def quote_semicolon(value):
    return value.replace(r';', r'\;')

def unquote_semicolon(value):
    return value.replace(r'\;', r';')

def rfc2425encode(name,value,parameters=None,charset="utf-8"):
    """Encodes a vCard field into an RFC2425 line.

    :Parameters:
        - `name`: field type name
        - `value`: field value
        - `parameters`: optional parameters
        - `charset`: encoding of the output and of the `value` (if not
          `str`)
    :Types:
        - `name`: `str`
        - `value`: `str` or `str`
        - `parameters`: `dict` of `str` -> `str`
        - `charset`: `str`

    :return: the encoded RFC2425 line (possibly folded)
    :returntype: `str`"""
    if not parameters:
        parameters={}
    if type(value) is str:
        value=value.replace("\r\n","\\n")
        value=value.replace("\n","\\n")
        value=value.replace("\r","\\n")
        value=value.encode(charset,"replace")
    elif type(value) is not str:
        raise TypeError("Bad type for rfc2425 value")
    elif not valid_string_re.match(value):
        parameters["encoding"]="b"
        value=binascii.b2a_base64(value)

    ret=str(name).lower()
    for k,v in list(parameters.items()):
        ret+=";%s=%s" % (str(k),str(v))
    ret+=":"
    while(len(value)>70):
        ret+=value[:70]+"\r\n "
        value=value[70:]
    ret+=value+"\r\n"
    return ret

class VCardField:
    """Base class for vCard fields.

    :Ivariables:
        - `name`: name of the field.
    """
    def __init__(self,name):
        """Initialize a `VCardField` object.

        Set its name.

        :Parameters:
            - `name`: field name
        :Types:
            - `name`: `str`"""
        self.name=name
    def __repr__(self):
        return "<%s %r>" % (self.__class__,self.rfc2426())
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return ""

class VCardString(VCardField):
    """Generic class for all standard text fields in the vCard.

    :Ivariables:
        - `value`: field value.
    :Types:
        - `value`: `str`"""
    def __init__(self,name, value, rfc2425parameters = None, empty_ok = False):
        """Initialize a `VCardString` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        _unused = rfc2425parameters
        VCardField.__init__(self,name)
        if isinstance(value,libxml2.xmlNode):
            value=value.getContent()
            if value:
                self.value=str(value,"utf-8","replace").strip()
            else:
                self.value=""
        else:
            self.value=value
        if not self.value and not empty_ok:
            raise Empty("Empty string value")
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode(self.name,self.value)
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        return parent.newTextChild(None, to_utf8(self.name.upper()), to_utf8(self.value))
    def __str__(self):
        return self.value
    def __str__(self):
        return self.value.encode("utf-8")

class VCardXString(VCardString):
    """Generic class for all text vCard fields not defined in RFC 2426.

    In the RFC 2425 representation field name will be prefixed with 'x-'.

    :Ivariables:
        - `value`: field value.
    :Types:
        - `value`: `str`"""
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode("x-"+self.name,self.value)

class VCardJID(VCardField):
    """JID vCard field.

    This field is not defined in RFC 2426, so it will be named 'x-jabberid'
    in RFC 2425 output.

    :Ivariables:
        - `value`: field value.
    :Types:
        - `value`: `JID`"""
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardJID` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        _unused = rfc2425parameters
        VCardField.__init__(self,name)
        if isinstance(value,libxml2.xmlNode):
            try:
                self.value=pyxmpp.jid.JID(value.getContent())
            except JIDError:
                raise JIDMalformedProtocolError("JID malformed")
        else:
            self.value=pyxmpp.jid.JID(value)
        if not self.value:
            raise Empty("Empty JID value")
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode("x-jabberid",self.value.as_unicode())
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        name=to_utf8(self.name.upper())
        content=self.value.as_utf8()
        return parent.newTextChild(None, name, content)
    def __str__(self):
        return self.value.as_unicode()
    def __str__(self):
        return self.value.as_string()

class VCardName(VCardField):
    """Name vCard field.

    :Ivariables:
        - `family`: family name.
        - `given`: given name.
        - `middle`: middle name.
        - `prefix`: name prefix.
        - `suffix`: name suffix.
    :Types:
        - `family`: `str`
        - `given`: `str`
        - `middle`: `str`
        - `prefix`: `str`
        - `suffix`: `str`"""
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardName` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        _unused = rfc2425parameters
        VCardField.__init__(self,name)
        if self.name.upper()!="N":
            raise RuntimeError("VCardName handles only 'N' type")
        if isinstance(value,libxml2.xmlNode):
            self.family,self.given,self.middle,self.prefix,self.suffix=[""]*5
            empty=1
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='FAMILY':
                    self.family=str(n.getContent(),"utf-8")
                    empty=0
                if n.name=='GIVEN':
                    self.given=str(n.getContent(),"utf-8")
                    empty=0
                if n.name=='MIDDLE':
                    self.middle=str(n.getContent(),"utf-8")
                    empty=0
                if n.name=='PREFIX':
                    self.prefix=str(n.getContent(),"utf-8")
                    empty=0
                if n.name=='SUFFIX':
                    self.suffix=str(n.getContent(),"utf-8")
                    empty=0
                n=n.__next__
            if empty:
                raise Empty("Empty N value")
        else:
            v=non_quoted_semicolon_re.split(value)
            value=[""]*5
            value[:len(v)]=v
            self.family,self.given,self.middle,self.prefix,self.suffix=(
                unquote_semicolon(val) for val in value)
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode("n",';'.join(quote_semicolon(val) for val in
                (self.family,self.given,self.middle,self.prefix,self.suffix)))
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,"N",None)
        n.newTextChild(None,"FAMILY",to_utf8(self.family))
        n.newTextChild(None,"GIVEN",to_utf8(self.given))
        n.newTextChild(None,"MIDDLE",to_utf8(self.middle))
        n.newTextChild(None,"PREFIX",to_utf8(self.prefix))
        n.newTextChild(None,"SUFFIX",to_utf8(self.suffix))
        return n
    def __str__(self):
        r=[]
        if self.prefix:
            r.append(self.prefix.replace(","," "))
        if self.given:
            r.append(self.given.replace(","," "))
        if self.middle:
            r.append(self.middle.replace(","," "))
        if self.family:
            r.append(self.family.replace(","," "))
        if self.suffix:
            r.append(self.suffix.replace(","," "))
        return " ".join(r)
    def __str__(self):
        return self.__unicode__().encode("utf-8")

class VCardImage(VCardField):
    """Image vCard field.

    :Ivariables:
        - `image`: image binary data (when `uri` is None)
        - `uri`: image URI (when `image` is None)
        - `type`: optional image type
    :Types:
        - `image`: `str`
        - `uri`: `str`
        - `type`: `str`"""
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardImage` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        VCardField.__init__(self,name)
        if not rfc2425parameters:
            rfc2425parameters={}
        self.uri,self.type,self.image=[None]*3
        if isinstance(value,libxml2.xmlNode):
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='TYPE':
                    self.type=str(n.getContent(),"utf-8","replace")
                if n.name=='BINVAL':
                    self.image=base64.decodestring(n.getContent())
                if n.name=='EXTVAL':
                    self.uri=str(n.getContent(),"utf-8","replace")
                n=n.__next__
            if (self.uri and self.image) or (not self.uri and not self.image):
                raise ValueError("Bad %s value in vcard" % (name,))
            if (not self.uri and not self.image):
                raise Empty("Bad %s value in vcard" % (name,))
        else:
            if rfc2425parameters.get("value", "").lower()=="uri":
                self.uri=value
                self.type=None
            else:
                self.type=rfc2425parameters.get("type")
                self.image=value
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        if self.uri:
            return rfc2425encode(self.name,self.uri,{"value":"uri"})
        elif self.image:
            if self.type:
                p={"type":self.type}
            else:
                p={}
            return rfc2425encode(self.name,self.image,p)
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,self.name.upper(),None)
        if self.uri:
            n.newTextChild(None,"EXTVAL",to_utf8(self.uri))
        else:
            if self.type:
                n.newTextChild(None,"TYPE",self.type)
            n.newTextChild(None,"BINVAL",binascii.b2a_base64(self.image))
        return n
    def __str__(self):
        if self.uri:
            return self.uri
        if self.type:
            return "(%s data)" % (self.type,)
        return "(binary data)"
    def __str__(self):
        return self.__unicode__().encode("utf-8")


class VCardAdr(VCardField):
    """Address vCard field.

    :Ivariables:
        - `type`: type of the address.
        - `pobox`: the post office box.
        - `extadr`: the extended address.
        - `street`: the street address.
        - `locality`: the locality (e.g. city).
        - `region`: the region.
        - `pcode`: the postal code.
        - `ctry`: the country.
    :Types:
        - `type`: `list` of "home","work","postal","parcel","dom","intl" or "pref"
        - `pobox`: `str`
        - `extadr`: `str`
        - `street`: `str`
        - `locality`: `str`
        - `region`: `str`
        - `pcode`: `str`
        - `ctry`: `str`"""
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardAdr` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        VCardField.__init__(self,name)
        if not rfc2425parameters:
            rfc2425parameters={}
        if self.name.upper()!="ADR":
            raise RuntimeError("VCardAdr handles only 'ADR' type")
        (self.pobox,self.extadr,self.street,self.locality,
                self.region,self.pcode,self.ctry)=[""]*7
        self.type=[]
        if isinstance(value,libxml2.xmlNode):
            self.__from_xml(value)
        else:
            t=rfc2425parameters.get("type")
            if t:
                self.type=t.split(",")
            else:
                self.type=["intl","postal","parcel","work"]
            v=non_quoted_semicolon_re.split(value)
            value=[""]*7
            value[:len(v)]=v
            (self.pobox,self.extadr,self.street,self.locality,
                    self.region,self.pcode,self.ctry)=(
                unquote_semicolon(val) for val in value)

    def __from_xml(self,value):
        """Initialize a `VCardAdr` object from and XML element.

        :Parameters:
            - `value`: field value as an XML node
        :Types:
            - `value`: `libxml2.xmlNode`"""
        n=value.children
        vns=get_node_ns(value)
        while n:
            if n.type!='element':
                n=n.__next__
                continue
            ns=get_node_ns(n)
            if (ns and vns and ns.getContent()!=vns.getContent()):
                n=n.__next__
                continue
            if n.name=='POBOX':
                self.pobox=str(n.getContent(),"utf-8","replace")
            elif n.name in ('EXTADR', 'EXTADD'):
                self.extadr=str(n.getContent(),"utf-8","replace")
            elif n.name=='STREET':
                self.street=str(n.getContent(),"utf-8","replace")
            elif n.name=='LOCALITY':
                self.locality=str(n.getContent(),"utf-8","replace")
            elif n.name=='REGION':
                self.region=str(n.getContent(),"utf-8","replace")
            elif n.name=='PCODE':
                self.pcode=str(n.getContent(),"utf-8","replace")
            elif n.name=='CTRY':
                self.ctry=str(n.getContent(),"utf-8","replace")
            elif n.name in ("HOME","WORK","POSTAL","PARCEL","DOM","INTL",
                    "PREF"):
                self.type.append(n.name.lower())
            n=n.__next__
        if self.type==[]:
            self.type=["intl","postal","parcel","work"]
        elif "dom" in self.type and "intl" in self.type:
            raise ValueError("Both 'dom' and 'intl' specified in vcard ADR")

    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode("adr",';'.join(quote_semicolon(val) for val in
                (self.pobox,self.extadr,self.street,self.locality,
                        self.region,self.pcode,self.ctry)),
                {"type":",".join(self.type)})

    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,"ADR",None)
        for t in ("home","work","postal","parcel","dom","intl","pref"):
            if t in self.type:
                n.newChild(None,t.upper(),None)
        n.newTextChild(None,"POBOX",to_utf8(self.pobox))
        n.newTextChild(None,"EXTADD",to_utf8(self.extadr))
        n.newTextChild(None,"STREET",to_utf8(self.street))
        n.newTextChild(None,"LOCALITY",to_utf8(self.locality))
        n.newTextChild(None,"REGION",to_utf8(self.region))
        n.newTextChild(None,"PCODE",to_utf8(self.pcode))
        n.newTextChild(None,"CTRY",to_utf8(self.ctry))
        return n

class VCardLabel(VCardField):
    """Address label vCard field.

    :Ivariables:
        - `lines`: list of label text lines.
        - `type`: type of the label.
    :Types:
        - `lines`: `list` of `str`
        - `type`: `list` of "home","work","postal","parcel","dom","intl" or "pref"
    """
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardLabel` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        VCardField.__init__(self,name)
        if not rfc2425parameters:
            rfc2425parameters={}
        if self.name.upper()!="LABEL":
            raise RuntimeError("VCardAdr handles only 'LABEL' type")
        if isinstance(value,libxml2.xmlNode):
            self.lines=[]
            self.type=[]
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='LINE':
                    l=str(n.getContent(),"utf-8","replace").strip()
                    l=l.replace("\n"," ").replace("\r"," ")
                    self.lines.append(l)
                elif n.name in ("HOME","WORK","POSTAL","PARCEL","DOM","INTL",
                        "PREF"):
                    self.type.append(n.name.lower())
                n=n.__next__
            if self.type==[]:
                self.type=["intl","postal","parcel","work"]
            elif "dom" in self.type and "intl" in self.type:
                raise ValueError("Both 'dom' and 'intl' specified in vcard LABEL")
            if not self.lines:
                self.lines=[""]
        else:
            t=rfc2425parameters.get("type")
            if t:
                self.type=t.split(",")
            else:
                self.type=["intl","postal","parcel","work"]
            self.lines=value.split("\\n")

    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode("label","\n".join(self.lines),
                {"type":",".join(self.type)})
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,"ADR",None)
        for t in ("home","work","postal","parcel","dom","intl","pref"):
            if t in self.type:
                n.newChild(None,t.upper(),None)
        for l in self.lines:
            n.newTextChild(None,"LINE",l)
        return n

class VCardTel(VCardField):
    """Telephone vCard field.

    :Ivariables:
        - `number`: phone number.
        - `type`: type of the phone number.
    :Types:
        - `number`: `str`
        - `type`: `list` of "home","work","voice","fax","pager","msg","cell","video","bbs","modem","isdn","pcs" or "pref".
    """
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardTel` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        VCardField.__init__(self,name)
        if not rfc2425parameters:
            rfc2425parameters={}
        if self.name.upper()!="TEL":
            raise RuntimeError("VCardTel handles only 'TEL' type")
        if isinstance(value,libxml2.xmlNode):
            self.number=None
            self.type=[]
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='NUMBER':
                    self.number=str(n.getContent(),"utf-8","replace")
                elif n.name in ("HOME","WORK","VOICE","FAX","PAGER","MSG",
                        "CELL","VIDEO","BBS","MODEM","ISDN","PCS",
                        "PREF"):
                    self.type.append(n.name.lower())
                n=n.__next__
            if self.type==[]:
                self.type=["voice"]
            if not self.number:
                raise Empty("No tel number")
        else:
            t=rfc2425parameters.get("type")
            if t:
                self.type=t.split(",")
            else:
                self.type=["voice"]
            self.number=value
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode("tel",self.number,{"type":",".join(self.type)})
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,"TEL",None)
        for t in ("home","work","voice","fax","pager","msg","cell","video",
                "bbs","modem","isdn","pcs","pref"):
            if t in self.type:
                n.newChild(None,t.upper(),None)
        n.newTextChild(None,"NUMBER",to_utf8(self.number))
        return n

class VCardEmail(VCardField):
    """E-mail vCard field.

    :Ivariables:
        - `address`: e-mail address.
        - `type`: type of the address.
    :Types:
        - `address`: `str`
        - `type`: `list` of "home","work","internet" or "x400".
    """
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardEmail` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        VCardField.__init__(self,name)
        if not rfc2425parameters:
            rfc2425parameters={}
        if self.name.upper()!="EMAIL":
            raise RuntimeError("VCardEmail handles only 'EMAIL' type")
        if isinstance(value,libxml2.xmlNode):
            self.address=None
            self.type=[]
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='USERID':
                    self.address=str(n.getContent(),"utf-8","replace")
                elif n.name in ("HOME","WORK","INTERNET","X400"):
                    self.type.append(n.name.lower())
                n=n.__next__
            if self.type==[]:
                self.type=["internet"]
            if not self.address:
                raise Empty("No USERID")
        else:
            t=rfc2425parameters.get("type")
            if t:
                self.type=t.split(",")
            else:
                self.type=["internet"]
            self.address=value
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode("email",self.address,{"type":",".join(self.type)})
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,"EMAIL",None)
        for t in ("home","work","internet","x400"):
            if t in self.type:
                n.newChild(None,t.upper(),None)
        n.newTextChild(None,"USERID",to_utf8(self.address))
        return n

class VCardGeo(VCardField):
    """Geographical location vCard field.

    :Ivariables:
        - `lat`: the latitude.
        - `lon`: the longitude.
    :Types:
        - `lat`: `str`
        - `lon`: `str`
    """
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardGeo` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        _unused = rfc2425parameters
        VCardField.__init__(self,name)
        if self.name.upper()!="GEO":
            raise RuntimeError("VCardName handles only 'GEO' type")
        if isinstance(value,libxml2.xmlNode):
            self.lat,self.lon=[None]*2
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='LAT':
                    self.lat=str(n.getContent(),"utf-8")
                if n.name=='LON':
                    self.lon=str(n.getContent(),"utf-8")
                n=n.__next__
            if not self.lat or not self.lon:
                raise ValueError("Bad vcard GEO value")
        else:
            self.lat,self.lon=(unquote_semicolon(val) for val in non_quoted_semicolon_re.split(value))
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode("geo",';'.join(quote_semicolon(val) for val in
                (self.lat,self.lon)))
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,"GEO",None)
        n.newTextChild(None,"LAT",to_utf8(self.lat))
        n.newTextChild(None,"LON",to_utf8(self.lon))
        return n

class VCardOrg(VCardField):
    """Organization vCard field.

    :Ivariables:
        - `name`: organization name.
        - `unit`: organizational unit.
    :Types:
        - `name`: `str`
        - `unit`: `str`
    """
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardOrg` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        _unused = rfc2425parameters
        VCardField.__init__(self,name)
        if self.name.upper()!="ORG":
            raise RuntimeError("VCardName handles only 'ORG' type")
        if isinstance(value,libxml2.xmlNode):
            self.name,self.unit=None,""
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='ORGNAME':
                    self.name=str(n.getContent(),"utf-8")
                if n.name=='ORGUNIT':
                    self.unit=str(n.getContent(),"utf-8")
                n=n.__next__
            if not self.name:
                raise Empty("Bad vcard ORG value")
        else:
            sp=non_quoted_semicolon_re.split(value,1)
            if len(sp)>1:
                self.name,self.unit=(unquote_semicolon(val) for val in sp)
            else:
                self.name=unquote_semicolon(sp[0])
                self.unit=None
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        if self.unit:
            return rfc2425encode("org",';'.join(quote_semicolon(val) for val in
                                      (self.name,self.unit)))
        else:
            return rfc2425encode("org",str(quote_semicolon(self.name)))
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,"ORG",None)
        n.newTextChild(None,"ORGNAME",to_utf8(self.name))
        n.newTextChild(None,"ORGUNIT",to_utf8(self.unit))
        return n

class VCardCategories(VCardField):
    """Categories vCard field.

    :Ivariables:
        - `keywords`: category keywords.
    :Types:
        - `keywords`: `list` of `str`
    """
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardCategories` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        _unused = rfc2425parameters
        VCardField.__init__(self,name)
        self.name=name
        if self.name.upper()!="CATEGORIES":
            raise RuntimeError("VCardName handles only 'CATEGORIES' type")
        if isinstance(value,libxml2.xmlNode):
            self.keywords=[]
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='KEYWORD':
                    self.keywords.append(str(n.getContent(),"utf-8"))
                n=n.__next__
            if not self.keywords:
                raise Empty("Bad vcard CATEGORIES value")
        else:
            self.keywords=value.split(",")
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode("keywords",",".join(self.keywords))
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,"CATEGORIES",None)
        for k in self.keywords:
            n.newTextChild(None,"KEYWORD",to_utf8(k))
        return n

class VCardSound(VCardField):
    """Sound vCard field.

    :Ivariables:
        - `sound`: binary sound data (when `uri` is None)
        - `uri`: sound URI (when `sound` is None)
        - `phonetic`: phonetic transcription
    :Types:
        - `sound`: `str`
        - `uri`: `str`
        - `phonetic`: `str`"""
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardSound` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        VCardField.__init__(self,name)
        if not rfc2425parameters:
            rfc2425parameters={}
        self.uri,self.sound,self.phonetic=[None]*3
        if isinstance(value,libxml2.xmlNode):
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='BINVAL':
                    if (self.phonetic or self.uri):
                        raise ValueError("Bad SOUND value in vcard")
                    self.sound=base64.decodestring(n.getContent())
                if n.name=='PHONETIC':
                    if (self.sound or self.uri):
                        raise ValueError("Bad SOUND value in vcard")
                    self.phonetic=str(n.getContent(),"utf-8","replace")
                if n.name=='EXTVAL':
                    if (self.phonetic or self.sound):
                        raise ValueError("Bad SOUND value in vcard")
                    self.uri=str(n.getContent(),"utf-8","replace")
                n=n.__next__
            if (not self.phonetic and not self.uri and not self.sound):
                raise Empty("Bad SOUND value in vcard")
        else:
            if rfc2425parameters.get("value", "").lower()=="uri":
                self.uri=value
                self.sound=None
                self.phonetic=None
            else:
                self.sound=value
                self.uri=None
                self.phonetic=None
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        if self.uri:
            return rfc2425encode(self.name,self.uri,{"value":"uri"})
        elif self.sound:
            return rfc2425encode(self.name,self.sound)
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,self.name.upper(),None)
        if self.uri:
            n.newTextChild(None,"EXTVAL",to_utf8(self.uri))
        elif self.phonetic:
            n.newTextChild(None,"PHONETIC",to_utf8(self.phonetic))
        else:
            n.newTextChild(None,"BINVAL",binascii.b2a_base64(self.sound))
        return n

class VCardPrivacy(VCardField):
    """Privacy vCard field.

    :Ivariables:
        - `value`: privacy information about the vcard data ("public", "private"
          or "confidental")
    :Types:
        - `value`: `str` """
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardPrivacy` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        _unused = rfc2425parameters
        VCardField.__init__(self,name)
        if isinstance(value,libxml2.xmlNode):
            self.value=None
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='PUBLIC':
                    self.value="public"
                elif n.name=='PRIVATE':
                    self.value="private"
                elif n.name=='CONFIDENTAL':
                    self.value="confidental"
                n=n.__next__
            if not self.value:
                raise Empty
        else:
            self.value=value
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        return rfc2425encode(self.name,self.value)
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        if self.value in ("public","private","confidental"):
            n=parent.newChild(None,self.name.upper(),None)
            n.newChild(None,self.value.upper(),None)
            return n
        return None

class VCardKey(VCardField):
    """Key vCard field.

    :Ivariables:
        - `type`: key type.
        - `cred`: key data.
    :Types:
        - `type`: `str`
        - `cred`: `str` """
    def __init__(self,name,value,rfc2425parameters=None):
        """Initialize a `VCardKey` object.

        :Parameters:
            - `name`: field name
            - `value`: field value as string or an XML node
            - `rfc2425parameters`: optional RFC 2425 parameters
        :Types:
            - `name`: `str`
            - `value`: `str` or `libxml2.xmlNode`
            - `rfc2425parameters`: `dict`"""
        VCardField.__init__(self,name)
        if not rfc2425parameters:
            rfc2425parameters={}
        if isinstance(value,libxml2.xmlNode):
            self.type,self.cred=None,None
            n=value.children
            vns=get_node_ns(value)
            while n:
                if n.type!='element':
                    n=n.__next__
                    continue
                ns=get_node_ns(n)
                if (ns and vns and ns.getContent()!=vns.getContent()):
                    n=n.__next__
                    continue
                if n.name=='TYPE':
                    self.type=str(n.getContent(),"utf-8","replace")
                if n.name=='CRED':
                    self.cred=base64.decodestring(n.getContent())
                n=n.__next__
            if not self.cred:
                raise Empty("Bad %s value in vcard" % (name,))
        else:
            self.type=rfc2425parameters.get("type")
            self.cred=value
    def rfc2426(self):
        """RFC2426-encode the field content.

        :return: the field in the RFC 2426 format.
        :returntype: `str`"""
        if self.type:
            p={"type":self.type}
        else:
            p={}
        return rfc2425encode(self.name,self.cred,p)
    def as_xml(self,parent):
        """Create vcard-tmp XML representation of the field.

        :Parameters:
            - `parent`: parent node for the element
        :Types:
            - `parent`: `libxml2.xmlNode`

        :return: xml node with the field data.
        :returntype: `libxml2.xmlNode`"""
        n=parent.newChild(None,self.name.upper(),None)
        if self.type:
            n.newTextChild(None,"TYPE",self.type)
        n.newTextChild(None,"CRED",binascii.b2a_base64(self.cred))
        return n

class VCard(StanzaPayloadObject):
    """Jabber (vcard-temp) or RFC2426 vCard.

    :Ivariables:
        - `fn`: full name.
        - `n`: structural name.
        - `nickname`: nickname(s).
        - `photo`: photo(s).
        - `bday`: birthday date(s).
        - `adr`: address(es).
        - `label`: address label(s).
        - `tel`: phone number(s).
        - `email`: e-mail address(es).
        - `jabberid`: JID(s).
        - `mailer`: mailer(s).
        - `tz`: timezone(s).
        - `geo`: geolocation(s).
        - `title`: title(s).
        - `role`: role(s).
        - `logo`: logo(s).
        - `org`: organization(s).
        - `categories`: categories.
        - `note`: note(s).
        - `prodid`: product id(s).
        - `rev`: revision(s).
        - `sort-string`: sort string(s).
        - `sound`: sound(s).
        - `uid`: user identifier(s).
        - `url`: URL(s).
        - `class`: class(es).
        - `key`: key(s).
        - `desc`: description.
    :Types:
        - `fn`: `VCardString`,
        - `n`: `VCardName`,
        - `nickname`: `list` of `VCardString`
        - `photo`: `list` of `VCardImage`
        - `bday`: `list` of `VCardString`
        - `adr`: `list` of `VCardAdr`
        - `label`: `list` of `VCardLabel`
        - `tel`: `list` of `VCardTel`
        - `email`: `list` of `VCardEmail`
        - `jabberid`: `list` of `VCardJID`
        - `mailer`: `list` of `VCardString`
        - `tz`: `list` of `VCardString`
        - `geo`: `list` of `VCardGeo`
        - `title`: `list` of `VCardString`
        - `role`: `list` of `VCardString`
        - `logo`: `list` of `VCardImage`
        - `org`: `list` of `VCardOrg`
        - `categories`: `list` of `VCardCategories`
        - `note`: `list` of `VCardString`
        - `prodid`: `list` of `VCardString`
        - `rev`: `list` of `VCardString`
        - `sort-string`: `list` of `VCardString`
        - `sound`: `list` of `VCardSound`
        - `uid`: `list` of `VCardString`
        - `url`: `list` of `VCardString`
        - `class`: `list` of `VCardString`
        - `key`: `list` of `VCardKey`
        - `desc`: `list` of `VCardXString`
    """

    xml_element_name = "vCard"
    xml_element_namespace = VCARD_NS

    components={
            #"VERSION": (VCardString,"optional"),
            "FN": (VCardString,"required"),
            "N": (VCardName,"required"),
            "NICKNAME": (VCardString,"multi"),
            "PHOTO": (VCardImage,"multi"),
            "BDAY": (VCardString,"multi"),
            "ADR": (VCardAdr,"multi"),
            "LABEL": (VCardLabel,"multi"),
            "TEL": (VCardTel,"multi"),
            "EMAIL": (VCardEmail,"multi"),
            "JABBERID": (VCardJID,"multi"),
            "MAILER": (VCardString,"multi"),
            "TZ": (VCardString,"multi"),
            "GEO": (VCardGeo,"multi"),
            "TITLE": (VCardString,"multi"),
            "ROLE": (VCardString,"multi"),
            "LOGO": (VCardImage,"multi"),
            "AGENT": ("VCardAgent","ignore"), #FIXME: agent field
            "ORG": (VCardOrg,"multi"),
            "CATEGORIES": (VCardCategories,"multi"),
            "NOTE": (VCardString,"multi"),
            "PRODID": (VCardString,"multi"),
            "REV": (VCardString,"multi"),
            "SORT-STRING": (VCardString,"multi"),
            "SOUND": (VCardSound,"multi"),
            "UID": (VCardString,"multi"),
            "URL": (VCardString,"multi"),
            "CLASS": (VCardString,"multi"),
            "KEY": (VCardKey,"multi"),
            "DESC": (VCardXString,"multi"),
        };
    def __init__(self,data):
        """Initialize a VCard object from data which may be XML node
        or an RFC2426 string.

        :Parameters:
            - `data`: vcard to parse.
        :Types:
            - `data`: `libxml2.xmlNode`, `str` or `str`"""

        # to make pylint happy
        self.n = None
        del self.n

        self.content={}
        if isinstance(data,libxml2.xmlNode):
            self.__from_xml(data)
        else:
            self.__from_rfc2426(data)
        if not self.content.get("N") and self.content.get("FN"):
            s=self.content['FN'].value.replace(";",",")
            s=s.split(None,2)
            if len(s)==2:
                s="%s;%s;;;" % (s[1],s[0])
            elif len(s)==3:
                s="%s;%s;%s" % (s[2],s[0],s[1])
            else:
                s="%s;;;;" % (s[0],)
            self.content["N"]=VCardName("N",s)
        elif not self.content.get("FN") and self.content.get("N"):
            self.__make_fn()
        for c, (_unused, tp) in list(self.components.items()):
            if c in self.content:
                continue
            if tp=="required":
                raise ValueError("%s is missing" % (c,))
            elif tp=="multi":
                self.content[c]=[]
            elif tp=="optional":
                self.content[c]=None
            else:
                continue

    def __make_fn(self):
        """Initialize the mandatory `self.fn` from `self.n`.

        This is a workaround for buggy clients which set only one of them."""
        s=[]
        if self.n.prefix:
            s.append(self.n.prefix)
        if self.n.given:
            s.append(self.n.given)
        if self.n.middle:
            s.append(self.n.middle)
        if self.n.family:
            s.append(self.n.family)
        if self.n.suffix:
            s.append(self.n.suffix)
        s=" ".join(s)
        self.content["FN"]=VCardString("FN", s, empty_ok = True)

    def __from_xml(self,data):
        """Initialize a VCard object from XML node.

        :Parameters:
            - `data`: vcard to parse.
        :Types:
            - `data`: `libxml2.xmlNode`"""
        ns=get_node_ns(data)
        if ns and ns.getContent()!=VCARD_NS:
            raise ValueError("Not in the %r namespace" % (VCARD_NS,))
        if data.name!="vCard":
            raise ValueError("Bad root element name: %r" % (data.name,))
        n=data.children
        dns=get_node_ns(data)
        while n:
            if n.type!='element':
                n=n.__next__
                continue
            ns=get_node_ns(n)
            if (ns and dns and ns.getContent()!=dns.getContent()):
                n=n.__next__
                continue
            if n.name not in self.components:
                n=n.__next__
                continue
            cl,tp=self.components[n.name]
            if tp in ("required","optional"):
                if n.name in self.content:
                    raise ValueError("Duplicate %s" % (n.name,))
                try:
                    self.content[n.name]=cl(n.name,n)
                except Empty:
                    pass
            elif tp=="multi":
                if n.name not in self.content:
                    self.content[n.name]=[]
                try:
                    self.content[n.name].append(cl(n.name,n))
                except Empty:
                    pass
            n=n.__next__

    def __from_rfc2426(self,data):
        """Initialize a VCard object from an RFC2426 string.

        :Parameters:
            - `data`: vcard to parse.
        :Types:
            - `data`: `libxml2.xmlNode`, `str` or `str`"""
        data=from_utf8(data)
        lines=data.split("\n")
        started=0
        current=None
        for l in lines:
            if not l:
                continue
            if l[-1]=="\r":
                l=l[:-1]
            if not l:
                continue
            if l[0] in " \t":
                if current is None:
                    continue
                current+=l[1:]
                continue
            if not started and current and current.upper().strip()=="BEGIN:VCARD":
                started=1
            elif started and current.upper().strip()=="END:VCARD":
                current=None
                break
            elif current and started:
                self._process_rfc2425_record(current)
            current=l
        if started and current:
            self._process_rfc2425_record(current)

    def _process_rfc2425_record(self,data):
        """Parse single RFC2425 record and update attributes of `self`.

        :Parameters:
            - `data`: the record (probably multiline)
        :Types:
            - `data`: `str`"""
        label,value=data.split(":",1)
        value=value.replace("\\n","\n").replace("\\N","\n")
        psplit=label.lower().split(";")
        name=psplit[0]
        params=psplit[1:]
        if "." in name:
            name=name.split(".",1)[1]
        name=name.upper()
        if name in ("X-DESC","X-JABBERID"):
            name=name[2:]
        if name not in self.components:
            return
        if params:
            params=dict([p.split("=",1) for p in params])
        cl,tp=self.components[name]
        if tp in ("required","optional"):
            if name in self.content:
                raise ValueError("Duplicate %s" % (name,))
            try:
                self.content[name]=cl(name,value,params)
            except Empty:
                pass
        elif tp=="multi":
            if name not in self.content:
                self.content[name]=[]
            try:
                self.content[name].append(cl(name,value,params))
            except Empty:
                pass
        else:
            return
    def __repr__(self):
        return "<vCard of %r>" % (self.content["FN"].value,)
    def rfc2426(self):
        """Get the RFC2426 representation of `self`.

        :return: the UTF-8 encoded RFC2426 representation.
        :returntype: `str`"""
        ret="begin:VCARD\r\n"
        ret+="version:3.0\r\n"
        for _unused, value in list(self.content.items()):
            if value is None:
                continue
            if type(value) is list:
                for v in value:
                    ret+=v.rfc2426()
            else:
                v=value.rfc2426()
                ret+=v
        return ret+"end:VCARD\r\n"

    def complete_xml_element(self, xmlnode, _unused):
        """Complete the XML node with `self` content.

        Should be overriden in classes derived from `StanzaPayloadObject`.

        :Parameters:
            - `xmlnode`: XML node with the element being built. It has already
              right name and namespace, but no attributes or content.
            - `_unused`: document to which the element belongs.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`
            - `_unused`: `libxml2.xmlDoc`"""
        for _unused1, value in list(self.content.items()):
            if value is None:
                continue
            if type(value) is list:
                for v in value:
                    v.as_xml(xmlnode)
            else:
                value.as_xml(xmlnode)

    def __getattr__(self,name):
        try:
            return self.content[name.upper().replace("_","-")]
        except KeyError:
            raise AttributeError("Attribute %r not found" % (name,))
    def __getitem__(self,name):
        return self.content[name.upper()]

# vi: sts=4 et sw=4
