import importlib
from os import listdir, path
from pprint import pprint
import sys
import traceback

data = {"": "message", "subject": "subject", "body": "body"}
#data = {"": "vote", "msgid": "msgid"}
#data = {"fsck": 1}

import messagetypes

if __name__ == '__main__':
    try:
        msgType = data[""]
    except KeyError:
        print "Message type missing"
        sys.exit(1)
    else:
        print "Message type: %s" % (msgType)
    msgObj = messagetypes.constructObject(data)
    if msgObj is None:
        sys.exit(1)
    try:
        msgObj.process()
    except:
        pprint(sys.exc_info())
