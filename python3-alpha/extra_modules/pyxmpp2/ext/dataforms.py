#
# (C) Copyright 2005-2010 Jacek Konieczny <jajcus@jajcus.net>
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
"""Jabber Data Forms support.

Normative reference:
  - `JEP 4 <http://www.jabber.org/jeps/jep-0004.html>`__
"""



raise ImportError("{0} is not yet rewritten for PyXMPP2".format(__name__))

__docformat__="restructuredtext en"

import copy
import libxml2
import warnings
from ..objects import StanzaPayloadObject
from ..utils import from_utf8, to_utf8
from ..xmlextra import xml_element_ns_iter
from ..jid import JID
from ..exceptions import BadRequestProtocolError

DATAFORM_NS = "jabber:x:data"

class Option(StanzaPayloadObject):
    """One of optional data form field values.

    :Ivariables:
        - `label`: option label.
        - `value`: option value.
    :Types:
        - `label`: `str`
        - `value`: `str`
    """
    xml_element_name = "option"
    xml_element_namespace = DATAFORM_NS

    def __init__(self, value = None, label = None, values = None):
        """Initialize an `Option` object.

        :Parameters:
            - `value`: option value (mandatory).
            - `label`: option label (human-readable description).
            - `values`: for backward compatibility only.
        :Types:
            - `label`: `str`
            - `value`: `str`
        """
        self.label = label

        if value:
            self.value = value
        elif values:
            warnings.warn("Option constructor accepts only single value now.", DeprecationWarning, stacklevel=1)
            self.value = values[0]
        else:
            raise TypeError("value argument to pyxmpp.dataforms.Option is required")


    @property
    def values(self):
        """Return list of option values (always single element). Obsolete. For
        backwards compatibility only."""
        return [self.value]

    def complete_xml_element(self, xmlnode, doc):
        """Complete the XML node with `self` content.

        :Parameters:
            - `xmlnode`: XML node with the element being built. It has already
              right name and namespace, but no attributes or content.
            - `doc`: document to which the element belongs.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`
            - `doc`: `libxml2.xmlDoc`"""
        _unused = doc
        if self.label is not None:
            xmlnode.setProp("label", self.label.encode("utf-8"))
        xmlnode.newTextChild(xmlnode.ns(), "value", self.value.encode("utf-8"))
        return xmlnode

    @classmethod
    def _new_from_xml(cls, xmlnode):
        """Create a new `Option` object from an XML element.

        :Parameters:
            - `xmlnode`: the XML element.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`

        :return: the object created.
        :returntype: `Option`
        """
        label = from_utf8(xmlnode.prop("label"))
        child = xmlnode.children
        value = None
        for child in xml_element_ns_iter(xmlnode.children, DATAFORM_NS):
            if child.name == "value":
                value = from_utf8(child.getContent())
                break
        if value is None:
            raise BadRequestProtocolError("No value in <option/> element")
        return cls(value, label)

class Field(StanzaPayloadObject):
    """A data form field.

    :Ivariables:
        - `name`: field name.
        - `values`: field values.
        - `value`: field value parsed according to the form type.
        - `label`: field label (human-readable description).
        - `type`: field type ("boolean", "fixed", "hidden", "jid-multi",
          "jid-single", "list-multi", "list-single", "text-multi",
          "text-private" or "text-single").
        - `options`: field options (for "list-multi" or "list-single" fields).
        - `required`: `True` when the field is required.
        - `desc`: natural-language description of the field.
    :Types:
        - `name`: `str`
        - `values`: `list` of `str`
        - `value`: `bool` for "boolean" field, `JID` for "jid-single", `list` of `JID`
          for "jid-multi", `list` of `str` for "list-multi" and "text-multi"
          and `str` for other field types.
        - `label`: `str`
        - `type`: `str`
        - `options`: `Option`
        - `required`: `boolean`
        - `desc`: `str`
    """
    xml_element_name = "field"
    xml_element_namespace = DATAFORM_NS
    allowed_types = ("boolean", "fixed", "hidden", "jid-multi",
                "jid-single", "list-multi", "list-single", "text-multi",
                "text-private", "text-single")
    def __init__(self, name = None, values = None, field_type = None, label = None,
            options = None, required = False, desc = None, value = None):
        """Initialize a `Field` object.

        :Parameters:
            - `name`: field name.
            - `values`: raw field values. Not to be used together with `value`.
            - `field_type`: field type.
            - `label`: field label.
            - `options`: optional values for the field.
            - `required`: `True` if the field is required.
            - `desc`: natural-language description of the field.
            - `value`: field value or values in a field_type-specific type. May be used only
              if `values` parameter is not provided.
        :Types:
            - `name`: `str`
            - `values`: `list` of `str`
            - `field_type`: `str`
            - `label`: `str`
            - `options`: `list` of `Option`
            - `required`: `bool`
            - `desc`: `str`
            - `value`: `bool` for "boolean" field, `JID` for "jid-single", `list` of `JID`
              for "jid-multi", `list` of `str` for "list-multi" and "text-multi"
              and `str` for other field types.
        """
        self.name = name
        if field_type is not None and field_type not in self.allowed_types:
            raise ValueError("Invalid form field type: %r" % (field_type,))
        self.type = field_type
        if value is not None:
            if values:
                raise ValueError("values or value must be given, not both")
            self.value = value
        elif not values:
            self.values = []
        else:
            self.values = list(values)
        if field_type and not field_type.endswith("-multi") and len(self.values) > 1:
            raise ValueError("Multiple values for a single-value field")
        self.label = label
        if not options:
            self.options = []
        elif field_type and not field_type.startswith("list-"):
            raise ValueError("Options not allowed for non-list fields")
        else:
            self.options = list(options)
        self.required = required
        self.desc = desc

    def __getattr__(self, name):
        if name != "value":
            raise AttributeError("'Field' object has no attribute %r" % (name,))
        values = self.values
        t = self.type
        l = len(values)
        if t is not None:
            if t == "boolean":
                if l == 0:
                    return None
                elif l == 1:
                    v = values[0]
                    if v in ("0","false"):
                        return False
                    elif v in ("1","true"):
                        return True
                raise ValueError("Bad boolean value")
            elif t.startswith("jid-"):
                values = [JID(v) for v in values]
            if t.endswith("-multi"):
                return values
        if l == 0:
            return None
        elif l == 1:
            return values[0]
        else:
            raise ValueError("Multiple values of a single-value field")

    def __setattr__(self, name, value):
        if name != "value":
            self.__dict__[name] = value
            return
        if value is None:
            self.values = []
            return
        t = self.type
        if t == "boolean":
            if value:
                self.values = ["1"]
            else:
                self.values = ["0"]
            return
        if t and t.endswith("-multi"):
            values = list(value)
        else:
            values = [value]
        if t and t.startswith("jid-"):
            values = [JID(v).as_unicode() for v in values]
        self.values = values

    def add_option(self, value, label):
        """Add an option for the field.

        :Parameters:
            - `value`: option values.
            - `label`: option label (human-readable description).
        :Types:
            - `value`: `list` of `str`
            - `label`: `str`
        """
        if type(value) is list:
            warnings.warn(".add_option() accepts single value now.", DeprecationWarning, stacklevel=1)
            value = value[0]
        if self.type not in ("list-multi", "list-single"):
            raise ValueError("Options are allowed only for list types.")
        option = Option(value, label)
        self.options.append(option)
        return option

    def complete_xml_element(self, xmlnode, doc):
        """Complete the XML node with `self` content.

        :Parameters:
            - `xmlnode`: XML node with the element being built. It has already
              right name and namespace, but no attributes or content.
            - `doc`: document to which the element belongs.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`
            - `doc`: `libxml2.xmlDoc`"""
        if self.type is not None and self.type not in self.allowed_types:
            raise ValueError("Invalid form field type: %r" % (self.type,))
        if self.type is not None:
            xmlnode.setProp("type", self.type)
        if not self.label is None:
            xmlnode.setProp("label", to_utf8(self.label))
        if not self.name is None:
            xmlnode.setProp("var", to_utf8(self.name))
        if self.values:
            if self.type and len(self.values) > 1 and not self.type.endswith("-multi"):
                raise ValueError("Multiple values not allowed for %r field" % (self.type,))
            for value in self.values:
                xmlnode.newTextChild(xmlnode.ns(), "value", to_utf8(value))
        for option in self.options:
            option.as_xml(xmlnode, doc)
        if self.required:
            xmlnode.newChild(xmlnode.ns(), "required", None)
        if self.desc:
            xmlnode.newTextChild(xmlnode.ns(), "desc", to_utf8(self.desc))
        return xmlnode

    @classmethod
    def _new_from_xml(cls, xmlnode):
        """Create a new `Field` object from an XML element.

        :Parameters:
            - `xmlnode`: the XML element.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`

        :return: the object created.
        :returntype: `Field`
        """
        field_type = xmlnode.prop("type")
        label = from_utf8(xmlnode.prop("label"))
        name = from_utf8(xmlnode.prop("var"))
        child = xmlnode.children
        values = []
        options = []
        required = False
        desc = None
        while child:
            if child.type != "element" or child.ns().content != DATAFORM_NS:
                pass
            elif child.name == "required":
                required = True
            elif child.name == "desc":
                desc = from_utf8(child.getContent())
            elif child.name == "value":
                values.append(from_utf8(child.getContent()))
            elif child.name == "option":
                options.append(Option._new_from_xml(child))
            child = child.__next__
        if field_type and not field_type.endswith("-multi") and len(values) > 1:
            raise BadRequestProtocolError("Multiple values for a single-value field")
        return cls(name, values, field_type, label, options, required, desc)

class Item(StanzaPayloadObject):
    """An item of multi-item form data (e.g. a search result).

    Additionally to the direct access to the contained fields via the `fields` attribute,
    `Item` object provides an iterator and mapping interface for field access. E.g.::

        for field in item:
            ...

    or::

        field = item['field_name']

    or::

        if 'field_name' in item:
            ...

    :Ivariables:
        - `fields`: the fields of the item.
    :Types:
        - `fields`: `list` of `Field`.
    """
    xml_element_name = "item"
    xml_element_namespace = DATAFORM_NS

    def __init__(self, fields = None):
        """Initialize an `Item` object.

        :Parameters:
            - `fields`: item fields.
        :Types:
            - `fields`: `list` of `Field`.
        """
        if fields is None:
            self.fields = []
        else:
            self.fields = list(fields)

    def __getitem__(self, name_or_index):
        if isinstance(name_or_index, int):
            return self.fields[name_or_index]
        for f in self.fields:
            if f.name == name_or_index:
                return f
        raise KeyError(name_or_index)

    def __contains__(self, name):
        for f in self.fields:
            if f.name == name:
                return True
        return False

    def __iter__(self):
        for field in self.fields:
            yield field

    def add_field(self, name = None, values = None, field_type = None,
            label = None, options = None, required = False, desc = None, value = None):
        """Add a field to the item.

        :Parameters:
            - `name`: field name.
            - `values`: raw field values. Not to be used together with `value`.
            - `field_type`: field type.
            - `label`: field label.
            - `options`: optional values for the field.
            - `required`: `True` if the field is required.
            - `desc`: natural-language description of the field.
            - `value`: field value or values in a field_type-specific type. May be used only
              if `values` parameter is not provided.
        :Types:
            - `name`: `str`
            - `values`: `list` of `str`
            - `field_type`: `str`
            - `label`: `str`
            - `options`: `list` of `Option`
            - `required`: `bool`
            - `desc`: `str`
            - `value`: `bool` for "boolean" field, `JID` for "jid-single", `list` of `JID`
              for "jid-multi", `list` of `str` for "list-multi" and "text-multi"
              and `str` for other field types.

        :return: the field added.
        :returntype: `Field`
        """
        field = Field(name, values, field_type, label, options, required, desc, value)
        self.fields.append(field)
        return field

    def complete_xml_element(self, xmlnode, doc):
        """Complete the XML node with `self` content.

        :Parameters:
            - `xmlnode`: XML node with the element being built. It has already
              right name and namespace, but no attributes or content.
            - `doc`: document to which the element belongs.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`
            - `doc`: `libxml2.xmlDoc`"""
        for field in self.fields:
            field.as_xml(xmlnode, doc)

    @classmethod
    def _new_from_xml(cls, xmlnode):
        """Create a new `Item` object from an XML element.

        :Parameters:
            - `xmlnode`: the XML element.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`

        :return: the object created.
        :returntype: `Item`
        """
        child = xmlnode.children
        fields = []
        while child:
            if child.type != "element" or child.ns().content != DATAFORM_NS:
                pass
            elif child.name == "field":
                fields.append(Field._new_from_xml(child))
            child = child.__next__
        return cls(fields)

class Form(StanzaPayloadObject):
    """A JEP-0004 compliant data form.

    Additionally to the direct access to the contained fields via the `fields` attribute,
    `Form` object provides an iterator and mapping interface for field access. E.g.::

        for field in form:
            ...

    or::

        field = form['field_name']

    :Ivariables:
        - `type`: form type ("form", "submit", "cancel" or "result").
        - `title`: form title.
        - `instructions`: instructions for a form user.
        - `fields`: the fields in the form.
        - `reported_fields`: list of fields returned in a multi-item data form.
        - `items`: items in a multi-item data form.
    :Types:
        - `title`: `str`
        - `instructions`: `str`
        - `fields`: `list` of `Field`
        - `reported_fields`: `list` of `Field`
        - `items`: `list` of `Item`
    """
    allowed_types = ("form", "submit", "cancel", "result")
    xml_element_name = "x"
    xml_element_namespace = DATAFORM_NS

    def __init__(self, xmlnode_or_type = "form", title = None, instructions = None,
            fields = None, reported_fields = None, items = None):
        """Initialize a `Form` object.

        :Parameters:
            - `xmlnode_or_type`: XML element to parse or a form title.
            - `title`: form title.
            - `instructions`: instructions for the form.
            - `fields`: form fields.
            - `reported_fields`: fields reported in multi-item data.
            - `items`: items of multi-item data.
        :Types:
            - `xmlnode_or_type`: `libxml2.xmlNode` or `str`
            - `title`: `str`
            - `instructions`: `str`
            - `fields`: `list` of `Field`
            - `reported_fields`: `list` of `Field`
            - `items`: `list` of `Item`
        """
        if isinstance(xmlnode_or_type, libxml2.xmlNode):
            self.__from_xml(xmlnode_or_type)
        elif xmlnode_or_type not in self.allowed_types:
            raise ValueError("Form type %r not allowed." % (xmlnode_or_type,))
        else:
            self.type = xmlnode_or_type
            self.title = title
            self.instructions = instructions
            if fields:
                self.fields = list(fields)
            else:
                self.fields = []
            if reported_fields:
                self.reported_fields = list(reported_fields)
            else:
                self.reported_fields = []
            if items:
                self.items = list(items)
            else:
                self.items = []

    def __getitem__(self, name_or_index):
        if isinstance(name_or_index, int):
            return self.fields[name_or_index]
        for f in self.fields:
            if f.name == name_or_index:
                return f
        raise KeyError(name_or_index)

    def __contains__(self, name):
        for f in self.fields:
            if f.name == name:
                return True
        return False

    def __iter__(self):
        for field in self.fields:
            yield field

    def add_field(self, name = None, values = None, field_type = None,
            label = None, options = None, required = False, desc = None, value = None):
        """Add a field to the form.

        :Parameters:
            - `name`: field name.
            - `values`: raw field values. Not to be used together with `value`.
            - `field_type`: field type.
            - `label`: field label.
            - `options`: optional values for the field.
            - `required`: `True` if the field is required.
            - `desc`: natural-language description of the field.
            - `value`: field value or values in a field_type-specific type. May be used only
              if `values` parameter is not provided.
        :Types:
            - `name`: `str`
            - `values`: `list` of `str`
            - `field_type`: `str`
            - `label`: `str`
            - `options`: `list` of `Option`
            - `required`: `bool`
            - `desc`: `str`
            - `value`: `bool` for "boolean" field, `JID` for "jid-single", `list` of `JID`
              for "jid-multi", `list` of `str` for "list-multi" and "text-multi"
              and `str` for other field types.

        :return: the field added.
        :returntype: `Field`
        """
        field = Field(name, values, field_type, label, options, required, desc, value)
        self.fields.append(field)
        return field

    def add_item(self, fields = None):
        """Add and item to the form.

        :Parameters:
            - `fields`: fields of the item (they may be added later).
        :Types:
            - `fields`: `list` of `Field`

        :return: the item added.
        :returntype: `Item`
        """
        item = Item(fields)
        self.items.append(item)
        return item

    def make_submit(self, keep_types = False):
        """Make a "submit" form using data in `self`.

        Remove uneeded information from the form. The information removed
        includes: title, instructions, field labels, fixed fields etc.

        :raise ValueError: when any required field has no value.

        :Parameters:
            - `keep_types`: when `True` field type information will be included
              in the result form. That is usually not needed.
        :Types:
            - `keep_types`: `bool`

        :return: the form created.
        :returntype: `Form`"""
        result = Form("submit")
        for field in self.fields:
            if field.type == "fixed":
                continue
            if not field.values:
                if field.required:
                    raise ValueError("Required field with no value!")
                continue
            if keep_types:
                result.add_field(field.name, field.values, field.type)
            else:
                result.add_field(field.name, field.values)
        return result

    def copy(self):
        """Get a deep copy of `self`.

        :return: a deep copy of `self`.
        :returntype: `Form`"""
        return copy.deepcopy(self)

    def complete_xml_element(self, xmlnode, doc):
        """Complete the XML node with `self` content.

        :Parameters:
            - `xmlnode`: XML node with the element being built. It has already
              right name and namespace, but no attributes or content.
            - `doc`: document to which the element belongs.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`
            - `doc`: `libxml2.xmlDoc`"""
        if self.type not in self.allowed_types:
            raise ValueError("Form type %r not allowed." % (self.type,))
        xmlnode.setProp("type", self.type)
        if self.type == "cancel":
            return
        ns = xmlnode.ns()
        if self.title is not None:
            xmlnode.newTextChild(ns, "title", to_utf8(self.title))
        if self.instructions is not None:
            xmlnode.newTextChild(ns, "instructions", to_utf8(self.instructions))
        for field in self.fields:
            field.as_xml(xmlnode, doc)
        if self.type != "result":
            return
        if self.reported_fields:
            reported = xmlnode.newChild(ns, "reported", None)
            for field in self.reported_fields:
                field.as_xml(reported, doc)
        for item in self.items:
            item.as_xml(xmlnode, doc)

    def __from_xml(self, xmlnode):
        """Initialize a `Form` object from an XML element.

        :Parameters:
            - `xmlnode`: the XML element.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`
        """
        self.fields = []
        self.reported_fields = []
        self.items = []
        self.title = None
        self.instructions = None
        if (xmlnode.type != "element" or xmlnode.name != "x"
                or xmlnode.ns().content != DATAFORM_NS):
            raise ValueError("Not a form: " + xmlnode.serialize()) 
        self.type = xmlnode.prop("type")
        if not self.type in self.allowed_types:
            raise BadRequestProtocolError("Bad form type: %r" % (self.type,))
        child = xmlnode.children
        while child:
            if child.type != "element" or child.ns().content != DATAFORM_NS:
                pass
            elif child.name == "title":
                self.title = from_utf8(child.getContent())
            elif child.name == "instructions":
                self.instructions = from_utf8(child.getContent())
            elif child.name == "field":
                self.fields.append(Field._new_from_xml(child))
            elif child.name == "item":
                self.items.append(Item._new_from_xml(child))
            elif child.name == "reported":
                self.__get_reported(child)
            child = child.__next__

    def __get_reported(self, xmlnode):
        """Parse the <reported/> element of the form.

        :Parameters:
            - `xmlnode`: the element to parse.
        :Types:
            - `xmlnode`: `libxml2.xmlNode`"""
        child = xmlnode.children
        while child:
            if child.type != "element" or child.ns().content != DATAFORM_NS:
                pass
            elif child.name == "field":
                self.reported_fields.append(Field._new_from_xml(child))
            child = child.__next__
# vi: sts=4 et sw=4
