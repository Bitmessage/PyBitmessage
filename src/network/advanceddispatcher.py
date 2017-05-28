import Queue
import time

import asyncore_pollchoose as asyncore
from debug import logger
from bmconfigparser import BMConfigParser

class AdvancedDispatcher(asyncore.dispatcher):
    _buf_len = 2097152 # 2MB

    def __init__(self, sock=None):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self, sock)
        self.read_buf = b""
        self.write_buf = b""
        self.writeQueue = Queue.Queue()
        self.receiveQueue = Queue.Queue()
        self.state = "init"
        self.lastTx = time.time()
        self.sentBytes = 0
        self.receivedBytes = 0
        self.expectBytes = 0

    def slice_write_buf(self, length=0):
        if length > 0:
            self.write_buf = self.write_buf[length:]

    def slice_read_buf(self, length=0):
        if length > 0:
            self.read_buf = self.read_buf[length:]

    def read_buf_sufficient(self, length=0):
        if len(self.read_buf) < length:
            return False
        else:
            return True

    def process(self):
        if self.state != "tls_handshake" and len(self.read_buf) == 0:
            return
        if not self.connected:
            return
        maxLoop = 20
        while maxLoop > 0:
            try:
#                print "Trying to handle state \"%s\"" % (self.state)
                if getattr(self, "state_" + str(self.state))() is False:
                    break
            except AttributeError:
                # missing state
                raise
            maxLoop -= 1

    def set_state(self, state, length=0, expectBytes=0):
        self.expectBytes = expectBytes
        self.slice_read_buf(length)
        self.state = state

    def writable(self):
        return asyncore.dispatcher.writable(self) and \
                (self.connecting or len(self.write_buf) > 0 or not self.writeQueue.empty())

    def readable(self):
        return asyncore.dispatcher.readable(self) and \
                (self.connecting or len(self.read_buf) < AdvancedDispatcher._buf_len)

    def handle_read(self):
        self.lastTx = time.time()
        downloadBytes = AdvancedDispatcher._buf_len
        if asyncore.maxDownloadRate > 0:
            downloadBytes = asyncore.downloadBucket
        if self.expectBytes > 0 and downloadBytes > self.expectBytes:
            downloadBytes = self.expectBytes
        if downloadBytes > 0:
            newData = self.recv(downloadBytes)
            self.receivedBytes += len(newData)
            if self.expectBytes > 0:
                self.expectBytes -= len(newData)
            asyncore.update_received(len(newData))
            self.read_buf += newData
        self.process()

    def handle_write(self):
        self.lastTx = time.time()
        bufSize = AdvancedDispatcher._buf_len
        if asyncore.maxUploadRate > 0:
            bufSize = asyncore.uploadBucket
        while len(self.write_buf) < bufSize:
            try:
                self.write_buf += self.writeQueue.get(False)
                self.writeQueue.task_done()
            except Queue.Empty:
                break
        if bufSize <= 0:
            return
        if len(self.write_buf) > 0:
            written = self.send(self.write_buf[0:bufSize])
            asyncore.update_sent(written)
            self.sentBytes += written
            self.slice_write_buf(written)

    def handle_connect(self):
        self.lastTx = time.time()
        self.process()

    def state_close(self):
        pass

    def close(self):
        self.read_buf = b""
        self.write_buf = b""
        self.state = "close"
        while True:
            try:
                self.writeQueue.get(False)
                self.writeQueue.task_done()
            except Queue.Empty:
                break
        while True:
            try:
                self.receiveQueue.get(False)
                self.receiveQueue.task_done()
            except Queue.Empty:
                break
        asyncore.dispatcher.close(self)
