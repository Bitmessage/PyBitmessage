import asyncore_pollchoose as asyncore

class AdvancedDispatcher(asyncore.dispatcher):
    _buf_len = 2097152 # 2MB

    def __init__(self):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self)
        self.read_buf = b""
        self.write_buf = b""
        self.state = "init"

    def slice_read_buf(self, length=0):
        self.read_buf = self.read_buf[length:]

    def slice_write_buf(self, length=0):
        self.write_buf = self.read_buf[length:]

    def read_buf_sufficient(self, length=0):
        if len(self.read_buf) < length:
            return False
        else:
            return True

    def process(self):
        if self.state != "init" and len(self.read_buf) == 0:
            return
        while True:
            try:
                if getattr(self, "state_" + str(self.state))() is False:
                    break
            except AttributeError:
                # missing state
                raise

    def set_state(self, state, length):
        self.slice_read_buf(length)
        self.state = state

    def writable(self):
        return self.connecting or len(self.write_buf) > 0

    def readable(self):
        return self.connecting or len(self.read_buf) < AdvancedDispatcher._buf_len

    def handle_read(self):
        self.read_buf += self.recv(AdvancedDispatcher._buf_len)
        self.process()

    def handle_write(self):
        written = self.send(self.write_buf)
        self.slice_write_buf(written)

    def handle_connect(self):
        self.process()
