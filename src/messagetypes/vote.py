class Vote:
    def __init__(self, data):
        self.msgid = data["msgid"]
        self.vote = data["vote"]

    def process(self):
        print "msgid: %s" % (self.msgid)
        print "vote: %s" % (self.vote)
