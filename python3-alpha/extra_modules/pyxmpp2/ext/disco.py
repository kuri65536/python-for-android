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
# pylint: disable-msg=W0201
"""Jabber Service Discovery support.

Normative reference:
  - `JEP 30 <http://www.jabber.org/jeps/jep-0030.html>`__
"""



__docformat__="restructuredtext en"

raise ImportError("{0} is not yet rewritten for PyXMPP2".format(__name__))

import warnings

import libxml2

from ..xmlextra import common_doc,common_root
from ..jid import JID
from .. import cache

from ..utils import to_utf8
from ..objects import StanzaPayloadWrapperObject
from ..exceptions import ProtocolError

DISCO_NS="http://jabber.org/protocol/disco"
DISCO_ITEMS_NS=DISCO_NS+"#items"
DISCO_INFO_NS=DISCO_NS+"#info"

class DiscoItem(StanzaPayloadWrapperObject):
    """An item of disco#items reply.

    :Ivariables:
        - `jid`: the JID of the item.
        - `node`: node name of the item.
        - `name`: name of the item.
        - `action`: action of the item.
        - `disco`: the disco reply this is the part of.
        - `xmlnode`: XML element describing the item.
    :Types:
        - `jid`: `JID`
        - `node`: `str`
        - `name`: `str`
        - `action`: `str`
        - `disco`: `DiscoItems`
        - `xmlnode`: `libxml2.xmlNode`
    """
    def __init__(self,disco,xmlnode_or_jid,node=None,name=None,action=None):
        """Initialize an `DiscoItem` object.

        :Parameters:
            - `disco`: the disco#items reply `self` is a part of.
            - `xmlnode_or_jid`: XML element describing the item or the JID of
              the item.
            - `node`: disco node of the item.
            - `name`: name of the item.
            - `action`: 'action' attribute of the item.
        :Types:
            - `disco`: `DiscoItems`
            - `xmlnode_or_jid`: `libxml2.xmlNode` or `JID`
            - `node`: `str`
            - `name`: `str`
            - `action`: `str`
        """
        self.disco=disco
        if isinstance(xmlnode_or_jid,JID):
            if disco:
                self.xmlnode=disco.xmlnode.newChild(None,"item",None)
            else:
                self.xmlnode=common_root.newChild(None,"item",None)
                ns=self.xmlnode.newNs(DISCO_ITEMS_NS,None)
                self.xmlnode.setNs(ns)
            self.set_jid(xmlnode_or_jid)
            self.set_name(name)
            self.set_node(node)
            self.set_action(action)
        else:
            if disco is None:
                self.xmlnode=xmlnode_or_jid.copyNode(1)
            else:
                self.xmlnode=xmlnode_or_jid
            if name:
                self.set_name(name)
            if node:
                self.set_node(node)
            if action:
                self.set_action(action)
        self.xpath_ctxt=common_doc.xpathNewContext()
        self.xpath_ctxt.setContextNode(self.xmlnode)
        self.xpath_ctxt.xpathRegisterNs("d",DISCO_ITEMS_NS)

    def __del__(self):
        if self.disco is None:
            if self.xmlnode:
                self.xmlnode.unlinkNode()
                self.xmlnode.freeNode()
                self.xmlnode=None
        if self.xpath_ctxt:
            self.xpath_ctxt.xpathFreeContext()

    def __str__(self):
        return self.xmlnode.serialize()

    def remove(self):
        """Remove `self` from the containing `DiscoItems` object."""
        if self.disco is None:
            return
        self.xmlnode.unlinkNode()
        oldns=self.xmlnode.ns()
        ns=self.xmlnode.newNs(oldns.getContent(),None)
        self.xmlnode.replaceNs(oldns,ns)
        common_root.addChild(self.xmlnode())
        self.disco=None

    def get_name(self):
        """Get the name of the item.

        :return: the name of the item or `None`.
        :returntype: `str`"""
        name = self.xmlnode.prop("name")
        if name is None:
            return None
        return name.decode("utf-8")

    def set_name(self, name):
        """Set the name of the item.

        :Parameters:
            - `name`: the new name or `None`.
        :Types:
            - `name`: `str` """
        if name is None:
            if self.xmlnode.hasProp("name"):
                self.xmlnode.unsetProp("name")
            return
        name = str(name)
        self.xmlnode.setProp("name", name.encode("utf-8"))

    name = property(get_name, set_name)

    def get_node(self):
        """Get the node of the item.

        :return: the node of the item or `None`.
        :returntype: `str`"""
        node = self.xmlnode.prop("node")
        if node is None:
            return None
        return node.decode("utf-8")

    def set_node(self,node):
        """Set the node of the item.

        :Parameters:
            - `node`: the new node or `None`.
        :Types:
            - `node`: `str`
        """
        if node is None:
            if self.xmlnode.hasProp("node"):
                self.xmlnode.unsetProp("node")
            return
        node = str(node)
        self.xmlnode.setProp("node", node.encode("utf-8"))

    node = property(get_node, set_node)

    def get_action(self):
        """Get the action attribute of the item.

        :return: the action of the item or `None`.
        :returntype: `str`"""
        action=self.xmlnode.prop("action")
        if action is None:
            return None
        return action.decode("utf-8")

    def set_action(self,action):
        """Set the action of the item.

        :Parameters:
            - `action`: the new action or `None`.
        :Types:
            - `action`: `str`
        """
        if action is None:
            if self.xmlnode.hasProp("action"):
                self.xmlnode.unsetProp("action")
            return
        if action not in ("remove","update"):
            raise ValueError("Action must be 'update' or 'remove'")
        action = str(action)
        self.xmlnode.setProp("action", action.encode("utf-8"))

    action = property(get_action, set_action)

    def get_jid(self):
        """Get the JID of the item.

        :return: the JID of the item.
        :returntype: `JID`"""
        jid = self.xmlnode.prop("jid")
        return JID( jid.decode("utf-8") )

    def set_jid(self,jid):
        """Set the JID of the item.

        :Parameters:
            - `jid`: the new jid.
        :Types:
            - `jid`: `JID`
        """
        self.xmlnode.setProp("jid", jid.as_unicode().encode("utf-8"))

    jid = property(get_jid, set_jid)

class DiscoIdentity(StanzaPayloadWrapperObject):
    """An <identity/> element of disco#info reply.

    Identifies an item by its name, category and type.

    :Ivariables:
        - `disco`: the disco reply this is the part of.
        - `xmlnode`: XML element describing the identity.
    :Types:
        - `disco`: `DiscoInfo`
        - `xmlnode`: `libxml2.xmlNode`
    """
    def __init__(self, disco, xmlnode_or_name, item_category=None, item_type=None, replace=False):
        """Initialize an `DiscoIdentity` object.

        :Parameters:
            - `disco`: the disco#info reply `self` is a part of.
            - `xmlnode_or_name`: XML element describing the identity or the
              name of the item described.
            - `item_category`: category of the item described.
            - `item_type`: type of the item described.
            - `replace`: if `True` than all other <identity/> elements in
              `disco` will be removed.
        :Types:
            - `disco`: `DiscoItems`
            - `xmlnode_or_name`: `libxml2.xmlNode` or `str`
            - `item_category`: `str`
            - `item_type`: `str`
            - `replace`: `bool`
        """
        self.disco=disco
        if disco and replace:
            old=disco.xpath_ctxt.xpathEval("d:identity")
            if old:
                for n in old:
                    n.unlinkNode()
                    n.freeNode()
        if isinstance(xmlnode_or_name,libxml2.xmlNode):
            if disco is None:
                self.xmlnode=xmlnode_or_name.copyNode(1)
            else:
                self.xmlnode=xmlnode_or_name
        elif not item_category:
            raise ValueError("DiscoInfo requires category")
        elif not item_type:
            raise ValueError("DiscoInfo requires type")
        else:
            if disco:
                self.xmlnode=disco.xmlnode.newChild(None,"identity",None)
            else:
                self.xmlnode=common_root.newChild(None,"identity",None)
                ns=self.xmlnode.newNs(DISCO_INFO_NS,None)
                self.xmlnode.setNs(ns)
            self.set_name(xmlnode_or_name)
            self.set_category(item_category)
            self.set_type(item_type)
        self.xpath_ctxt=common_doc.xpathNewContext()
        self.xpath_ctxt.setContextNode(self.xmlnode)
        self.xpath_ctxt.xpathRegisterNs("d",DISCO_INFO_NS)

    def __del__(self):
        if self.disco is None:
            if self.xmlnode:
                self.xmlnode.unlinkNode()
                self.xmlnode.freeNode()
                self.xmlnode=None
        if self.xpath_ctxt:
            self.xpath_ctxt.xpathFreeContext()

    def __str__(self):
        return self.xmlnode.serialize()

    def remove(self):
        """Remove `self` from the containing `DiscoInfo` object."""
        if self.disco is None:
            return
        self.xmlnode.unlinkNode()
        oldns=self.xmlnode.ns()
        ns=self.xmlnode.newNs(oldns.getContent(),None)
        self.xmlnode.replaceNs(oldns,ns)
        common_root.addChild(self.xmlnode())
        self.disco=None

    def get_name(self):
        """Get the name of the item.

        :return: the name of the item or `None`.
        :returntype: `str`"""
        var = self.xmlnode.prop("name")
        if not var:
            var = ""
        return var.decode("utf-8")

    def set_name(self,name):
        """Set the name of the item.

        :Parameters:
            - `name`: the new name or `None`.
        :Types:
            - `name`: `str` """
        if not name:
            raise ValueError("name is required in DiscoIdentity")
        name = str(name)
        self.xmlnode.setProp("name", name.encode("utf-8"))

    name = property(get_name, set_name)

    def get_category(self):
        """Get the category of the item.

        :return: the category of the item.
        :returntype: `str`"""
        var = self.xmlnode.prop("category")
        if not var:
            var = "?"
        return var.decode("utf-8")

    def set_category(self, category):
        """Set the category of the item.

        :Parameters:
            - `category`: the new category.
        :Types:
            - `category`: `str` """
        if not category:
            raise ValueError("Category is required in DiscoIdentity")
        category = str(category)
        self.xmlnode.setProp("category", category.encode("utf-8"))

    category = property(get_category, set_category)

    def get_type(self):
        """Get the type of the item.

        :return: the type of the item.
        :returntype: `str`"""
        item_type = self.xmlnode.prop("type")
        if not item_type:
            item_type = "?"
        return item_type.decode("utf-8")

    def set_type(self, item_type):
        """Set the type of the item.

        :Parameters:
            - `item_type`: the new type.
        :Types:
            - `item_type`: `str` """
        if not item_type:
            raise ValueError("Type is required in DiscoIdentity")
        item_type = str(item_type)
        self.xmlnode.setProp("type", item_type.encode("utf-8"))

    type = property(get_type, set_type)

class DiscoItems(StanzaPayloadWrapperObject):
    """A disco#items response or publish-request object.

    :Ivariables:
        - `node`: node name of the disco#items element.
        - `items`: items in the disco#items element.
        - `xmlnode`: XML element listing the items.
    :Types:
        - `node`: `str`
        - `items`: `tuple` of `DiscoItem`
        - `xmlnode`: `libxml2.xmlNode`
    """
    def __init__(self,xmlnode_or_node=None):
        """Initialize an `DiscoItems` object.

        Wrap an existing disco#items XML element or create a new one.

        :Parameters:
            - `xmlnode_or_node`: XML node to be wrapped into `self` or an item
              node name.
        :Types:
            - `xmlnode_or_node`: `libxml2.xmlNode` or `str`"""
        self.xmlnode=None
        self.xpath_ctxt=None
        if isinstance(xmlnode_or_node,libxml2.xmlNode):
            ns=xmlnode_or_node.ns()
            if ns.getContent() != DISCO_ITEMS_NS:
                raise ValueError("Bad disco-items namespace")
            self.xmlnode=xmlnode_or_node.docCopyNode(common_doc,1)
            common_root.addChild(self.xmlnode)
            self.ns=self.xmlnode.ns()
        else:
            self.xmlnode=common_root.newChild(None,"query",None)
            self.ns=self.xmlnode.newNs(DISCO_ITEMS_NS,None)
            self.xmlnode.setNs(self.ns)
            self.set_node(xmlnode_or_node)
        self.xpath_ctxt=common_doc.xpathNewContext()
        self.xpath_ctxt.setContextNode(self.xmlnode)
        self.xpath_ctxt.xpathRegisterNs("d",DISCO_ITEMS_NS)

    def __del__(self):
        if self.xmlnode:
            self.xmlnode.unlinkNode()
            self.xmlnode.freeNode()
            self.xmlnode=None
        if self.xpath_ctxt:
            self.xpath_ctxt.xpathFreeContext()
            self.xpath_ctxt=None

    def get_node(self):
        """Get the node address of the `DiscoItems` object.

        :return: the node name.
        :returntype: `str`"""
        node = self.xmlnode.prop("node")
        if not node:
            return None
        return node.decode("utf-8")

    def set_node(self, node):
        """Set the node of the disco#item element.

        :Parameters:
            - `node`: the new node or `None`.
        :Types:
            - `node`: `str`
        """
        if node is None:
            if self.xmlnode.hasProp("node"):
                self.xmlnode.unsetProp("node")
            return
        node = str(node)
        self.xmlnode.setProp("node", node.encode("utf-8"))

    node = property(get_node, set_node)

    def get_items(self):
        """Get the items contained in `self`.

        :return: the items contained.
        :returntype: `list` of `DiscoItem`"""
        ret=[]
        l=self.xpath_ctxt.xpathEval("d:item")
        if l is not None:
            for i in l:
                ret.append(DiscoItem(self, i))
        return ret

    def set_items(self, item_list):
        """Set items in the disco#items object.

        All previous items are removed.

        :Parameters:
            - `item_list`: list of items or item properties
              (jid,node,name,action).
        :Types:
            - `item_list`: sequence of `DiscoItem` or sequence of sequences
        """
        for item in self.items:
            item.remove()
        for item in item_list:
            try:
                self.add_item(item.jid,item.node,item.name,item.action)
            except AttributeError:
                self.add_item(*item)

    items = property(get_items, set_items, doc = "List of `DiscoItems`")

    def invalidate_items(self):
        """Clear cached item list."""
        warnings.warn("DiscoItems.invalidate_items() is deprecated and not needed any more.", DeprecationWarning, stacklevel=1)

    def add_item(self,jid,node=None,name=None,action=None):
        """Add a new item to the `DiscoItems` object.

        :Parameters:
            - `jid`: item JID.
            - `node`: item node name.
            - `name`: item name.
            - `action`: action for a "disco push".
        :Types:
            - `jid`: `pyxmpp.JID`
            - `node`: `str`
            - `name`: `str`
            - `action`: `str`

        :returns: the item created.
        :returntype: `DiscoItem`."""
        return DiscoItem(self,jid,node,name,action)

    def has_item(self,jid,node=None):
        """Check if `self` contains an item.

        :Parameters:
            - `jid`: JID of the item.
            - `node`: node name of the item.
        :Types:
            - `jid`: `JID`
            - `node`: `libxml2.xmlNode`

        :return: `True` if the item is found in `self`.
        :returntype: `bool`"""
        l=self.xpath_ctxt.xpathEval("d:item")
        if l is None:
            return False
        for it in l:
            di=DiscoItem(self,it)
            if di.jid==jid and di.node==node:
                return True
        return False

class DiscoInfo(StanzaPayloadWrapperObject):
    """A disco#info response object.

    :Ivariables:
        - `node`: node name of the disco#info element (cached).
        - `identities`: identities in the disco#info object.
        - `features`: features in the disco#info object.
        - `xmlnode`: XML element listing the items.
    :Types:
        - `node`: `str`
        - `identities`: `tuple` of `DiscoIdentity`
        - `features`: `tuple` of `str`
        - `xmlnode`: `libxml2.xmlNode`
    """
    def __init__(self,xmlnode_or_node=None, parent=None, doc=None):
        """Initialize an `DiscoInfo` object.

        Wrap an existing disco#info XML element or create a new one.

        :Parameters:
            - `xmlnode_or_node`: XML node to be wrapped into `self` or an item
              node name.
            - `parent`: parent node for the `DiscoInfo` element.
            - `doc`: document for the `DiscoInfo` element.
        :Types:
            - `xmlnode_or_node`: `libxml2.xmlNode` or `str`
            - `parent`: `libxml2.xmlNode`
            - `doc`: `libxml2.xmlDoc`
            """
        self.xmlnode=None
        self.xpath_ctxt=None
        if not doc:
            doc=common_doc
        if not parent:
            parent=common_root
        if isinstance(xmlnode_or_node,libxml2.xmlNode):
            ns=xmlnode_or_node.ns()
            if ns.getContent() != DISCO_INFO_NS:
                raise ValueError("Bad disco-info namespace")
            self.xmlnode=xmlnode_or_node.docCopyNode(doc,1)
            parent.addChild(self.xmlnode)
        else:
            self.xmlnode=parent.newChild(None,"query",None)
            self.ns=self.xmlnode.newNs(DISCO_INFO_NS,None)
            self.xmlnode.setNs(self.ns)
            self.set_node(xmlnode_or_node)

        self.xpath_ctxt=doc.xpathNewContext()
        self.xpath_ctxt.setContextNode(self.xmlnode)
        self.xpath_ctxt.xpathRegisterNs("d",DISCO_INFO_NS)

    def __del__(self):
        if self.xmlnode:
            self.xmlnode.unlinkNode()
            self.xmlnode.freeNode()
            self.xmlnode=None
        if self.xpath_ctxt:
            self.xpath_ctxt.xpathFreeContext()
            self.xpath_ctxt=None

    def get_node(self):
        """Get the node address of the `DiscoInfo` object.

        :return: the node name.
        :returntype: `str`"""

        node=self.xmlnode.prop("node")
        if not node:
            return None
        return node.decode("utf-8")

    def set_node(self,node):
        """Set the node of the disco#info element.

        :Parameters:
            - `node`: the new node or `None`.
        :Types:
            - `node`: `str`
        """
        if node is None:
            if self.xmlnode.hasProp("node"):
                self.xmlnode.unsetProp("node")
            return
        node = str(node)
        self.xmlnode.setProp("node", node.encode("utf-8"))

    node = property(get_node, set_node)

    def get_features(self):
        """Get the features contained in `self`.

        :return: the list of features.
        :returntype: `list` of `str`"""
        l = self.xpath_ctxt.xpathEval("d:feature")
        ret = []
        for f in l:
            if f.hasProp("var"):
                ret.append( f.prop("var").decode("utf-8") )
        return ret

    def set_features(self, features):
        """Set features in the disco#info object.

        All existing features are removed from `self`.

        :Parameters:
            - `features`: list of features.
        :Types:
            - `features`: sequence of `str`
        """
        for var in self.features:
            self.remove_feature(var)

        for var in features:
            self.add_feature(var)

    features = property(get_features, set_features)

    def has_feature(self,var):
        """Check if `self` contains the named feature.

        :Parameters:
            - `var`: the feature name.
        :Types:
            - `var`: `str`

        :return: `True` if the feature is found in `self`.
        :returntype: `bool`"""
        if not var:
            raise ValueError("var is None")
        if '"' not in var:
            expr='d:feature[@var="%s"]' % (var,)
        elif "'" not in var:
            expr="d:feature[@var='%s']" % (var,)
        else:
            raise ValueError("Invalid feature name")

        l=self.xpath_ctxt.xpathEval(to_utf8(expr))
        if l:
            return True
        else:
            return False

    def invalidate_features(self):
        """Clear cached feature list."""
        warnings.warn("DiscoInfo.invalidate_features() is deprecated and not needed any more.", DeprecationWarning, stacklevel=1)

    def add_feature(self,var):
        """Add a feature to `self`.

        :Parameters:
            - `var`: the feature name.
        :Types:
            - `var`: `str`"""
        if self.has_feature(var):
            return
        n=self.xmlnode.newChild(None, "feature", None)
        n.setProp("var", to_utf8(var))

    def remove_feature(self,var):
        """Remove a feature from `self`.

        :Parameters:
            - `var`: the feature name.
        :Types:
            - `var`: `str`"""
        if not var:
            raise ValueError("var is None")
        if '"' not in var:
            expr='d:feature[@var="%s"]' % (var,)
        elif "'" not in var:
            expr="d:feature[@var='%s']" % (var,)
        else:
            raise ValueError("Invalid feature name")

        l=self.xpath_ctxt.xpathEval(expr)
        if not l:
            return

        for f in l:
            f.unlinkNode()
            f.freeNode()

    def get_identities(self):
        """List the identity objects contained in `self`.

        :return: the list of identities.
        :returntype: `list` of `DiscoIdentity`"""
        ret=[]
        l=self.xpath_ctxt.xpathEval("d:identity")
        if l is not None:
            for i in l:
                ret.append(DiscoIdentity(self,i))
        return ret

    def set_identities(self,identities):
        """Set identities in the disco#info object.

        Remove all existing identities from `self`.

        :Parameters:
            - `identities`: list of identities or identity properties
              (jid,node,category,type,name).
        :Types:
            - `identities`: sequence of `DiscoIdentity` or sequence of sequences
        """
        for identity in self.identities:
            identity.remove()
        for identity in identities:
            try:
                self.add_identity(identity.name,identity.category,identity.type)
            except AttributeError:
                self.add_identity(*identity)

    identities = property(get_identities, set_identities)

    def identity_is(self,item_category,item_type=None):
        """Check if the item described by `self` belongs to the given category
        and type.

        :Parameters:
            - `item_category`: the category name.
            - `item_type`: the type name. If `None` then only the category is
              checked.
        :Types:
            - `item_category`: `str`
            - `item_type`: `str`

        :return: `True` if `self` contains at least one <identity/> object with
            given type and category.
        :returntype: `bool`"""
        if not item_category:
            raise ValueError("bad category")
        if not item_type:
            type_expr=""
        elif '"' not in item_type:
            type_expr=' and @type="%s"' % (item_type,)
        elif "'" not in type:
            type_expr=" and @type='%s'" % (item_type,)
        else:
            raise ValueError("Invalid type name")
        if '"' not in item_category:
            expr='d:identity[@category="%s"%s]' % (item_category,type_expr)
        elif "'" not in item_category:
            expr="d:identity[@category='%s'%s]" % (item_category,type_expr)
        else:
            raise ValueError("Invalid category name")

        l=self.xpath_ctxt.xpathEval(to_utf8(expr))
        if l:
            return True
        else:
            return False

    def invalidate_identities(self):
        """Clear cached identity list."""
        warnings.warn("DiscoInfo.invalidate_identities() is deprecated and not needed any more.", DeprecationWarning, stacklevel=1)

    def add_identity(self,item_name,item_category=None,item_type=None):
        """Add an identity to the `DiscoInfo` object.

        :Parameters:
            - `item_name`: name of the item.
            - `item_category`: category of the item.
            - `item_type`: type of the item.
        :Types:
            - `item_name`: `str`
            - `item_category`: `str`
            - `item_type`: `str`

        :returns: the identity created.
        :returntype: `DiscoIdentity`"""
        return DiscoIdentity(self,item_name,item_category,item_type)

class DiscoCacheFetcherBase(cache.CacheFetcher):
    """Base class for disco cache fetchers.

    :Cvariables:
        - `stream`: stream used by the fetcher.
        - `disco_class`: disco class to be used (`DiscoInfo` or `DiscoItems`).
    :Types:
        - `stream`: `pyxmpp.stream.Stream`
        - `disco_class`: `classobj`
    """
    stream=None
    disco_class=None
    def fetch(self):
        """Initialize the Service Discovery process."""
        from ..iq import Iq
        jid,node = self.address
        iq = Iq(to_jid = jid, stanza_type = "get")
        disco = self.disco_class(node)
        iq.add_content(disco.xmlnode)
        self.stream.set_response_handlers(iq,self.__response, self.__error,
                self.__timeout)
        self.stream.send(iq)

    def __response(self,stanza):
        """Handle successful disco response.

        :Parameters:
            - `stanza`: the stanza received.
        :Types:
            - `stanza`: `pyxmpp.stanza.Stanza`"""
        try:
            d=self.disco_class(stanza.get_query())
            self.got_it(d)
        except ValueError as e:
            self.error(e)

    def __error(self,stanza):
        """Handle disco error response.

        :Parameters:
            - `stanza`: the stanza received.
        :Types:
            - `stanza`: `pyxmpp.stanza.Stanza`"""
        try:
            self.error(stanza.get_error())
        except ProtocolError:
            from ..error import StanzaErrorNode
            self.error(StanzaErrorNode("undefined-condition"))

    def __timeout(self,stanza):
        """Handle disco timeout."""
        pass

def register_disco_cache_fetchers(cache_suite,stream):
    """Register Service Discovery cache fetchers into given
    cache suite and using the stream provided.

    :Parameters:
        - `cache_suite`: the cache suite where the fetchers are to be
          registered.
        - `stream`: the stream to be used by the fetchers.
    :Types:
        - `cache_suite`: `cache.CacheSuite`
        - `stream`: `pyxmpp.stream.Stream`
    """
    tmp=stream
    class DiscoInfoCacheFetcher(DiscoCacheFetcherBase):
        """Cache fetcher for DiscoInfo."""
        stream=tmp
        disco_class=DiscoInfo
    class DiscoItemsCacheFetcher(DiscoCacheFetcherBase):
        """Cache fetcher for DiscoItems."""
        stream=tmp
        disco_class=DiscoItems
    cache_suite.register_fetcher(DiscoInfo,DiscoInfoCacheFetcher)
    cache_suite.register_fetcher(DiscoItems,DiscoItemsCacheFetcher)

# vi: sts=4 et sw=4
