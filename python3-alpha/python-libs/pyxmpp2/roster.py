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

"""XMPP-IM roster handling.

This module provides a `Roster` class representing the roster (XMPP contact
list), a `RosterClient` class for requesting the roster and manipulating 
the roster on server and related clases (`RosterItem`, `RosterPayload`).

The roster contains JIDs of the contacts, their display names, names of the
groups they belong to and presence subscription information. 

The interface provided by this module can be used to add  and remove items
in the roster and to change the name and group infromation of the items,
however the presence subscription should be managed by different means (handling
of the `Presence` stanzas) and the `Roster` object provides only the current
subscription state information.

Normative reference:
  - :RFC:`6121`
"""



__docformat__ = "restructuredtext en"

import logging

from collections import Sequence, Mapping

from .etree import ElementTree
from .settings import XMPPSettings
from .jid import JID
from .iq import Iq
from .interfaces import XMPPFeatureHandler
from .interfaces import iq_set_stanza_handler
from .interfaces import StanzaPayload, payload_element_name
from .interfaces import EventHandler, event_handler, Event
from .interfaces import NO_CHANGE
from .streamevents import AuthorizedEvent, GotFeaturesEvent
from .exceptions import BadRequestProtocolError, NotAcceptableProtocolError

logger = logging.getLogger("pyxmpp2.roster")

ROSTER_NS = "jabber:iq:roster"
ROSTER_QNP = "{{{0}}}".format(ROSTER_NS)
QUERY_TAG = ROSTER_QNP + "query"
ITEM_TAG = ROSTER_QNP + "item"
GROUP_TAG = ROSTER_QNP + "group"
FEATURE_ROSTERVER = "{urn:xmpp:features:rosterver}ver"
FEATURE_APPROVALS = "{urn:xmpp:features:pre-approval}sub"

class RosterReceivedEvent(Event):
    """Event emitted when roster is received from server.
    
    :Ivariables:
        - `roster_client`: roster client object that emitted this event
        - `roster`: the roster received
    :Types:
        - `roster_client`: `RosterClient`
        - `roster`: `Roster`
    """
    # pylint: disable=R0903
    def __init__(self, roster_client, roster):
        self.roster_client = roster_client
        self.roster = roster

    def __str__(self):
        return "Roster received ({0} items)".format(len(self.roster))

class RosterUpdatedEvent(Event):
    """Event emitted when roster update is received.
    
    :Ivariables:
        - `roster_client`: roster client object that emitted this event
        - `item`: the update received
    :Types:
        - `roster_client`: `RosterClient`
        - `item`: `RosterItem`
    """
    # pylint: disable=R0903
    def __init__(self, roster_client, old_item, item):
        self.roster_client = roster_client
        self.old_item = old_item
        self.item = item

    def __str__(self):
        return "Roster update received for: {0}".format(self.item.jid)

class RosterNotReceivedEvent(Event):
    """Event emitted when a roster request fails.
    
    :Ivariables:
        - `roster_client`: roster client object that emitted this event
        - `stanza`: the invalid or error stanza received, `None` in case of
          time-out.
    :Types:
        - `roster_client`: `RosterClient`
        - `stanza`: `Stanza`
    """
    # pylint: disable=R0903
    def __init__(self, roster_client, stanza):
        self.roster_client = roster_client
        self.stanza = stanza 

    def __str__(self):
        if self.stanza is None:
            return "Roster fetch fail (timeout)"
        if self.stanza.stanza_type == "error":
            cond = self.stanza.error.condition_name
            text = self.stanza.error.text
            if text:
                return "Roster fetch fail: {0} ({1})".format(cond, text)
            else:
                return "Roster fetch fail: {0}".format(cond)
        else:
            return "Roster fetch fail: invalid response from server"

class RosterItem(object):
    """
    Roster item.

    Represents part of a roster, or roster update request.

    :Ivariables:
        - `jid`: the JID
        - `name`: visible name
        - `groups`: roster groups the item belongs to
        - `subscription`: subscription type (None, "to", "from", "both",
                                                                or "remove")
        - `ask`: "subscribe" if there was unreplied subsription request sent
        - `approved`: `True` if the entry subscription is pre-approved
    :Types:
        - `jid`: `JID`
        - `name`: `str`
        - `groups`: `set` of `str`
        - `subscription`: `str`
        - `ask`: `str`
        - `approved`: `bool`
    """
    def __init__(self, jid, name = None, groups = None,
                            subscription = None, ask = None, approved = None):
        """
        Initialize a roster item element.

        :Parameters:
            - `jid`: entry jid
            - `name`: item visible name
            - `groups`: iterable of groups the item is member of
            - `subscription`: subscription type (None, "to", "from", "both" 
                                                                    or "remove")
            - `ask`: "subscribe" if there was unreplied subscription request
              sent
            - `approved`: `True` if the entry subscription is pre-approved
        """
        # pylint: disable=R0913
        self.jid = JID(jid)
        if name is not None:
            self.name = str(name)
        else:
            self.name = None
        if groups is not None:
            self.groups = set(groups)
        else:
            self.groups = set()
        if subscription == "none":
            subscription = None
        # no verify because of RFC 6121, section 2.1.2.5 (client MUST ignore...)
        self.subscription = subscription
        if ask is not None:
            self.ask = ask
        else:
            self.ask = None
        self.approved = bool(approved)
        self._duplicate_group = False

    @classmethod
    def from_xml(cls, element):
        """Make a RosterItem from an XML element.

        :Parameters:
            - `element`: the XML element
        :Types:
            - `element`: :etree:`ElementTree.Element`
        
        :return: a freshly created roster item
        :returntype: `cls`
        """
        if element.tag != ITEM_TAG:
            raise ValueError("{0!r} is not a roster item".format(element))
        try:
            jid = JID(element.get("jid"))
        except ValueError:
            raise BadRequestProtocolError("Bad item JID")
        subscription = element.get("subscription")
        ask = element.get("ask")
        name = element.get("name")
        duplicate_group = False
        groups = set()
        for child in element:
            if child.tag != GROUP_TAG:
                continue
            group = child.text
            if group is None:
                group = ""
            if group in groups:
                duplicate_group = True
            else:
                groups.add(group)
        approved = element.get("approved")
        if approved == "true":
            approved = True
        elif approved in ("false", None):
            approved = False
        else:
            logger.debug("RosterItem.from_xml: got unknown 'approved':"
                            " {0!r}, changing to False".format(approved))
            approved = False
        result = cls(jid, name, groups, subscription, ask, approved)
        result._duplicate_group = duplicate_group
        return result

    def as_xml(self, parent = None):
        """Make an XML element from self.

        :Parameters:
            - `parent`: Parent element
        :Types:
            - `parent`: :etree:`ElementTree.Element`
        """
        if parent is not None:
            element = ElementTree.SubElement(parent, ITEM_TAG)
        else:
            element = ElementTree.Element(ITEM_TAG)
        element.set("jid", str(self.jid))
        if self.name is not None:
            element.set("name", self.name)
        if self.subscription is not None:
            element.set("subscription", self.subscription)
        if self.ask:
            element.set("ask", self.ask)
        if self.approved:
            element.set("approved", "true")
        for group in self.groups:
            ElementTree.SubElement(element, GROUP_TAG).text = group
        return element

    def _verify(self, valid_subscriptions, fix):
        """Check if `self` is valid roster item.

        Valid item must have proper `subscription` and valid value for 'ask'.

        :Parameters:
            - `valid_subscriptions`: sequence of valid subscription values
            - `fix`: if `True` than replace invalid 'subscription' and 'ask'
              values with the defaults
        :Types:
            - `fix`: `bool`

        :Raise: `ValueError` if the item is invalid.
        """
        if self.subscription not in valid_subscriptions:
            if fix:
                logger.debug("RosterItem.from_xml: got unknown 'subscription':"
                        " {0!r}, changing to None".format(self.subscription))
                self.subscription = None
            else:
                raise ValueError("Bad 'subscription'")
        if self.ask not in (None, "subscribe"):
            if fix:
                logger.debug("RosterItem.from_xml: got unknown 'ask':"
                                " {0!r}, changing to None".format(self.ask))
                self.ask = None
            else:
                raise ValueError("Bad 'ask'")

    def verify_roster_result(self, fix = False):
        """Check if `self` is valid roster item.

        Valid item must have proper `subscription` value other than 'remove'
        and valid value for 'ask'.

        :Parameters:
            - `fix`: if `True` than replace invalid 'subscription' and 'ask'
              values with the defaults
        :Types:
            - `fix`: `bool`

        :Raise: `ValueError` if the item is invalid.
        """
        self._verify((None, "from", "to", "both"), fix)

    def verify_roster_push(self, fix = False):
        """Check if `self` is valid roster push item.

        Valid item must have proper `subscription` value other and valid value
        for 'ask'.

        :Parameters:
            - `fix`: if `True` than replace invalid 'subscription' and 'ask'
              values with the defaults
        :Types:
            - `fix`: `bool`

        :Raise: `ValueError` if the item is invalid.
        """
        self._verify((None, "from", "to", "both", "remove"), fix)

    def verify_roster_set(self, fix = False, settings = None):
        """Check if `self` is valid roster set item.

        For use on server to validate incoming roster sets.

        Valid item must have proper `subscription` value other and valid value
        for 'ask'. The lengths of name and group names must fit the configured
        limits.

        :Parameters:
            - `fix`: if `True` than replace invalid 'subscription' and 'ask'
              values with right defaults
            - `settings`: settings object providing the name limits
        :Types:
            - `fix`: `bool`
            - `settings`: `XMPPSettings`

        :Raise: `BadRequestProtocolError` if the item is invalid.
        """
        # pylint: disable=R0912
        try:
            self._verify((None, "remove"), fix)
        except ValueError as err:
            raise BadRequestProtocolError(str(err))
        if self.ask:
            if fix:
                self.ask = None
            else:
                raise BadRequestProtocolError("'ask' in roster set")
        if self.approved:
            if fix:
                self.approved = False
            else:
                raise BadRequestProtocolError("'approved' in roster set")
        if settings is None:
            settings = XMPPSettings()
        name_length_limit = settings["roster_name_length_limit"]
        if self.name and len(self.name) > name_length_limit:
            raise NotAcceptableProtocolError("Roster item name too long")
        group_length_limit = settings["roster_group_name_length_limit"]
        for group in self.groups:
            if not group:
                raise NotAcceptableProtocolError("Roster group name empty")
            if len(group) > group_length_limit:
                raise NotAcceptableProtocolError("Roster group name too long")
        if self._duplicate_group:
            raise BadRequestProtocolError("Item group duplicated")

    def __repr__(self):
        return "<RosterItem {0!r}>".format(str(self.jid))

@payload_element_name(QUERY_TAG)
class RosterPayload(StanzaPayload, Sequence):
    """<query/> element carried via a roster Iq stanza.
    
    Can contain a single item or whole roster with optional version 
    information.

    len(), "in" and [] work like for a sequence of roster items.

    :Ivariables:
        - `version`: the version attribute
        - `_items`: roster item list
    :Types:
        - `_items`: `list` of `RosterItem`
    """
    def __init__(self, items = None, version = None):
        """
        :Parameters:
            - `items`: sequence of roster items
            - `version`: optional roster version string
        :Types:
            - `items`: iterable
            - `version`: `str`
        """
        if items is not None:
            self._items = list(items)
        else:
            self._items = []
        self.version = version

    @classmethod
    def from_xml(cls, element):
        """
        Create a `RosterPayload` object from an XML element.

        :Parameters:
            - `element`: the XML element
        :Types:
            - `element`: :etree:`ElementTree.Element`
        
        :return: a freshly created roster payload
        :returntype: `cls`
        """
        # pylint: disable-msg=W0221
        items = []
        jids = set()
        if element.tag != QUERY_TAG:
            raise ValueError("{0!r} is not a roster item".format(element))
        version = element.get("ver")
        for child in element:
            if child.tag != ITEM_TAG:
                logger.debug("Unknown element in roster: {0!r}".format(child))
                continue
            item = RosterItem.from_xml(child)
            if item.jid in jids:
                logger.warning("Duplicate jid in roster: {0!r}".format(
                                                                    item.jid))
                continue
            jids.add(item.jid)
            items.append(item)
        return cls(items, version)

    def as_xml(self):
        """Return the XML representation of roster payload.

        Makes a <query/> element with <item/> children.
        """
        element = ElementTree.Element(QUERY_TAG)
        if self.version is not None:
            element.set("ver", self.version)
        for item in self._items:
            item.as_xml(element)
        return element
    
    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)
    
    def __getitem__(self, index):
        return self._items[index]

    def __eq__(self, other):
        # pylint: disable=W0212
        if not isinstance(other, RosterPayload):
            return False
        return set(self._items) == set(other._items)

    def __ne__(self, other):
        return not self.__eq__(other)

    def items(self):
        """Return the roster items.
        
        :Returntype: iterable of `RosterType`
        """
        return self._items

class Roster(RosterPayload, Mapping):
    """Represents the XMPP roster (contact list).

    Works like an ordered JID->RosterItem dictionary with a few exceptions:
        
        - the `items()` method returns roster items (values), not JIDs (keys)
        - for [] or get() a JID or a numeric index can be used

    Please note that changes to this object do not automatically affect
    any remote copy of the roster.

    :Ivariables:
        - `_jids`: jid -> item index dictionary
    :Types:
        - `_jids`: `dict` of `JID` -> `int`
    """
    def __init__(self, items = None, version = None):
        if items:
            for item in items:
                if item.subscription == "remove":
                    raise ValueError("Roster item subscription cannot be"
                                                                " 'remove'")
        RosterPayload.__init__(self, items, version)
        self._jids = dict((item.jid, i) for i, item in enumerate(self._items))
        if len(self._items) != len(self._jids):
            raise ValueError("Duplicate JIDs")

    @classmethod
    def from_xml(cls, element):
        try:
            return super(Roster, cls).from_xml(element)
        except ValueError as err:
            raise BadRequestProtocolError(str(err))

    def __contains__(self, value):
        if isinstance(value, JID):
            return value in self._jids
        else:
            return RosterPayload.__contains__(self, value)

    def __getitem__(self, key):
        if isinstance(key, int):
            return RosterPayload.__getitem__(self, key)
        elif isinstance(key, JID):
            jid = self._jids[key]
            return self._items[jid]
        else:
            raise TypeError("Roster items may be indexed by int or JID only")

    def keys(self):
        """Return the JIDs in the roster.
        
        :Returntype: iterable of `JID`
        """
        return list(self._jids.keys())

    def values(self):
        """Return the roster items.
        
        :Returntype: iterable of `RosterType`
        """
        return self._items

    items = values

    @property
    def groups(self):
        """Set of groups defined in the roster.

        :Return: the groups
        :ReturnType: `set` of `str`
        """
        groups = set()
        for item in self._items:
            groups |= item.groups
        return groups

    def get_items_by_name(self, name, case_sensitive = True):
        """
        Return a list of items with given name.

        :Parameters:
            - `name`: name to look-up
            - `case_sensitive`: if `False` the matching will be case
              insensitive.
        :Types:
            - `name`: `str`
            - `case_sensitive`: `bool`

        :Returntype: `list` of `RosterItem`
        """
        if not case_sensitive and name:
            name = name.lower()
        result = []
        for item in self._items:
            if item.name == name:
                result.append(item)
            elif item.name is None:
                continue
            elif not case_sensitive and item.name.lower() == name:
                result.append(item)
        return result

    def get_items_by_group(self, group, case_sensitive = True):
        """
        Return a list of items within a given group.

        :Parameters:
            - `name`: name to look-up
            - `case_sensitive`: if `False` the matching will be case
              insensitive.
        :Types:
            - `name`: `str`
            - `case_sensitive`: `bool`
        
        :Returntype: `list` of `RosterItem`
        """
        result = []
        if not group:
            for item in self._items:
                if not item.groups:
                    result.append(item)
            return result
        if not case_sensitive:
            group = group.lower()
        for item in self._items:
            if group in item.groups:
                result.append(item)
            elif not case_sensitive and group in [g.lower() for g 
                                                            in item.groups]:
                result.append(item)
        return result

    def add_item(self, item, replace = False):
        """
        Add an item to the roster.

        This will not automatically update the roster on the server.

        :Parameters:
            - `item`: the item to add
            - `replace`: if `True` then existing item will be replaced,
              otherwise a `ValueError` will be raised on conflict
        :Types:
            - `item`: `RosterItem`
            - `replace`: `bool`
        """
        if item.jid in self._jids:
            if replace:
                self.remove_item(item.jid)
            else:
                raise ValueError("JID already in the roster")
        index = len(self._items)
        self._items.append(item)
        self._jids[item.jid] = index

    def remove_item(self, jid):
        """Remove item from the roster.

        :Parameters:
            - `jid`: JID of the item to remove
        :Types:
            - `jid`: `JID`
        """
        if jid not in self._jids:
            raise KeyError(jid)
        index = self._jids.pop(jid)
        del self._items[index]

class RosterClient(XMPPFeatureHandler, EventHandler):
    """Client side implementation of the roster management (:RFC:`6121`,
    section 2.)

    :Parameters:
        - `settings`: roster client settings
        - `roster`: the roster
        - `server`: roster server JID (usually the domain part of user JID)
        - `server_features`: set of features supported by the server. May
          contain ``"versioning"`` and ``"pre-approvals"``
        - `_event_queue`: the event queue
    :Types:
        - `settings`: `XMPPSettings`
        - `roster`: `Roster`
        - `server`: `JID`
        - `server_features`: `set` of `str`
        - `_event_queue`: :std:`Queue.Queue`
    """
    def __init__(self, settings = None):
        self.settings = settings if settings else XMPPSettings()
        self.roster = None
        self.server = None
        self._event_queue = self.settings["event_queue"]
        self.server_features = set()

    def load_roster(self, source):
        """Load roster from an XML file.

        Can be used before the connection is started to load saved
        roster copy, for efficient retrieval of versioned roster.

        :Parameters:
            - `source`: file name or a file object
        :Types:
            - `source`: `str` or file-like object
        """
        try:
            tree = ElementTree.parse(source)
        except ElementTree.ParseError as err:
            raise ValueError("Invalid roster format: {0}".format(err))
        roster = Roster.from_xml(tree.getroot())
        for item in roster:
            item.verify_roster_result(True)
        self.roster = roster

    def save_roster(self, dest, pretty = True):
        """Save the roster to an XML file.

        Can be used to save the last know roster copy for faster loading
        of a verisoned roster (if server supports that).

        :Parameters:
            - `dest`: file name or a file object
            - `pretty`: pretty-format the roster XML
        :Types:
            - `dest`: `str` or file-like object
            - `pretty`: `bool`
        """
        if self.roster is None:
            raise ValueError("No roster")
        element = self.roster.as_xml()
        if pretty:
            if len(element):
                element.text = '\n  '
            p_child = None
            for child in element:
                if p_child is not None:
                    p_child.tail = '\n  '
                if len(child):
                    child.text = '\n    '
                p_grand = None
                for grand in child:
                    if p_grand is not None:
                        p_grand.tail = '\n    '
                    p_grand = grand
                if p_grand is not None:
                    p_grand.tail = '\n  '
                p_child = child
            if p_child is not None:
                p_child.tail = "\n"
        tree = ElementTree.ElementTree(element)
        tree.write(dest, "utf-8")

    @event_handler(GotFeaturesEvent)
    def handle_got_features_event(self, event):
        """Check for roster related features in the stream features received
        and set `server_features` accordingly.
        """
        server_features = set()
        logger.debug("Checking roster-related features")
        if event.features.find(FEATURE_ROSTERVER) is not None:
            logger.debug("  Roster versioning available")
            server_features.add("versioning")
        if event.features.find(FEATURE_APPROVALS) is not None:
            logger.debug("  Subscription pre-approvals available")
            server_features.add("pre-approvals")
        self.server_features = server_features

    @event_handler(AuthorizedEvent)
    def handle_authorized_event(self, event):
        """Request roster upon login."""
        self.server = event.authorized_jid.bare()
        if "versioning" in self.server_features:
            if self.roster is not None and self.roster.version is not None:
                version = self.roster.version
            else:
                version = ""
        else:
            version = None
        self.request_roster(version)

    def request_roster(self, version = None):
        """Request roster from server.

        :Parameters:
            - `version`: if not `None` versioned roster will be requested
              for given local version. Use "" to request full roster.
        :Types:
            - `version`: `str`
        """
        processor = self.stanza_processor
        request = Iq(stanza_type = "get")
        request.set_payload(RosterPayload(version = version))
        processor.set_response_handlers(request, 
                                    self._get_success, self._get_error)
        processor.send(request)

    def _get_success(self, stanza):
        """Handle successful response to the roster request.
        """
        payload = stanza.get_payload(RosterPayload)
        if payload is None:
            if "versioning" in self.server_features and self.roster:
                logger.debug("Server will send roster delta in pushes")
            else:
                logger.warning("Bad roster response (no payload)")
                self._event_queue.put(RosterNotReceivedEvent(self, stanza))
                return
        else:
            items = list(payload)
            for item in items:
                item.verify_roster_result(True)
            self.roster = Roster(items, payload.version)
        self._event_queue.put(RosterReceivedEvent(self, self.roster))

    def _get_error(self, stanza):
        """Handle failure of the roster request.
        """
        if stanza:
            logger.debug("Roster request failed: {0}".format(
                                                stanza.error.condition_name))
        else:
            logger.debug("Roster request failed: timeout")
        self._event_queue.put(RosterNotReceivedEvent(self, stanza))

    @iq_set_stanza_handler(RosterPayload)
    def handle_roster_push(self, stanza):
        """Handle a roster push received from server.
        """
        if self.server is None and stanza.from_jid:
            logger.debug("Server address not known, cannot verify roster push"
                                " from {0}".format(stanza.from_jid))
            return stanza.make_error_response("service-unavailable")
        if self.server and stanza.from_jid and stanza.from_jid != self.server:
            logger.debug("Roster push from invalid source: {0}".format(
                                                            stanza.from_jid))
            return stanza.make_error_response("service-unavailable")
        payload = stanza.get_payload(RosterPayload)
        if len(payload) != 1:
            logger.warning("Bad roster push received ({0} items)"
                                                    .format(len(payload)))
            return stanza.make_error_response("bad-request")
        if self.roster is None:
            logger.debug("Dropping roster push - no roster here")
            return True
        item = payload[0]
        item.verify_roster_push(True)
        old_item = self.roster.get(item.jid)
        if item.subscription == "remove":
            if old_item:
                self.roster.remove_item(item.jid)
        else:
            self.roster.add_item(item, replace = True)
        self._event_queue.put(RosterUpdatedEvent(self, old_item, item))
        return stanza.make_result_response()

    def add_item(self, jid, name = None, groups = None,
                                callback = None, error_callback = None):
        """Add a contact to the roster.

        :Parameters:
            - `jid`: contact's jid
            - `name`: name for the contact
            - `groups`: sequence of group names the contact should belong to
            - `callback`: function to call when the request succeeds. It should
              accept a single argument - a `RosterItem` describing the
              requested change
            - `error_callback`: function to call when the request fails. It
              should accept a single argument - an error stanza received
              (`None` in case of timeout)
        :Types:
            - `jid`: `JID`
            - `name`: `str`
            - `groups`: sequence of `str`
        """
        # pylint: disable=R0913
        if jid in self.roster:
            raise ValueError("{0!r} already in the roster".format(jid))
        item = RosterItem(jid, name, groups)
        self._roster_set(item, callback, error_callback)

    def update_item(self, jid, name = NO_CHANGE, groups = NO_CHANGE,
                                callback = None, error_callback = None):
        """Modify a contact in the roster.

        :Parameters:
            - `jid`: contact's jid
            - `name`: a new name for the contact
            - `groups`: a sequence of group names the contact should belong to
            - `callback`: function to call when the request succeeds. It should
              accept a single argument - a `RosterItem` describing the
              requested change
            - `error_callback`: function to call when the request fails. It
              should accept a single argument - an error stanza received
              (`None` in case of timeout)
        :Types:
            - `jid`: `JID`
            - `name`: `str`
            - `groups`: sequence of `str`
        """
        # pylint: disable=R0913
        item = self.roster[jid]
        if name is NO_CHANGE and groups is NO_CHANGE:
            return
        if name is NO_CHANGE:
            name = item.name
        if groups is NO_CHANGE:
            groups = item.groups
        item = RosterItem(jid, name, groups)
        self._roster_set(item, callback, error_callback)

    def remove_item(self, jid, callback = None, error_callback = None):
        """Remove a contact from the roster.

        :Parameters:
            - `jid`: contact's jid
            - `callback`: function to call when the request succeeds. It should
              accept a single argument - a `RosterItem` describing the
              requested change
            - `error_callback`: function to call when the request fails. It
              should accept a single argument - an error stanza received
              (`None` in case of timeout)
        :Types:
            - `jid`: `JID`
        """
        item = self.roster[jid]
        if jid not in self.roster:
            raise KeyError(jid)
        item = RosterItem(jid, subscription = "remove")
        self._roster_set(item, callback, error_callback)

    def _roster_set(self, item, callback, error_callback):
        """Send a 'roster set' to the server.

        :Parameters:
            - `item`: the requested change
        :Types:
            - `item`: `RosterItem`
        """
        stanza = Iq(to_jid = self.server, stanza_type = "set")
        payload = RosterPayload([item])
        stanza.set_payload(payload)
        def success_cb(result_stanza):
            """Success callback for roster set."""
            if callback:
                callback(item)
        def error_cb(error_stanza):
            """Error callback for roster set."""
            if error_callback:
                error_callback(error_stanza)
            else:
                logger.error("Roster change of '{0}' failed".format(item.jid))
        processor = self.stanza_processor
        processor.set_response_handlers(stanza, 
                                    success_cb, error_cb)
        processor.send(stanza)

XMPPSettings.add_setting("roster_name_length_limit", type = int,
        default = 1023,
        doc = """Maximum length of roster item name."""
    )
XMPPSettings.add_setting("roster_group_name_length_limit", type = int,
        default = 1023,
        doc = """Maximum length of roster group name."""
    )
