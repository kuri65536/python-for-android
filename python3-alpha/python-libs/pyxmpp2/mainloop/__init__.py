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

"""PyXMPP main event loop - the event and I/O framework, aka re-inventing the
wheel."""



__docformat__ = "restructuredtext en"

import select
from ..settings import XMPPSettings

XMPPSettings.add_setting("poll_interval", type = float, default = 1.0,
        validator = XMPPSettings.validate_positive_float,
        cmdline_help = "Polling interval",
        doc = """Maximum time to wait for an event. Smaller value may increase
response times, by the cost of higher CPU usage."""
    )

if hasattr(select, "poll"):
    # pylint: disable=W0404
    from .poll import PollMainLoop as main_loop_factory
else:
    # pylint: disable=W0404
    from .select import SelectMainLoop as main_loop_factory
