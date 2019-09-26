"""
src/network/advanceddispatcher.py
=================================
"""
# pylint: disable=attribute-defined-outside-init

import socket
import threading
import time

import network.asyncore_pollchoose as asyncore
import state
from debug import logger
from helper_threading import BusyError, nonBlocking


class ProcessingError(Exception):
    """General class for protocol parser exception, use as a base for others."""
    pass


class UnknownStateError(ProcessingError):
    """Parser points to an unknown (unimplemented) state."""
    pass


class AdvancedDispatcher(asyncore.dispatcher):
    """Improved version of asyncore dispatcher, with buffers and protocol state."""
    # pylint: disable=too-many-instance-attributes
    _buf_len = 131072  # 128kB

    def __init__(self, sock=None):
        # python 2 below condition is used
        # if not hasattr(self, '_map'):
        # python 3 below condition is used
        if not '_map' in dir(self):
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
        """Append binary data to the end of stream write buffer."""
        if data:
            if isinstance(data, list):
                with self.writeLock:
                    for chunk in data:
                        self.write_buf.extend(chunk)
            else:
                with self.writeLock:
                    self.write_buf.extend(data)

    def slice_write_buf(self, length=0):
        """Cut the beginning of the stream write buffer."""
        if length > 0:
            with self.writeLock:
                if length >= len(self.write_buf):
                    del self.write_buf[:]
                else:
                    del self.write_buf[0:length]

    def slice_read_buf(self, length=0):
        """Cut the beginning of the stream read buffer."""
        if length > 0:
            with self.readLock:
                if length >= len(self.read_buf):
                    del self.read_buf[:]
                else:
                    del self.read_buf[0:length]

    def process(self):
        """Process (parse) data that's in the buffer, as long as there is enough data and the connection is open."""
        while self.connected and not state.shutdown:
            try:
                with nonBlocking(self.processingLock):
                    if not self.connected or state.shutdown:
                        break
                    if len(self.read_buf) < self.expectBytes:
                        return False
                    try:
                        cmd = getattr(self, "state_" + str(self.state))
                    except AttributeError:
                        logger.error("Unknown state %s", self.state, exc_info=True)
                        raise UnknownStateError(self.state)
                    if not cmd():
                        break
            except BusyError:
                return False
        return False

    def set_state(self, state_str, length=0, expectBytes=0):
        """Set the next processing state."""
        self.expectBytes = expectBytes
        self.slice_read_buf(length)
        self.state = state_str

    def writable(self):
        """Is data from the write buffer ready to be sent to the network?"""
        self.uploadChunk = AdvancedDispatcher._buf_len
        if asyncore.maxUploadRate > 0:
            self.uploadChunk = int(asyncore.uploadBucket)
        self.uploadChunk = min(self.uploadChunk, len(self.write_buf))
        return asyncore.dispatcher.writable(self) and \
            (self.connecting or (self.connected and self.uploadChunk > 0))

    def readable(self):
        """Is the read buffer ready to accept data from the network?"""
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
        """Append incoming data to the read buffer."""
        self.lastTx = time.time()
        newData = self.recv(self.downloadChunk)
        self.receivedBytes += len(newData)
        asyncore.update_received(len(newData))
        with self.readLock:
            self.read_buf.extend(newData)

    def handle_write(self):
        """Send outgoing data from write buffer."""
        self.lastTx = time.time()
        written = self.send(self.write_buf[0:self.uploadChunk])
        asyncore.update_sent(written)
        self.sentBytes += written
        self.slice_write_buf(written)

    def handle_connect_event(self):
        """Callback for connection established event."""
        try:
            asyncore.dispatcher.handle_connect_event(self)
        except socket.error as e:
            if e.args[0] not in asyncore._DISCONNECTED:  # pylint: disable=protected-access
                raise

    def handle_connect(self):
        """Method for handling connection established implementations."""
        self.lastTx = time.time()

    def state_close(self):
        """Signal to the processing loop to end."""
        # pylint: disable=no-self-use
        return False

    def handle_close(self):
        """Callback for connection being closed, but can also be called directly when you want connection to close."""
        with self.readLock:
            self.read_buf = bytearray()
        with self.writeLock:
            self.write_buf = bytearray()
        self.set_state("close")
        self.close()
