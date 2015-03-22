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

"""Utility functions to wait until a socket (or object implementing .fileno()
in POSIX) is ready for input or output."""



__docformat__ = "restructuredtext en"

import select

if hasattr(select, "poll"):
    def wait_for_read(socket, timeout = None):
        """Wait up to `timeout` seconds until `socket` is ready for reading.
        """
        if timeout is not None:
            timeout *= 1000
        poll = select.poll()
        poll.register(socket, select.POLLIN)
        events = poll.poll(timeout)
        return bool(events)
    def wait_for_write(socket, timeout = None):
        """Wait up to `timeout` seconds until `socket` is ready for writing.
        """
        if timeout is not None:
            timeout *= 1000
        poll = select.poll()
        poll.register(socket, select.POLLOUT)
        events = poll.poll(timeout)
        return bool(events)
else:
    def wait_for_read(socket, timeout = None):
        """Wait up to `timeout` seconds until `socket` is ready for reading.
        """
        readable = select.select([socket], [], [], timeout)[0]
        return bool(readable)
    def wait_for_write(socket, timeout = None):
        """Wait up to `timeout` seconds until `socket` is ready for writing.
        """
        writable = select.select([], [socket], [], timeout)[1]
        return writable(writable)

