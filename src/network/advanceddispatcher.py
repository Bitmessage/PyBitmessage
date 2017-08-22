import socket
import threading
import time

import asyncore_pollchoose as asyncore
from debug import logger
from helper_threading import BusyError, nonBlocking

class AdvancedDispatcher(asyncore.dispatcher):
    _buf_len = 2097152 # 2MB

    def __init__(self, sock=None):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self, sock)
        self.read_buf = b""
        self.write_buf = b""
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
            with self.writeLock:
                self.write_buf += data

    def slice_write_buf(self, length=0):
        if length > 0:
            with self.writeLock:
                self.write_buf = self.write_buf[length:]

    def slice_read_buf(self, length=0):
        if length > 0:
            with self.readLock:
                self.read_buf = self.read_buf[length:]

    def process(self):
        if not self.connected:
            return False
        while True:
            try:
                with nonBlocking(self.processingLock):
                    if len(self.read_buf) < self.expectBytes:
                        return False
                    if getattr(self, "state_" + str(self.state))() is False:
                        break
            except AttributeError:
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
            self.uploadChunk = asyncore.uploadBucket
        self.uploadChunk = min(self.uploadChunk, len(self.write_buf))
        return asyncore.dispatcher.writable(self) and \
                (self.connecting or self.uploadChunk > 0)

    def readable(self):
        self.downloadChunk = AdvancedDispatcher._buf_len
        if asyncore.maxDownloadRate > 0:
            self.downloadChunk = asyncore.downloadBucket
        try:
            if self.expectBytes > 0 and not self.fullyEstablished:
                self.downloadChunk = min(self.downloadChunk, self.expectBytes - len(self.read_buf))
        except AttributeError:
            pass
        return asyncore.dispatcher.readable(self) and \
                (self.connecting or self.downloadChunk > 0)

    def handle_read(self):
        self.lastTx = time.time()
        newData = self.recv(self.downloadChunk)
        self.receivedBytes += len(newData)
        asyncore.update_received(len(newData))
        with self.readLock:
            self.read_buf += newData

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
        self.read_buf = b""
        self.write_buf = b""
        self.state = "close"
        asyncore.dispatcher.close(self)
