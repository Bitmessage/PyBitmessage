# -*- Mode: Python -*-
#   Id: asyncore.py,v 2.51 2000/09/07 22:29:26 rushing Exp
#   Author: Sam Rushing <rushing@nightmare.com>
# pylint: disable=too-many-statements,too-many-branches,no-self-use,too-many-lines,attribute-defined-outside-init
# pylint: disable=global-statement
"""
src/network/asyncore_pollchoose.py
==================================

# ======================================================================
# Copyright 1996 by Sam Rushing
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Sam
# Rushing not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# SAM RUSHING DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL SAM RUSHING BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ======================================================================

Basic infrastructure for asynchronous socket service clients and servers.

There are only two ways to have a program on a single processor do "more
than one thing at a time".  Multi-threaded programming is the simplest and
most popular way to do it, but there is another very different technique,
that lets you have nearly all the advantages of multi-threading, without
actually using multiple threads. it's really only practical if your program
is largely I/O bound. If your program is CPU bound, then pre-emptive
scheduled threads are probably what you really need. Network servers are
rarely CPU-bound, however.

If your operating system supports the select() system call in its I/O
library (and nearly all do), then you can use it to juggle multiple
communication channels at once; doing other work while your I/O is taking
place in the "background."  Although this strategy can seem strange and
complex, especially at first, it is in many ways easier to understand and
control than multi-threaded programming. The module documented here solves
many of the difficult problems for you, making the task of building
sophisticated high-performance network servers and clients a snap.
"""

import os
import select
import socket
import sys
import time
import warnings
from errno import (
    EADDRINUSE, EAGAIN, EALREADY, EBADF, ECONNABORTED, ECONNREFUSED, ECONNRESET, EHOSTUNREACH, EINPROGRESS, EINTR,
    EINVAL, EISCONN, ENETUNREACH, ENOTCONN, ENOTSOCK, EPIPE, ESHUTDOWN, ETIMEDOUT, EWOULDBLOCK, errorcode
)
from threading import current_thread

import helper_random

try:
    from errno import WSAEWOULDBLOCK
except (ImportError, AttributeError):
    WSAEWOULDBLOCK = EWOULDBLOCK
try:
    from errno import WSAENOTSOCK
except (ImportError, AttributeError):
    WSAENOTSOCK = ENOTSOCK
try:
    from errno import WSAECONNRESET
except (ImportError, AttributeError):
    WSAECONNRESET = ECONNRESET
try:
    # Desirable side-effects on Windows; imports winsock error numbers
    from errno import WSAEADDRINUSE  # pylint: disable=unused-import
except (ImportError, AttributeError):
    WSAEADDRINUSE = EADDRINUSE


_DISCONNECTED = frozenset((
    ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, EPIPE, EBADF, ECONNREFUSED,
    EHOSTUNREACH, ENETUNREACH, ETIMEDOUT, WSAECONNRESET))

OP_READ = 1
OP_WRITE = 2

try:
    socket_map
except NameError:
    socket_map = {}


def _strerror(err):
    try:
        return os.strerror(err)
    except (ValueError, OverflowError, NameError):
        if err in errorcode:
            return errorcode[err]
        return "Unknown error %s" % err


class ExitNow(Exception):
    """We don't use directly but may be necessary as we replace asyncore due to some library raising or expecting it"""
    pass


_reraised_exceptions = (ExitNow, KeyboardInterrupt, SystemExit)

maxDownloadRate = 0
downloadTimestamp = 0
downloadBucket = 0
receivedBytes = 0
maxUploadRate = 0
uploadTimestamp = 0
uploadBucket = 0
sentBytes = 0


def read(obj):
    """Event to read from the object, i.e. its network socket."""

    if not can_receive():
        return
    try:
        obj.handle_read_event()
    except _reraised_exceptions:
        raise
    except BaseException:
        obj.handle_error()


def write(obj):
    """Event to write to the object, i.e. its network socket."""

    if not can_send():
        return
    try:
        obj.handle_write_event()
    except _reraised_exceptions:
        raise
    except BaseException:
        obj.handle_error()


def set_rates(download, upload):
    """Set throttling rates"""

    global maxDownloadRate, maxUploadRate, downloadBucket, uploadBucket, downloadTimestamp, uploadTimestamp

    maxDownloadRate = float(download) * 1024
    maxUploadRate = float(upload) * 1024
    downloadBucket = maxDownloadRate
    uploadBucket = maxUploadRate
    downloadTimestamp = time.time()
    uploadTimestamp = time.time()


def can_receive():
    """Predicate indicating whether the download throttle is in effect"""

    return maxDownloadRate == 0 or downloadBucket > 0


def can_send():
    """Predicate indicating whether the upload throttle is in effect"""

    return maxUploadRate == 0 or uploadBucket > 0


def update_received(download=0):
    """Update the receiving throttle"""

    global receivedBytes, downloadBucket, downloadTimestamp

    currentTimestamp = time.time()
    receivedBytes += download
    if maxDownloadRate > 0:
        bucketIncrease = maxDownloadRate * (currentTimestamp - downloadTimestamp)
        downloadBucket += bucketIncrease
        if downloadBucket > maxDownloadRate:
            downloadBucket = int(maxDownloadRate)
        downloadBucket -= download
    downloadTimestamp = currentTimestamp


def update_sent(upload=0):
    """Update the sending throttle"""

    global sentBytes, uploadBucket, uploadTimestamp

    currentTimestamp = time.time()
    sentBytes += upload
    if maxUploadRate > 0:
        bucketIncrease = maxUploadRate * (currentTimestamp - uploadTimestamp)
        uploadBucket += bucketIncrease
        if uploadBucket > maxUploadRate:
            uploadBucket = int(maxUploadRate)
        uploadBucket -= upload
    uploadTimestamp = currentTimestamp


def _exception(obj):
    """Handle exceptions as appropriate"""

    try:
        obj.handle_expt_event()
    except _reraised_exceptions:
        raise
    except BaseException:
        obj.handle_error()


def readwrite(obj, flags):
    """Read and write any pending data to/from the object"""

    try:
        if flags & select.POLLIN and can_receive():
            obj.handle_read_event()
        if flags & select.POLLOUT and can_send():
            obj.handle_write_event()
        if flags & select.POLLPRI:
            obj.handle_expt_event()
        if flags & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
            obj.handle_close()
    except socket.error as e:
        if e.args[0] not in _DISCONNECTED:
            obj.handle_error()
        else:
            obj.handle_close()
    except _reraised_exceptions:
        raise
    except BaseException:
        obj.handle_error()


def select_poller(timeout=0.0, map=None):
    """A poller which uses select(), available on most platforms."""
    # pylint: disable=redefined-builtin

    if map is None:
        map = socket_map
    if map:
        r = []
        w = []
        e = []
        for fd, obj in list(map.items()):
            is_r = obj.readable()
            is_w = obj.writable()
            if is_r:
                r.append(fd)
            # accepting sockets should not be writable
            if is_w and not obj.accepting:
                w.append(fd)
            if is_r or is_w:
                e.append(fd)
        if [] == r == w == e:
            time.sleep(timeout)
            return

        try:
            r, w, e = select.select(r, w, e, timeout)
        except KeyboardInterrupt:
            return
        except socket.error as err:
            if err.args[0] in (EBADF, EINTR):
                return
        except Exception as err:
            if err.args[0] in (WSAENOTSOCK, ):
                return

        for fd in helper_random.randomsample(r, len(r)):
            obj = map.get(fd)
            if obj is None:
                continue
            read(obj)

        for fd in helper_random.randomsample(w, len(w)):
            obj = map.get(fd)
            if obj is None:
                continue
            write(obj)

        for fd in e:
            obj = map.get(fd)
            if obj is None:
                continue
            _exception(obj)
    else:
        current_thread().stop.wait(timeout)


def poll_poller(timeout=0.0, map=None):
    """A poller which uses poll(), available on most UNIXen."""
    # pylint: disable=redefined-builtin

    if map is None:
        map = socket_map
    if timeout is not None:
        # timeout is in milliseconds
        timeout = int(timeout * 1000)
    try:
        poll_poller.pollster
    except AttributeError:
        poll_poller.pollster = select.poll()
    if map:
        for fd, obj in list(map.items()):
            flags = newflags = 0
            if obj.readable():
                flags |= select.POLLIN | select.POLLPRI
                newflags |= OP_READ
            else:
                newflags &= ~ OP_READ
            # accepting sockets should not be writable
            if obj.writable() and not obj.accepting:
                flags |= select.POLLOUT
                newflags |= OP_WRITE
            else:
                newflags &= ~ OP_WRITE
            if newflags != obj.poller_flags:
                obj.poller_flags = newflags
                try:
                    if obj.poller_registered:
                        poll_poller.pollster.modify(fd, flags)
                    else:
                        poll_poller.pollster.register(fd, flags)
                        obj.poller_registered = True
                except IOError:
                    pass
        try:
            r = poll_poller.pollster.poll(timeout)
        except KeyboardInterrupt:
            r = []
        except socket.error as err:
            if err.args[0] in (EBADF, WSAENOTSOCK, EINTR):
                return
        for fd, flags in helper_random.randomsample(r, len(r)):
            obj = map.get(fd)
            if obj is None:
                continue
            readwrite(obj, flags)
    else:
        current_thread().stop.wait(timeout)


# Aliases for backward compatibility
poll = select_poller
poll2 = poll3 = poll_poller


def epoll_poller(timeout=0.0, map=None):
    """A poller which uses epoll(), supported on Linux 2.5.44 and newer."""
    # pylint: disable=redefined-builtin

    if map is None:
        map = socket_map
    try:
        epoll_poller.pollster
    except AttributeError:
        epoll_poller.pollster = select.epoll()
    if map:
        for fd, obj in map.items():
            flags = newflags = 0
            if obj.readable():
                flags |= select.POLLIN | select.POLLPRI
                newflags |= OP_READ
            else:
                newflags &= ~ OP_READ
            # accepting sockets should not be writable
            if obj.writable() and not obj.accepting:
                flags |= select.POLLOUT
                newflags |= OP_WRITE
            else:
                newflags &= ~ OP_WRITE
            if newflags != obj.poller_flags:
                obj.poller_flags = newflags
                # Only check for exceptions if object was either readable
                # or writable.
                flags |= select.POLLERR | select.POLLHUP | select.POLLNVAL
                try:
                    if obj.poller_registered:
                        epoll_poller.pollster.modify(fd, flags)
                    else:
                        epoll_poller.pollster.register(fd, flags)
                        obj.poller_registered = True
                except IOError:
                    pass
        try:
            r = epoll_poller.pollster.poll(timeout)
        except IOError as e:
            if e.errno != EINTR:
                raise
            r = []
        except select.error as err:
            if err.args[0] != EINTR:
                raise
            r = []
        for fd, flags in helper_random.randomsample(r, len(r)):
            obj = map.get(fd)
            if obj is None:
                continue
            readwrite(obj, flags)
    else:
        current_thread().stop.wait(timeout)


def kqueue_poller(timeout=0.0, map=None):
    """A poller which uses kqueue(), BSD specific."""
    # pylint: disable=redefined-builtin,no-member

    if map is None:
        map = socket_map
    try:
        kqueue_poller.pollster
    except AttributeError:
        kqueue_poller.pollster = select.kqueue()
    if map:
        updates = []
        selectables = 0
        for fd, obj in map.items():
            kq_filter = 0
            if obj.readable():
                kq_filter |= 1
                selectables += 1
            if obj.writable() and not obj.accepting:
                kq_filter |= 2
                selectables += 1
            if kq_filter != obj.poller_filter:
                # unlike other pollers, READ and WRITE aren't OR able but have
                # to be set and checked separately
                if kq_filter & 1 != obj.poller_filter & 1:
                    poller_flags = select.KQ_EV_ADD
                    if kq_filter & 1:
                        poller_flags |= select.KQ_EV_ENABLE
                    else:
                        poller_flags |= select.KQ_EV_DISABLE
                    updates.append(select.kevent(fd, filter=select.KQ_FILTER_READ, flags=poller_flags))
                if kq_filter & 2 != obj.poller_filter & 2:
                    poller_flags = select.KQ_EV_ADD
                    if kq_filter & 2:
                        poller_flags |= select.KQ_EV_ENABLE
                    else:
                        poller_flags |= select.KQ_EV_DISABLE
                    updates.append(select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=poller_flags))
                obj.poller_filter = kq_filter

        if not selectables:
            # unlike other pollers, kqueue poll does not wait if there are no
            # filters setup
            current_thread().stop.wait(timeout)
            return

        events = kqueue_poller.pollster.control(updates, selectables, timeout)
        if len(events) > 1:
            events = helper_random.randomsample(events, len(events))

        for event in events:
            fd = event.ident
            obj = map.get(fd)
            if obj is None:
                continue
            if event.flags & select.KQ_EV_ERROR:
                _exception(obj)
                continue
            if event.flags & select.KQ_EV_EOF and event.data and event.fflags:
                obj.handle_close()
                continue
            if event.filter == select.KQ_FILTER_READ:
                read(obj)
            if event.filter == select.KQ_FILTER_WRITE:
                write(obj)
    else:
        current_thread().stop.wait(timeout)


def loop(timeout=30.0, use_poll=False, map=None, count=None, poller=None):
    """Poll in a loop, until count or timeout is reached"""
    # pylint: disable=redefined-builtin

    if map is None:
        map = socket_map
    if count is None:
        count = True
    # code which grants backward compatibility with "use_poll"
    # argument which should no longer be used in favor of
    # "poller"

    if poller is None:
        if use_poll:
            poller = poll_poller
        elif hasattr(select, 'epoll'):
            poller = epoll_poller
        elif hasattr(select, 'kqueue'):
            poller = kqueue_poller
        elif hasattr(select, 'poll'):
            poller = poll_poller
        elif hasattr(select, 'select'):
            poller = select_poller

    if timeout == 0:
        deadline = 0
    else:
        deadline = time.time() + timeout
    while count:
        # fill buckets first
        update_sent()
        update_received()
        subtimeout = deadline - time.time()
        if subtimeout <= 0:
            break
        # then poll
        poller(subtimeout, map)
        if isinstance(count, int):
            count = count - 1


class dispatcher:
    """Dispatcher for socket objects"""
    # pylint: disable=too-many-public-methods,too-many-instance-attributes,old-style-class

    debug = False
    connected = False
    accepting = False
    connecting = False
    closing = False
    addr = None
    ignore_log_types = frozenset(['warning'])
    poller_registered = False
    poller_flags = 0
    # don't do network IO with a smaller bucket than this
    minTx = 1500

    def __init__(self, sock=None, map=None):
        # pylint: disable=redefined-builtin
        if map is None:
            self._map = socket_map
        else:
            self._map = map

        self._fileno = None

        if sock:
            # Set to nonblocking just to make sure for cases where we
            # get a socket from a blocking source.
            sock.setblocking(0)
            self.set_socket(sock, map)
            self.connected = True
            # The constructor no longer requires that the socket
            # passed be connected.
            try:
                self.addr = sock.getpeername()
            except socket.error as err:
                if err.args[0] in (ENOTCONN, EINVAL):
                    # To handle the case where we got an unconnected
                    # socket.
                    self.connected = False
                else:
                    # The socket is broken in some unknown way, alert
                    # the user and remove it from the map (to prevent
                    # polling of broken sockets).
                    self.del_channel(map)
                    raise
        else:
            self.socket = None

    def __repr__(self):
        status = [self.__class__.__module__ + "." + self.__class__.__name__]
        if self.accepting and self.addr:
            status.append('listening')
        elif self.connected:
            status.append('connected')
        if self.addr is not None:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
        return '<%s at %#x>' % (' '.join(status), id(self))

    __str__ = __repr__

    def add_channel(self, map=None):
        """Add a channel"""
        # pylint: disable=redefined-builtin

        if map is None:
            map = self._map
        map[self._fileno] = self
        self.poller_flags = 0
        self.poller_filter = 0

    def del_channel(self, map=None):
        """Delete a channel"""
        # pylint: disable=redefined-builtin

        fd = self._fileno
        if map is None:
            map = self._map
        if fd in map:
            del map[fd]
        if self._fileno:
            try:
                kqueue_poller.pollster.control([select.kevent(fd, select.KQ_FILTER_READ, select.KQ_EV_DELETE)], 0)
            except (AttributeError, KeyError, TypeError, IOError, OSError):
                pass
            try:
                kqueue_poller.pollster.control([select.kevent(fd, select.KQ_FILTER_WRITE, select.KQ_EV_DELETE)], 0)
            except (AttributeError, KeyError, TypeError, IOError, OSError):
                pass
            try:
                epoll_poller.pollster.unregister(fd)
            except (AttributeError, KeyError, TypeError, IOError):
                # no epoll used, or not registered
                pass
            try:
                poll_poller.pollster.unregister(fd)
            except (AttributeError, KeyError, TypeError, IOError):
                # no poll used, or not registered
                pass
        self._fileno = None
        self.poller_flags = 0
        self.poller_filter = 0
        self.poller_registered = False

    def create_socket(self, family=socket.AF_INET, socket_type=socket.SOCK_STREAM):
        """Create a socket"""
        self.family_and_type = family, socket_type
        sock = socket.socket(family, socket_type)
        sock.setblocking(0)
        self.set_socket(sock)

    def set_socket(self, sock, map=None):
        """Set socket"""
        # pylint: disable=redefined-builtin

        self.socket = sock
        self._fileno = sock.fileno()
        self.add_channel(map)

    def set_reuse_addr(self):
        """try to re-use a server port if possible"""

        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
            )
        except socket.error:
            pass

    # ==================================================
    # predicates for select()
    # these are used as filters for the lists of sockets
    # to pass to select().
    # ==================================================

    def readable(self):
        """Predicate to indicate download throttle status"""
        if maxDownloadRate > 0:
            return downloadBucket > dispatcher.minTx
        return True

    def writable(self):
        """Predicate to indicate upload throttle status"""
        if maxUploadRate > 0:
            return uploadBucket > dispatcher.minTx
        return True

    # ==================================================
    # socket object methods.
    # ==================================================

    def listen(self, num):
        """Listen on a port"""
        self.accepting = True
        if os.name == 'nt' and num > 5:
            num = 5
        return self.socket.listen(num)

    def bind(self, addr):
        """Bind to an address"""
        self.addr = addr
        return self.socket.bind(addr)

    def connect(self, address):
        """Connect to an address"""
        self.connected = False
        self.connecting = True
        err = self.socket.connect_ex(address)
        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK, WSAEWOULDBLOCK) \
                or err == EINVAL and os.name in ('nt', 'ce'):
            self.addr = address
            return
        if err in (0, EISCONN):
            self.addr = address
            self.handle_connect_event()
        else:
            raise socket.error(err, errorcode[err])

    def accept(self):
        """Accept incoming connections. Returns either an address pair or None."""
        try:
            conn, addr = self.socket.accept()
        except TypeError:
            return None
        except socket.error as why:
            if why.args[0] in (EWOULDBLOCK, WSAEWOULDBLOCK, ECONNABORTED, EAGAIN, ENOTCONN):
                return None
            else:
                raise
        else:
            return conn, addr

    def send(self, data):
        """Send data"""
        try:
            result = self.socket.send(data)
            return result
        except socket.error as why:
            if why.args[0] in (EAGAIN, EWOULDBLOCK, WSAEWOULDBLOCK):
                return 0
            elif why.args[0] in _DISCONNECTED:
                self.handle_close()
                return 0
            else:
                raise

    def recv(self, buffer_size):
        """Receive data"""
        try:
            data = self.socket.recv(buffer_size)
            if not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() return 0.
                self.handle_close()
                return b''
            return data
        except socket.error as why:
            # winsock sometimes raises ENOTCONN
            if why.args[0] in (EAGAIN, EWOULDBLOCK, WSAEWOULDBLOCK):
                return b''
            if why.args[0] in _DISCONNECTED:
                self.handle_close()
                return b''
            else:
                raise

    def close(self):
        """Close connection"""
        self.connected = False
        self.accepting = False
        self.connecting = False
        self.del_channel()
        try:
            self.socket.close()
        except socket.error as why:
            if why.args[0] not in (ENOTCONN, EBADF):
                raise

    # cheap inheritance, used to pass all other attribute
    # references to the underlying socket object.
    def __getattr__(self, attr):
        try:
            # import pdb;pdb.set_trace()
            retattr = getattr(self.socket, attr)
        except AttributeError:
            raise AttributeError("{} instance has no attribute {}"
                                 .format(self.__class__.__name__, attr))
        else:
            msg = "%(me)s.%(attr)s is deprecated; use %(me)s.socket.%(attr)s " \
                  "instead" % {'me': self.__class__.__name__, 'attr': attr}
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return retattr

    # log and log_info may be overridden to provide more sophisticated
    # logging and warning methods. In general, log is for 'hit' logging
    # and 'log_info' is for informational, warning and error logging.

    def log(self, message):
        """Log a message to stderr"""
        sys.stderr.write('log: %s\n' % str(message))

    def log_info(self, message, log_type='info'):
        """Conditionally print a message"""
        if log_type not in self.ignore_log_types:
            print ('{}: {}'.format((log_type, message)))

    def handle_read_event(self):
        """Handle a read event"""
        if self.accepting:
            # accepting sockets are never connected, they "spawn" new
            # sockets that are connected
            self.handle_accept()
        elif not self.connected:
            if self.connecting:
                self.handle_connect_event()
            self.handle_read()
        else:
            self.handle_read()

    def handle_connect_event(self):
        """Handle a connection event"""
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            raise socket.error(err, _strerror(err))
        self.handle_connect()
        self.connected = True
        self.connecting = False

    def handle_write_event(self):
        """Handle a write event"""
        if self.accepting:
            # Accepting sockets shouldn't get a write event.
            # We will pretend it didn't happen.
            return

        if not self.connected:
            if self.connecting:
                self.handle_connect_event()
        self.handle_write()

    def handle_expt_event(self):
        """Handle expected exceptions"""
        # handle_expt_event() is called if there might be an error on the
        # socket, or if there is OOB data
        # check for the error condition first
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            # we can get here when select.select() says that there is an
            # exceptional condition on the socket
            # since there is an error, we'll go ahead and close the socket
            # like we would in a subclassed handle_read() that received no
            # data
            self.handle_close()
        elif sys.platform.startswith("win"):
            # async connect failed
            self.handle_close()
        else:
            self.handle_expt()

    def handle_error(self):
        """Handle unexpected exceptions"""
        _, t, v, tbinfo = compact_traceback()

        # sometimes a user repr method will crash.
        try:
            self_repr = repr(self)
        except BaseException:
            self_repr = '<__repr__(self) failed for object at %0x>' % id(self)

        self.log_info(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (
                self_repr,
                t,
                v,
                tbinfo
            ),
            'error'
        )
        self.handle_close()

    def handle_accept(self):
        """Handle an accept event"""
        pair = self.accept()
        if pair is not None:
            self.handle_accepted(*pair)

    def handle_expt(self):
        """Log that the subclass does not implement handle_expt"""
        self.log_info('unhandled incoming priority event', 'warning')

    def handle_read(self):
        """Log that the subclass does not implement handle_read"""
        self.log_info('unhandled read event', 'warning')

    def handle_write(self):
        """Log that the subclass does not implement handle_write"""
        self.log_info('unhandled write event', 'warning')

    def handle_connect(self):
        """Log that the subclass does not implement handle_connect"""
        self.log_info('unhandled connect event', 'warning')

    def handle_accepted(self, sock, addr):
        """Log that the subclass does not implement handle_accepted"""
        sock.close()
        self.log_info('unhandled accepted event on %s' % (addr), 'warning')

    def handle_close(self):
        """Log that the subclass does not implement handle_close"""
        self.log_info('unhandled close event', 'warning')
        self.close()


class dispatcher_with_send(dispatcher):
    """
    adds simple buffered output capability, useful for simple clients.
    [for more sophisticated usage use asynchat.async_chat]
    """
    # pylint: disable=redefined-builtin

    def __init__(self, sock=None, map=None):
        # pylint: disable=redefined-builtin

        dispatcher.__init__(self, sock, map)
        self.out_buffer = b''

    def initiate_send(self):
        """Initiate a send"""
        num_sent = 0
        num_sent = dispatcher.send(self, self.out_buffer[:512])
        self.out_buffer = self.out_buffer[num_sent:]

    def handle_write(self):
        """Handle a write event"""
        self.initiate_send()

    def writable(self):
        """Predicate to indicate if the object is writable"""
        return not self.connected or len(self.out_buffer)

    def send(self, data):
        """Send data"""
        if self.debug:
            self.log_info('sending %s' % repr(data))
        self.out_buffer = self.out_buffer + data
        self.initiate_send()


# ---------------------------------------------------------------------------
# used for debugging.
# ---------------------------------------------------------------------------


def compact_traceback():
    """Return a compact traceback"""
    t, v, tb = sys.exc_info()
    tbinfo = []
    if not tb:  # Must have a traceback
        raise AssertionError("traceback does not exist")
    while tb:
        tbinfo.append((
            tb.tb_frame.f_code.co_filename,
            tb.tb_frame.f_code.co_name,
            str(tb.tb_lineno)
        ))
        tb = tb.tb_next

    # just to be safe
    del tb

    filename, function, line = tbinfo[-1]
    info = ' '.join(['[%s|%s|%s]' % x for x in tbinfo])
    return (filename, function, line), t, v, info


def close_all(map=None, ignore_all=False):
    """Close all connections"""
    # pylint: disable=redefined-builtin

    if map is None:
        map = socket_map
    for x in list(map.values()):
        try:
            x.close()
        except OSError as e:
            if e.args[0] == EBADF:
                pass
            elif not ignore_all:
                raise
        except _reraised_exceptions:
            raise
        except BaseException:
            if not ignore_all:
                raise
    map.clear()


# Asynchronous File I/O:
#
# After a little research (reading man pages on various unixen, and
# digging through the linux kernel), I've determined that select()
# isn't meant for doing asynchronous file i/o.
# Heartening, though - reading linux/mm/filemap.c shows that linux
# supports asynchronous read-ahead.  So _MOST_ of the time, the data
# will be sitting in memory for us already when we go to read it.
#
# What other OS's (besides NT) support async file i/o?  [VMS?]
#
# Regardless, this is useful for pipes, and stdin/stdout...


if os.name == 'posix':
    import fcntl

    class file_wrapper:
        """
        Here we override just enough to make a file look like a socket for the purposes of asyncore.

        The passed fd is automatically os.dup()'d
        """
        # pylint: disable=old-style-class

        def __init__(self, fd):
            self.fd = os.dup(fd)

        def recv(self, *args):
            """Fake recv()"""
            return os.read(self.fd, *args)

        def send(self, *args):
            """Fake send()"""
            return os.write(self.fd, *args)

        def getsockopt(self, level, optname, buflen=None):
            """Fake getsockopt()"""
            if (level == socket.SOL_SOCKET and
                    optname == socket.SO_ERROR and
                    not buflen):
                return 0
            raise NotImplementedError("Only asyncore specific behaviour "
                                      "implemented.")

        read = recv
        write = send

        def close(self):
            """Fake close()"""
            os.close(self.fd)

        def fileno(self):
            """Fake fileno()"""
            return self.fd

    class file_dispatcher(dispatcher):
        """A dispatcher for file_wrapper objects"""

        def __init__(self, fd, map=None):
            # pylint: disable=redefined-builtin

            dispatcher.__init__(self, None, map)
            self.connected = True
            try:
                fd = fd.fileno()
            except AttributeError:
                pass
            self.set_file(fd)
            # set it to non-blocking mode
            flags = fcntl.fcntl(fd, fcntl.F_GETFL, 0)
            flags = flags | os.O_NONBLOCK
            fcntl.fcntl(fd, fcntl.F_SETFL, flags)

        def set_file(self, fd):
            """Set file"""
            self.socket = file_wrapper(fd)
            self._fileno = self.socket.fileno()
            self.add_channel()
