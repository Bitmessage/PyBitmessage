import Queue
import socket
import sys
import threading
import time

import asyncore_pollchoose as asyncore
from debug import logger

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
            return
        loop = 0
        while len(self.read_buf) >= self.expectBytes:
            loop += 1
            if loop > 1000:
                logger.error("Stuck at state %s, report this bug please", self.state)
                break
            try:
                if getattr(self, "state_" + str(self.state))() is False:
                    break
            except AttributeError:
                raise

    def set_state(self, state, length=0, expectBytes=0):
        self.expectBytes = expectBytes
        self.slice_read_buf(length)
        self.state = state

    def writable(self):
        return asyncore.dispatcher.writable(self) and \
                (self.connecting or self.write_buf)

    def readable(self):
        return asyncore.dispatcher.readable(self) and \
                (self.connecting or len(self.read_buf) < AdvancedDispatcher._buf_len)

    def handle_read(self):
        self.lastTx = time.time()
        downloadBytes = AdvancedDispatcher._buf_len
        if asyncore.maxDownloadRate > 0:
            downloadBytes = asyncore.downloadBucket
        if self.expectBytes > 0 and downloadBytes > self.expectBytes - len(self.read_buf):
            downloadBytes = self.expectBytes - len(self.read_buf)
        if downloadBytes > 0:
            newData = self.recv(downloadBytes)
            self.receivedBytes += len(newData)
            asyncore.update_received(len(newData))
            with self.readLock:
                self.read_buf += newData

    def handle_write(self):
        self.lastTx = time.time()
        bufSize = AdvancedDispatcher._buf_len
        if asyncore.maxUploadRate > 0:
            bufSize = asyncore.uploadBucket
        if bufSize <= 0:
            return
        if self.write_buf:
            written = self.send(self.write_buf[0:bufSize])
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
