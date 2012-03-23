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

"""DNS resolever with SRV record support.

Normative reference:
  - `RFC 1035 <http://www.ietf.org/rfc/rfc1035.txt>`__
  - `RFC 2782 <http://www.ietf.org/rfc/rfc2782.txt>`__
"""



__docformat__ = "restructuredtext en"

import socket
import random
import logging
import threading
import queue

from .settings import XMPPSettings
from .interfaces import Resolver

logger = logging.getLogger("pyxmpp2.resolver")

try:
    import dns.resolver     # pylint: disable=W0404
    import dns.name         # pylint: disable=W0404
    import dns.exception    # pylint: disable=W0404

    HAVE_DNSPYTHON = True
except ImportError:
    HAVE_DNSPYTHON = False

def is_ipv6_available():
    """Check if IPv6 is available.
    
    :Return: `True` when an IPv6 socket can be created.
    """
    try:
        socket.socket(socket.AF_INET6)
    except (socket.error, AttributeError):
        return False
    return True

def is_ipv4_available():
    """Check if IPv4 is available.
    
    :Return: `True` when an IPv4 socket can be created.
    """
    try:
        socket.socket(socket.AF_INET)
    except socket.error:
        return False
    return True

def shuffle_srv(records):
    """Randomly reorder SRV records using their weights.

    :Parameters:
        - `records`: SRV records to shuffle.
    :Types:
        - `records`: sequence of :dns:`dns.rdtypes.IN.SRV`

    :return: reordered records.
    :returntype: `list` of :dns:`dns.rdtypes.IN.SRV`"""
    if not records:
        return []
    ret = []
    while len(records) > 1:
        weight_sum = 0
        for rrecord in records:
            weight_sum += rrecord.weight + 0.1
        thres = random.random() * weight_sum
        weight_sum = 0
        for rrecord in records:
            weight_sum += rrecord.weight + 0.1
            if thres < weight_sum:
                records.remove(rrecord)
                ret.append(rrecord)
                break
    ret.append(records[0])
    return ret

def reorder_srv(records):
    """Reorder SRV records using their priorities and weights.

    :Parameters:
        - `records`: SRV records to shuffle.
    :Types:
        - `records`: `list` of :dns:`dns.rdtypes.IN.SRV`

    :return: reordered records.
    :returntype: `list` of :dns:`dns.rdtypes.IN.SRV`"""
    records = list(records)
    records.sort()
    ret = []
    tmp = []
    for rrecord in records:
        if not tmp or rrecord.priority == tmp[0].priority:
            tmp.append(rrecord)
            continue
        ret += shuffle_srv(tmp)
        tmp = [rrecord]
    if tmp:
        ret += shuffle_srv(tmp)
    return ret

class ThreadedResolverBase(Resolver):
    """Base class for threaded resolvers.

    Starts worker threads, each running a blocking resolver implementation
    and communicates with them to provide non-blocking asynchronous API.
    """
    def __init__(self, settings =  None, max_threads = 1):
        if settings:
            self.settings = settings
        else:
            self.settings = XMPPSettings()
        self.threads = []
        self.queue = queue.Queue()
        self.lock = threading.RLock()
        self.max_threads = max_threads
        self.last_thread_n = 0
        
    def _make_resolver(self):
        """Return the blocking resolver implementation that should be
        used by the resolver threads.
        """
        raise NotImplementedError

    def stop(self):
        """Stop the resolver threads.
        """
        with self.lock:
            for dummy in self.threads:
                self.queue.put(None)
        
    def _start_thread(self):
        """Start a new working thread unless the maximum number of threads
        has been reached or the request queue is empty.
        """
        with self.lock:
            if self.threads and self.queue.empty():
                return
            if len(self.threads) >= self.max_threads:
                return
            thread_n = self.last_thread_n + 1
            self.last_thread_n = thread_n
            thread = threading.Thread(target = self._run,
                            name = "{0!r} #{1}".format(self, thread_n),
                            args = (thread_n,))
            self.threads.append(thread)
            thread.daemon = True
            thread.start()

    def resolve_address(self, hostname, callback, allow_cname = True):
        request = ("resolve_address", (hostname, callback, allow_cname))
        self._start_thread()
        self.queue.put(request)
    
    def resolve_srv(self, domain, service, protocol, callback):
        request = ("resolve_srv", (domain, service, protocol, callback))
        self._start_thread()
        self.queue.put(request)

    def _run(self, thread_n):
        """The thread function."""
        try:
            logger.debug("{0!r}: entering thread #{1}"
                                                .format(self, thread_n))
            resolver = self._make_resolver()
            while True:
                request = self.queue.get()
                if request is None:
                    break
                method, args = request
                logger.debug(" calling {0!r}.{1}{2!r}"
                                            .format(resolver, method, args))
                getattr(resolver, method)(*args) # pylint: disable=W0142
                self.queue.task_done()
            logger.debug("{0!r}: leaving thread #{1}"
                                                .format(self, thread_n))
        finally:
            self.threads.remove(threading.currentThread())

class DumbBlockingResolver(Resolver):
    """Simple blocking resolver using only the standard Python library.
    
    This doesn't support SRV lookups!

    `resolve_srv` will raise NotImplementedError
    `resolve_address` will block until the lookup completes or fail and then
    call the callback immediately.
    """
    # pylint: disable-msg=R0921
    def __init__(self, settings = None):
        if settings:
            self.settings = settings
        else:
            self.settings = XMPPSettings()

    def resolve_srv(self, domain, service, protocol, callback):
        raise NotImplementedError("The DumbBlockingResolver cannot resolve"
                " SRV records. DNSPython or target hostname explicitely set"
                                                                " required")

    def resolve_address(self, hostname, callback, allow_cname = True):
        """Start looking up an A or AAAA record.

        `callback` will be called with a list of (family, address) tuples
        on success. Family is :std:`socket.AF_INET` or :std:`socket.AF_INET6`,
        the address is IPv4 or IPv6 literal. The list will be empty on error.

        :Parameters:
            - `hostname`: the host name to look up
            - `callback`: a function to be called with a list of received
              addresses
            - `allow_cname`: `True` if CNAMEs should be followed
        :Types:
            - `hostname`: `str`
            - `callback`: function accepting a single argument
            - `allow_cname`: `bool`
        """
        if self.settings["ipv6"]:
            if self.settings["ipv4"]:
                family = socket.AF_UNSPEC
            else:
                family = socket.AF_INET6
        elif self.settings["ipv4"]:
            family = socket.AF_INET
        else:
            logger.warning("Neither IPv6 or IPv4 allowed.")
            callback([])
            return
        try:
            ret = socket.getaddrinfo(hostname, 0, family, socket.SOCK_STREAM, 0)
        except socket.gaierror as err:
            logger.warning("Couldn't resolve {0!r}: {1}".format(hostname,
                                                                        err))
            callback([])
            return
        if family == socket.AF_UNSPEC:
            tmp = ret
            if self.settings["prefer_ipv6"]:
                ret = [ addr for addr in tmp if addr[0] == socket.AF_INET6 ]
                ret += [ addr for addr in tmp if addr[0] == socket.AF_INET ]
            else:
                ret = [ addr for addr in tmp if addr[0] == socket.AF_INET ]
                ret += [ addr for addr in tmp if addr[0] == socket.AF_INET6 ]
        callback([(addr[0], addr[4][0]) for addr in ret])


if HAVE_DNSPYTHON:
    class BlockingResolver(Resolver):
        """Blocking resolver using the DNSPython package.

        Both `resolve_srv` and `resolve_address` will block until the 
        lookup completes or fail and then call the callback immediately.
        """
        def __init__(self, settings =  None):
            if settings:
                self.settings = settings
            else:
                self.settings = XMPPSettings()
            
        def resolve_srv(self, domain, service, protocol, callback):
            """Start looking up an SRV record for `service` at `domain`.

            `callback` will be called with a properly sorted list of (hostname,
            port) pairs on success. The list will be empty on error and it will
            contain only (".", 0) when the service is explicitely disabled.

            :Parameters:
                - `domain`: domain name to look up
                - `service`: service name e.g. 'xmpp-client'
                - `protocol`: protocol name, e.g. 'tcp'
                - `callback`: a function to be called with a list of received
                  addresses
            :Types:
                - `domain`: `str`
                - `service`: `str`
                - `protocol`: `str`
                - `callback`: function accepting a single argument
            """
            if isinstance(domain, str):
                domain = domain.encode("idna").decode("us-ascii")
            domain = "_{0}._{1}.{2}".format(service, protocol, domain)
            try:
                records = dns.resolver.query(domain, 'SRV')
            except dns.exception.DNSException as err:
                logger.warning("Could not resolve {0!r}: {1}"
                                    .format(domain, err.__class__.__name__))
                callback([])
                return
            if not records:
                callback([])
                return

            result = []
            for record in reorder_srv(records):
                hostname = record.target.to_text()
                if hostname in (".", ""):
                    continue
                result.append((hostname, record.port))

            if not result:
                callback([(".", 0)])
            else:
                callback(result)
            return

        def resolve_address(self, hostname, callback, allow_cname = True):
            """Start looking up an A or AAAA record.

            `callback` will be called with a list of (family, address) tuples
            (each holiding socket.AF_*  and IPv4 or IPv6 address literal) on
            success. The list will be empty on error.

            :Parameters:
                - `hostname`: the host name to look up
                - `callback`: a function to be called with a list of received
                  addresses
                - `allow_cname`: `True` if CNAMEs should be followed
            :Types:
                - `hostname`: `str`
                - `callback`: function accepting a single argument
                - `allow_cname`: `bool`
            """
            if isinstance(hostname, str):
                hostname = hostname.encode("idna").decode("us-ascii")
            rtypes = []
            if self.settings["ipv6"]:
                rtypes.append(("AAAA", socket.AF_INET6))
            if self.settings["ipv4"]:
                rtypes.append(("A", socket.AF_INET))
            if not self.settings["prefer_ipv6"]:
                rtypes.reverse()
            exception = None
            result = []
            for rtype, rfamily in rtypes:
                try:
                    try:
                        records = dns.resolver.query(hostname, rtype)
                    except dns.exception.DNSException:
                        records = dns.resolver.query(hostname + ".", rtype)
                except dns.exception.DNSException as err:
                    exception = err
                    continue
                if not allow_cname and records.rrset.name != dns.name.from_text(
                                                                    hostname):
                    logger.warning("Unexpected CNAME record found for {0!r}"
                                                            .format(hostname))
                    continue
                if records:
                    for record in records:
                        result.append((rfamily, record.to_text()))

            if not result and exception:
                logger.warning("Could not resolve {0!r}: {1}".format(hostname,
                                                exception.__class__.__name__))
            callback(result)

    class ThreadedResolver(ThreadedResolverBase):
        """Threaded resolver implementation using the DNSPython
        :dns:`dns.resolver` module.
        """
        def _make_resolver(self):    
            return BlockingResolver(self.settings)

    _DEFAULT_RESOLVER = BlockingResolver
else:
    _DEFAULT_RESOLVER = DumbBlockingResolver

XMPPSettings.add_setting("dns_resolver", type = Resolver,
        factory = _DEFAULT_RESOLVER, 
        default_d = "A `{0}` instance".format(_DEFAULT_RESOLVER.__name__),
        doc = """The DNS resolver implementation to be used by PyXMPP."""
    )
XMPPSettings.add_setting("ipv4", type = bool, default = True,
        cmdline_help = "Allow IPv4 address lookup",
        doc = """Look up IPv4 addresses for a server host name."""
    )
XMPPSettings.add_setting("ipv6", type = bool, basic = True,
        factory = lambda x: is_ipv6_available(), cache = True,
        cmdline_help = "Allow IPv6 address lookup",
        doc = """Look up IPv6 addresses for a server host name."""
    )
XMPPSettings.add_setting("prefer_ipv6", type = bool, basic = True,
        default = True,
        cmdline_help = "Prefer IPv6",
        doc = """When enabled IPv6 and connecting to a dual-stack XMPP server
IPv6 addresses will be tried first."""
    )

# vi: sts=4 et sw=4
