"""Helper test used for generate random address and send message."""
import xmlrpclib
import time
import base64
import network.stats
from network.stats import pendingDownload


class RandomNumber(object):
    """docstring for RandomNumber."""

    def __init__(self):
        """Initialize the variables."""
        super(RandomNumber, self).__init__()

    def generateRandomNumber(self):
        """Generate random address and send messages."""
        api = xmlrpclib.ServerProxy("http://username:password@localhost:8442/")
        label = 'Test-' + str(time.time())
        random_address = api.createRandomAddress(base64.encodestring(label))
        fromsend = random_address
        tosend = "BM-2cWyUfBdY2FbgyuCb7abFZ49JYxSzUhNFe"
        subject = 'subject!'.encode('base64')
        message = 'Hello, this is the new asasf message'.encode('base64')

        try:
            ack_data = api.sendMessage(tosend, fromsend, subject, message)
            connectedhosts = len(network.stats.connectedHostsList())
            print "synchronisation in progress..."
            print "Connection Status: ", connectedhosts
            while pendingDownload() > 0:
                print "synchronisation in progress..."
                print "Connection Status: ", connectedhosts
                time.sleep(10)
            if ack_data:
                return True
            else:
                return False
        except:
            return False
