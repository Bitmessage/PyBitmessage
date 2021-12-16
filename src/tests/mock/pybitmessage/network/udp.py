"""
UDP protocol handler
"""
import logging
import socket
import time

import protocol
import state
from bmproto import BMProto
from constants import MAX_TIME_OFFSET
from node import Peer
from objectracker import ObjectTracker
from queues import receiveDataQueue

logger = logging.getLogger('default')


class UDPSocket(BMProto):  # pylint: disable=too-many-instance-attributes
    """Bitmessage protocol over UDP (class)"""
    port = 8444

    def __init__(self, host=None, sock=None, announcing=False):
        # pylint: disable=bad-super-call
        super(BMProto, self).__init__(sock=sock)
        self.verackReceived = True
        self.verackSent = True
        # .. todo:: sort out streams
        self.streams = [1]
        self.fullyEstablished = True
        self.skipUntil = 0
        if sock is None:
            if host is None:
                host = ''
            self.create_socket(
                socket.AF_INET6 if ":" in host else socket.AF_INET,
                socket.SOCK_DGRAM
            )
            self.set_socket_reuse()
            logger.info("Binding UDP socket to %s:%i", host, self.port)
            self.socket.bind((host, self.port))
        else:
            self.socket = sock
            self.set_socket_reuse()
        self.listening = Peer(*self.socket.getsockname())
        self.destination = Peer(*self.socket.getsockname())
        ObjectTracker.__init__(self)
        self.connecting = False
        self.connected = True
        self.announcing = announcing
        self.set_state("bm_header", expectBytes=protocol.Header.size)

    def set_socket_reuse(self):
        """Set socket reuse option"""
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass

    # disable most commands before doing research / testing
    # only addr (peer discovery), error and object are implemented

    def bm_command_getdata(self):
        # return BMProto.bm_command_getdata(self)
        return True

    def bm_command_inv(self):
        # return BMProto.bm_command_inv(self)
        return True

    def bm_command_addr(self):
        addresses = self._decode_addr()
        # only allow peer discovery from private IPs in order to avoid
        # attacks from random IPs on the internet
        if not self.local:
            return True
        remoteport = False
        for seenTime, stream, _, ip, port in addresses:
            decodedIP = protocol.checkIPAddress(str(ip))
            if stream not in state.streamsInWhichIAmParticipating:
                continue
            if (seenTime < time.time() - MAX_TIME_OFFSET
                    or seenTime > time.time() + MAX_TIME_OFFSET):
                continue
            if decodedIP is False:
                # if the address isn't local, interpret it as
                # the host's own announcement
                remoteport = port
        if remoteport is False:
            return True
        logger.debug(
            "received peer discovery from %s:%i (port %i):",
            self.destination.host, self.destination.port, remoteport)
        state.discoveredPeers[Peer(self.destination.host, remoteport)] = \
            time.time()
        return True

    def bm_command_portcheck(self):
        return True

    def bm_command_ping(self):
        return True

    def bm_command_pong(self):
        return True

    def bm_command_verack(self):
        return True

    def bm_command_version(self):
        return True

    def handle_connect(self):
        return

    def writable(self):
        return self.write_buf

    def readable(self):
        return len(self.read_buf) < self._buf_len

    def handle_read(self):
        try:
            recdata, addr = self.socket.recvfrom(self._buf_len)
        except socket.error:
            logger.error("socket error on recvfrom:", exc_info=True)
            return

        self.destination = Peer(*addr)
        encodedAddr = protocol.encodeHost(addr[0])
        self.local = bool(protocol.checkIPAddress(encodedAddr, True))
        # overwrite the old buffer to avoid mixing data and so that
        # self.local works correctly
        self.read_buf[0:] = recdata
        self.bm_proto_reset()
        receiveDataQueue.put(self.listening)

    def handle_write(self):
        try:
            retval = self.socket.sendto(
                self.write_buf, ('<broadcast>', self.port))
        except socket.error:
            logger.error("socket error on sendto:", exc_info=True)
            retval = len(self.write_buf)
        self.slice_write_buf(retval)
