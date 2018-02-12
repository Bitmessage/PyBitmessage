import socket
import threading
import time

import asyncore_pollchoose as asyncore
from debug import logger
from helper_threading import BusyError, nonBlocking
import state

class AdvancedDispatcher(asyncore.dispatcher):
    _buf_len = 131072 # 128kB

    def __init__(self, sock=None):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self, sock)
        self.read_buf = bytearray()
        self.write_buf = bytearray()
        self.state = "init"
        self.lastTx = time.time()
        self.sentBytes = 0
        self.receivedBytes = 0
        self.expectBytes = 0
        self.readLock = threading.RLock()
        self.writeLock = threading.RLock()
        self.processingLock = threading.RLock()

    def append_write_buf(self, data):
        if data:
            if isinstance(data, list):
                with self.writeLock:
                    for chunk in data:
                        self.write_buf.extend(chunk)
            else:
                with self.writeLock:
                    self.write_buf.extend(data)

    def slice_write_buf(self, length=0):
        if length > 0:
            with self.writeLock:
                if length >= len(self.write_buf):
                    del self.write_buf[:]
                else:
                    del self.write_buf[0:length]

    def slice_read_buf(self, length=0):
        if length > 0:
            with self.readLock:
                if length >= len(self.read_buf):
                    del self.read_buf[:]
                else:
                    del self.read_buf[0:length]

    def process(self):
        while self.connected and not state.shutdown:
            try:
                with nonBlocking(self.processingLock):
                    if not self.connected or state.shutdown:
                        break
                    if len(self.read_buf) < self.expectBytes:
                        return False
                    if not getattr(self, "state_" + str(self.state))():
                        break
            except AttributeError:
                logger.error("Unknown state %s", self.state, exc_info=True)
                raise
            except BusyError:
                return False
        return False

    def set_state(self, state, length=0, expectBytes=0):
        self.expectBytes = expectBytes
        self.slice_read_buf(length)
        self.state = state

    def writable(self):
        self.uploadChunk = AdvancedDispatcher._buf_len
        if asyncore.maxUploadRate > 0:
            self.uploadChunk = int(asyncore.uploadBucket)
        self.uploadChunk = min(self.uploadChunk, len(self.write_buf))
        return asyncore.dispatcher.writable(self) and \
                (self.connecting or (self.connected and self.uploadChunk > 0))

    def readable(self):
        self.downloadChunk = AdvancedDispatcher._buf_len
        if asyncore.maxDownloadRate > 0:
            self.downloadChunk = int(asyncore.downloadBucket)
        try:
            if self.expectBytes > 0 and not self.fullyEstablished:
                self.downloadChunk = min(self.downloadChunk, self.expectBytes - len(self.read_buf))
                if self.downloadChunk < 0:
                    self.downloadChunk = 0
        except AttributeError:
            pass
        return asyncore.dispatcher.readable(self) and \
                (self.connecting or self.accepting or (self.connected and self.downloadChunk > 0))

    def handle_read(self):
        self.lastTx = time.time()
        newData = self.recv(self.downloadChunk)
        self.receivedBytes += len(newData)
        asyncore.update_received(len(newData))
        with self.readLock:
            self.read_buf.extend(newData)

    def handle_write(self):
        self.lastTx = time.time()
        written = self.send(self.write_buf[0:self.uploadChunk])
        asyncore.update_sent(written)
        self.sentBytes += written
        self.slice_write_buf(written)

    def handle_connect_event(self):
        try:
            asyncore.dispatcher.handle_connect_event(self)
        except socket.error as e:
            if e.args[0] not in asyncore._DISCONNECTED:
                raise

    def handle_connect(self):
        self.lastTx = time.time()

    def state_close(self):
        return False

    def handle_close(self):
        with self.readLock:
            self.read_buf = bytearray()
        with self.writeLock:
            self.write_buf = bytearray()
        self.set_state("close")
        self.close()
