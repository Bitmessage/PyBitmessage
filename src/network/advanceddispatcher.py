import asyncore

class AdvancedDispatcher(asyncore.dispatcher):
    _buf_len = 131072

    def __init__(self, sock):
        asyncore.dispatcher.__init__(self, sock)
        self.read_buf = ""
        self.write_buf = ""
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
        if len(self.read_buf) == 0:
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
        return len(self.write_buf) > 0

    def readable(self):
        return len(self.read_buf) < AdvancedDispatcher._buf_len

    def handle_read(self):
        self.read_buf += self.recv(AdvancedDispatcher._buf_len)
        self.process()

    def handle_write(self):
        written = self.send(self.write_buf)
        self.slice_write_buf(written)
#        self.process()
