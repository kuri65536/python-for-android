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
# pylint: disable-msg=W0201

"""General settings container.

The behaviour of the XMPP implementation may be controlled by many, many
parameters, like addresses, authetication methods, TLS settings, keep alive,
etc.
Those need to be passed from one component to other and passing it directly
via function parameters would only mess up the API.

Instead an `XMPPSettings` object will be used to pass all the optional
parameters. It will also provide the defaults.

This is also a mechanism for dependency injection, allowing different
components share the same objects, like event queue or DNS resolver
implementation.
"""



__docformat__ = "restructuredtext en"

import sys
import argparse
import logging

from collections import MutableMapping

logger = logging.getLogger("pyxmpp2.settings")

class _SettingDefinition(object):
    """A PyXMPP2 setting meta-data and defaults."""
    # pylint: disable-msg=R0902,R0903
    def __init__(self, name, type = str, default = None, factory = None,
                        cache = False, default_d = None, doc = None,
                        cmdline_help = None, validator = None, basic = False):
        # pylint: disable-msg=W0622,R0913
        self.name = name
        self.type = type
        self.default = default
        self.factory = factory
        self.cache = cache
        self.default_d = default_d
        self.doc = doc
        self.cmdline_help = cmdline_help
        self.basic = basic
        self.validator = validator

class XMPPSettings(MutableMapping):
    """Container for various parameters used all over PyXMPP.
    
    It can be used like a regular dictionary, but will provide reasonable
    defaults for PyXMPP for parameters which are not explicitely set.

    All known PyXMPP settings are included in the :r:`settings list`.
    
    :CVariables:
        - `_defaults`: defaults for registered parameters.
        - `_defaults_factories`: factory functions providing default values
          which cannot be hard-coded.
    :Ivariables:
        - `_settings`: current values of the parameters explicitely set.
    """
    _defs = {}
    def __init__(self, data = None):
        """Create settings, optionally initialized with `data`.

        :Parameters:
            - `data`: initial data
        :Types:
            - `data`: any mapping, including `XMPPSettings`
        """
        if data is None:
            self._settings = {}
        else:
            self._settings = dict(data)
    def __len__(self):
        """Number of parameters set."""
        return len(self._settings)
    def __iter__(self):
        """Iterate over the parameter names."""
        for key in self._settings.keys():
            return self[key]
    def __contains__(self, key):
        """Check if a parameter is set.
        
        :Parameters:
            - `key`: the parameter name
        :Types:
            - `key`: `str`
        """
        return key in self._settings
    def __getitem__(self, key):
        """Get a parameter value. Return the default if no value is set
        and the default is provided by PyXMPP.
        
        :Parameters:
            - `key`: the parameter name
        :Types:
            - `key`: `str`
        """
        return self.get(key, required = True)
    def __setitem__(self, key, value):
        """Set a parameter value.
        
        :Parameters:
            - `key`: the parameter name
            - `value`: the new value
        :Types:
            - `key`: `str`
        """
        self._settings[str(key)] = value
    def __delitem__(self, key):
        """Unset a parameter value.
        
        :Parameters:
            - `key`: the parameter name
        :Types:
            - `key`: `str`
        """
        del self._settings[key]
    def get(self, key, local_default = None, required = False):
        """Get a parameter value.
        
        If parameter is not set, return `local_default` if it is not `None`
        or the PyXMPP global default otherwise.

        :Raise `KeyError`: if parameter has no value and no global default

        :Return: parameter value
        """
        # pylint: disable-msg=W0221
        if key in self._settings:
            return self._settings[key]
        if local_default is not None:
            return local_default
        if key in self._defs:
            setting_def = self._defs[key]
            if setting_def.default is not None:
                return setting_def.default
            factory = setting_def.factory
            if factory is None:
                return None
            value = factory(self)
            if setting_def.cache is True:
                setting_def.default = value
            return value
        if required:
            raise KeyError(key)
        return local_default
    def keys(self):
        """Return names of parameters set.
        
        :Returntype: - `list` of `str`
        """
        return list(self._settings.keys())
    def items(self):
        """Return names and values of parameters set.
        
        :Returntype: - `list` of tuples
        """
        return list(self._settings.items())

    def load_arguments(self, args):
        """Load settings from :std:`ArgumentParser` output.

        :Parameters:
            - `args`: output of argument parsed based on the one 
              returned by `get_arg_parser()`
        """
        for name, setting in list(self._defs.items()):
            if sys.version_info.major < 3:
                # pylint: disable-msg=W0404
                from locale import getpreferredencoding
                encoding = getpreferredencoding()
                name = name.encode(encoding, "replace")
            attr = "pyxmpp2_" + name
            try:
                self[setting.name] = getattr(args, attr)
            except AttributeError:
                pass

    @classmethod
    def add_setting(cls, name, type = str, default = None, factory = None,
                        cache = False, default_d = None, doc = None,
                        cmdline_help = None, validator = None, basic = False):
        """Add a new setting definition.

        :Parameters:
            - `name`: setting name
            - `type`: setting type object or type description
            - `default`: default value
            - `factory`: default value factory
            - `cache`: if `True` the `factory` will be called only once
              and its value stored as a constant default.
            - `default_d`: description of the default value
            - `doc`: setting documentation
            - `cmdline_help`: command line argument description. When not 
              provided then the setting won't be available as a command-line
              option
            - `basic`: when `True` the option is considered a basic option - 
              one of those which should usually stay configurable in
              an application.
            - `validator`: function validating command-line option value string
              and returning proper value for the settings objects. Defaults
              to `type`.
        :Types:
            - `name`: `str`
            - `type`: type or `str`
            - `factory`: a callable
            - `cache`: `bool`
            - `default_d`: `str`
            - `doc`: `str`
            - `cmdline_help`: `str`
            - `basic`: `bool`
            - `validator`: a callable
        """
        # pylint: disable-msg=W0622,R0913
        setting_def = _SettingDefinition(name, type, default, factory,
                                            cache, default_d, doc, 
                                            cmdline_help, validator, basic)
        if name not in cls._defs:
            cls._defs[name] = setting_def
            return
        duplicate = cls._defs[name]
        if duplicate.type != setting_def.type:
            raise ValueError("Setting duplicate, with a different type")
        if duplicate.default != setting_def.default:
            raise ValueError("Setting duplicate, with a different default")
        if duplicate.factory != setting_def.factory:
            raise ValueError("Setting duplicate, with a different factory")

    @staticmethod
    def validate_string_list(value):
        """Validator for string lists to be used with `add_setting`."""
        try:
            if sys.version_info.major < 3:
                # pylint: disable-msg=W0404
                from locale import getpreferredencoding
                encoding = getpreferredencoding()
                value = value.decode(encoding)
            return [x.strip() for x in value.split(",")]
        except (AttributeError, TypeError, UnicodeError):
            raise ValueError("Bad string list")
    
    @staticmethod
    def validate_positive_int(value):
        """Positive integer validator to be used with `add_setting`."""
        value = int(value)
        if value <= 0:
            raise ValueError("Positive number required")
        return value

    @staticmethod
    def validate_positive_float(value):
        """Positive float validator to be used with `add_setting`."""
        value = float(value)
        if value <= 0:
            raise ValueError("Positive number required")
        return value

    @staticmethod
    def get_int_range_validator(start, stop):
        """Return an integer range validator to be used with `add_setting`.

        :Parameters:
            - `start`: minimum value for the integer
            - `stop`: the upper bound (maximum value + 1)
        :Types:
            - `start`: `int`
            - `stop`: `int`
        
        :return: a validator function
        """
        def validate_int_range(value):
            """Integer range validator."""
            value = int(value)
            if value >= start and value < stop:
                return value
            raise ValueError("Not in <{0},{1}) range".format(start, stop))
        return validate_int_range

    @classmethod
    def list_all(cls, basic = None):
        """List known settings.

        :Parameters:
            - `basic`: When `True` then limit output to the basic settings,
              when `False` list only the extra settings.
        """
        if basic is None:
            return [s for s in cls._defs]
        else:
            return [s.name for s in list(cls._defs.values()) if s.basic == basic]

    @classmethod
    def get_arg_parser(cls, settings = None, option_prefix = '--',
                                                            add_help = False):
        """Make a command-line option parser.

        The returned parser may be used as a parent parser for application
        argument parser.

        :Parameters:
            - `settings`: list of PyXMPP2 settings to consider. By default
              all 'basic' settings are provided.
            - `option_prefix`: custom prefix for PyXMPP2 options. E.g. 
              ``'--xmpp'`` to differentiate them from not xmpp-related
              application options.
            - `add_help`: when `True` a '--help' option will be included
              (probably already added in the application parser object)
        :Types:
            - `settings`: list of `str`
            - `option_prefix`: `str`
            - `add_help`: 

        :return: an argument parser object.
        :returntype: :std:`argparse.ArgumentParser`
        """
        # pylint: disable-msg=R0914,R0912
        parser = argparse.ArgumentParser(add_help = add_help, 
                                            prefix_chars = option_prefix[0])
        if settings is None:
            settings = cls.list_all(basic = True)

        if sys.version_info.major < 3:
            # pylint: disable-msg=W0404
            from locale import getpreferredencoding
            encoding = getpreferredencoding()
            def decode_string_option(value):
                """Decode a string option."""
                return value.decode(encoding)

        for name in settings:
            if name not in cls._defs:
                logger.debug("get_arg_parser: ignoring unknown option {0}"
                                                                .format(name))
                return
            setting = cls._defs[name]
            if not setting.cmdline_help:
                logger.debug("get_arg_parser: option {0} has no cmdline"
                                                                .format(name))
                return
            if sys.version_info.major < 3:
                name = name.encode(encoding, "replace")
            option = option_prefix + name.replace("_", "-")
            dest = "pyxmpp2_" + name
            if setting.validator:
                opt_type = setting.validator
            elif setting.type is str and sys.version_info.major < 3:
                opt_type = decode_string_option
            else:
                opt_type = setting.type
            if setting.default_d:
                default_s = setting.default_d
                if sys.version_info.major < 3:
                    default_s = default_s.encode(encoding, "replace")
            elif setting.default is not None:
                default_s = repr(setting.default)
            else:
                default_s = None
            opt_help = setting.cmdline_help
            if sys.version_info.major < 3:
                opt_help = opt_help.encode(encoding, "replace")
            if default_s:
                opt_help += " (Default: {0})".format(default_s)
            if opt_type is bool:
                opt_action = _YesNoAction
            else:
                opt_action = "store"
            parser.add_argument(option,
                                action = opt_action,
                                default = setting.default,
                                type = opt_type,
                                help = opt_help,
                                metavar = name.upper(),
                                dest = dest)
        return parser

class _YesNoAction(argparse.Action):
    """Custom std:`argparse` option to handle boolean options
    via '--no-' prefixes.

    For every "--something" option a "--no-something" option will be added
    storing a `False` value (original option will store `True`).
    """
    # pylint: disable-msg=R0903
    def __init__(self, option_strings, **kwargs):
        strings = []
        self.positive_strings = set()
        for string in option_strings:
            if string[0] != string[1]:
                raise ValueError("Doubly-prefixed option expected")
            strings.append(string)
            self.positive_strings.add(string)
            neg_string = string[:2] + "no" + string[1:]
            strings.append(neg_string)
        kwargs["nargs"] = 0
        super(_YesNoAction, self).__init__(strings, **kwargs)

    def __call__(self, parser, namespace, value, option_string = None):
        if option_string in self.positive_strings:
            setattr(namespace, self.dest, True)
        else:
            setattr(namespace, self.dest, False)

