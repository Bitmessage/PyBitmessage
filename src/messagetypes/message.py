class Message:
    def __init__(self, data):
        self.subject = data["subject"]
        self.body = data["body"]

    def process(self):
        print "Subject: %s" % (self.subject)
        print "Body: %s" % (self.body)
