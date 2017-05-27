import base64
from binascii import hexlify
import hashlib
import math
import time
from pprint import pprint
import socket
import struct
import random
import traceback

from addresses import calculateInventoryHash
from debug import logger
from inventory import Inventory
import knownnodes
from network.advanceddispatcher import AdvancedDispatcher
from network.bmproto import BMProtoError, BMProtoInsufficientDataError, BMProtoExcessiveDataError, BMProto
from network.bmobject import BMObject, BMObjectInsufficientPOWError, BMObjectInvalidDataError, BMObjectExpiredError, BMObjectUnwantedStreamError, BMObjectInvalidError, BMObjectAlreadyHaveError
import network.connectionpool
from network.downloadqueue import DownloadQueue
from network.node import Node
import network.asyncore_pollchoose as asyncore
from network.objectracker import ObjectTracker
from network.uploadqueue import UploadQueue, UploadElem, AddrUploadQueue, ObjUploadQueue

import addresses
from bmconfigparser import BMConfigParser
from queues import objectProcessorQueue, peerDiscoveryQueue, portCheckerQueue, UISignalQueue
import shared
import state
import protocol

class UDPSocket(BMProto):
    port = 8444
    announceInterval = 60

    def __init__(self, host=None, sock=None):
        AdvancedDispatcher.__init__(self, sock)
        self.verackReceived = True
        self.verackSent = True
        # TODO sort out streams
        self.streams = [1]
        self.fullyEstablished = True
        self.connectedAt = 0
        self.skipUntil = 0
        self.isOutbound = False
        if sock is None:
            if host is None:
                host = ''
            if ":" in host:
                self.create_socket(socket.AF_INET6, socket.SOCK_DGRAM)
            else:
                self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
            print "binding to %s" % (host)
            self.socket.bind((host, UDPSocket.port))
            #BINDTODEVICE is only available on linux and requires root
            #try:
                #print "binding to %s" % (host)
                #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, host)
            #except AttributeError:
        else:
            self.socket = sock
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.destination = state.Peer(self.socket.getsockname()[0], self.socket.getsockname()[1])
        ObjectTracker.__init__(self)
        self.connecting = False
        self.connected = True
        # packet was received from a local IP
        self.local = False
        self.set_state("bm_header")

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
            return
        remoteport = False
        for i in addresses:
            seenTime, stream, services, ip, port = i
            decodedIP = protocol.checkIPAddress(ip)
            if stream not in state.streamsInWhichIAmParticipating:
                continue
            if seenTime < time.time() - BMProto.maxTimeOffset or seenTime > time.time() + BMProto.maxTimeOffset:
                continue
            if decodedIP is False:
                # if the address isn't local, interpret it as the hosts' own announcement
                remoteport = port
        if remoteport is False:
            return
        print "received peer discovery from %s:%i (port %i):" % (self.destination.host, self.destination.port, remoteport)
        if self.local:
            peerDiscoveryQueue.put(state.Peer(self.destination.host, remoteport))
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
        return not self.writeQueue.empty()

    def readable(self):
        return len(self.read_buf) < AdvancedDispatcher._buf_len

    def handle_read(self):
        try:
            (recdata, addr) = self.socket.recvfrom(AdvancedDispatcher._buf_len)
        except socket.error as e:
            print "socket error: %s" % (str(e))
            return

        self.destination = state.Peer(addr[0], addr[1])
        encodedAddr = protocol.encodeHost(addr[0])
        if protocol.checkIPAddress(encodedAddr, True):
            self.local = True
        else:
            self.local = False
        print "read %ib" % (len(recdata))
        # overwrite the old buffer to avoid mixing data and so that self.local works correctly
        self.read_buf = recdata
        self.bm_proto_reset()
        self.process()

    def handle_write(self):
#        print "handling write"
        try:
            data = self.writeQueue.get(False)
        except Queue.Empty:
            return
        try:
            retval = self.socket.sendto(data, ('<broadcast>', UDPSocket.port))
            print "broadcasted %ib" % (retval)
        except socket.error as e:
            print "socket error on sendato: %s" % (e)
        self.writeQueue.task_done()


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
