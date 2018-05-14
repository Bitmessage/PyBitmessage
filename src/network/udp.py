import time
import Queue
import socket

from debug import logger
from network.advanceddispatcher import AdvancedDispatcher
from network.bmproto import BMProtoError, BMProtoInsufficientDataError, BMProto
from network.bmobject import BMObject, BMObjectInsufficientPOWError, BMObjectInvalidDataError, BMObjectExpiredError, BMObjectInvalidError, BMObjectAlreadyHaveError
import network.asyncore_pollchoose as asyncore
from network.objectracker import ObjectTracker

from queues import objectProcessorQueue, UISignalQueue, receiveDataQueue
import state
import protocol

class UDPSocket(BMProto):
    port = 8444
    announceInterval = 60

    def __init__(self, host=None, sock=None, announcing=False):
        super(BMProto, self).__init__(sock=sock)
        self.verackReceived = True
        self.verackSent = True
        # TODO sort out streams
        self.streams = [1]
        self.fullyEstablished = True
        self.connectedAt = 0
        self.skipUntil = 0
        if sock is None:
            if host is None:
                host = ''
            if ":" in host:
                self.create_socket(socket.AF_INET6, socket.SOCK_DGRAM)
            else:
                self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.set_socket_reuse()
            logger.info("Binding UDP socket to %s:%i", host, UDPSocket.port)
            self.socket.bind((host, UDPSocket.port))
            #BINDTODEVICE is only available on linux and requires root
            #try:
                #print "binding to %s" % (host)
                #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, host)
            #except AttributeError:
        else:
            self.socket = sock
            self.set_socket_reuse()
        self.listening = state.Peer(self.socket.getsockname()[0], self.socket.getsockname()[1])
        self.destination = state.Peer(self.socket.getsockname()[0], self.socket.getsockname()[1])
        ObjectTracker.__init__(self)
        self.connecting = False
        self.connected = True
        self.announcing = announcing
        self.set_state("bm_header", expectBytes=protocol.Header.size)

    def set_socket_reuse(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass

    def state_bm_command(self):
        return BMProto.state_bm_command(self)

    # disable most commands before doing research / testing
    # only addr (peer discovery), error and object are implemented

    def bm_command_error(self):
        return BMProto.bm_command_error(self)

    def bm_command_getdata(self):
        return True
#        return BMProto.bm_command_getdata(self)

    def bm_command_inv(self):
        return True
#        return BMProto.bm_command_inv(self)

    def bm_command_object(self):
        return BMProto.bm_command_object(self)

    def bm_command_addr(self):
#        BMProto.bm_command_object(self)
        addresses = self._decode_addr()
        # only allow peer discovery from private IPs in order to avoid attacks from random IPs on the internet
        if not self.local:
            return True
        remoteport = False
        for i in addresses:
            seenTime, stream, services, ip, port = i
            decodedIP = protocol.checkIPAddress(str(ip))
            if stream not in state.streamsInWhichIAmParticipating:
                continue
            if seenTime < time.time() - BMProto.maxTimeOffset or seenTime > time.time() + BMProto.maxTimeOffset:
                continue
            if decodedIP is False:
                # if the address isn't local, interpret it as the hosts' own announcement
                remoteport = port
        if remoteport is False:
            return True
        logger.debug("received peer discovery from %s:%i (port %i):", self.destination.host, self.destination.port, remoteport)
        if self.local:
            state.discoveredPeers[state.Peer(self.destination.host, remoteport)] = time.time()
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
        return len(self.read_buf) < AdvancedDispatcher._buf_len

    def handle_read(self):
        try:
            (recdata, addr) = self.socket.recvfrom(AdvancedDispatcher._buf_len)
        except socket.error as e:
            logger.error("socket error: %s", str(e))
            return

        self.destination = state.Peer(addr[0], addr[1])
        encodedAddr = protocol.encodeHost(addr[0])
        if protocol.checkIPAddress(encodedAddr, True):
            self.local = True
        else:
            self.local = False
        # overwrite the old buffer to avoid mixing data and so that self.local works correctly
        self.read_buf[0:] = recdata
        self.bm_proto_reset()
        receiveDataQueue.put(self.listening)

    def handle_write(self):
        try:
            retval = self.socket.sendto(self.write_buf, ('<broadcast>', UDPSocket.port))
        except socket.error as e:
            logger.error("socket error on sendato: %s", str(e))
            retval = 0
        self.slice_write_buf(retval)


if __name__ == "__main__":
    # initial fill

    for host in (("127.0.0.1", 8448),):
        direct = BMConnection(host)
        while len(asyncore.socket_map) > 0:
            print "loop, state = %s" % (direct.state)
            asyncore.loop(timeout=10, count=1)
        continue

        proxy = Socks5BMConnection(host)
        while len(asyncore.socket_map) > 0:
#            print "loop, state = %s" % (proxy.state)
            asyncore.loop(timeout=10, count=1)

        proxy = Socks4aBMConnection(host)
        while len(asyncore.socket_map) > 0:
#            print "loop, state = %s" % (proxy.state)
            asyncore.loop(timeout=10, count=1)
