# This is an example of how to connect to and use the Bitmessage API.
# See https://bitmessage.org/wiki/API_Reference

import xmlrpclib
import json

api = xmlrpclib.ServerProxy("http://bradley:password@localhost:8442/")

print 'Let\'s test the API first.'
inputstr1 = "hello"
inputstr2 = "world"
print api.helloWorld(inputstr1, inputstr2)
print api.add(2,3)

print 'Let\'s set the status bar message.'
print api.statusBar("new status bar message")

print 'Let\'s list our addresses:'
print api.listAddresses()

print 'Let\'s list our address again, but this time let\'s parse the json data into a Python data structure:'
jsonAddresses = json.loads(api.listAddresses())
print jsonAddresses
print 'Now that we have our address data in a nice Python data structure, let\'s look at the first address (index 0) and print its label:'
print jsonAddresses['addresses'][0]['label']

print 'Uncomment this next line to create a new random address.'
#print api.createRandomAddress('new address label')

print 'Uncomment these next three lines to create new new deterministic addresses.'
#jsonDeterministicAddresses = api.createDeterministicAddresses('asdfasdfqwerasdf', 2, 2, 1, False)
#print jsonDeterministicAddresses
#print json.loads(jsonDeterministicAddresses)

print 'Let\'s now print all of our inbox messages:'
print api.getAllInboxMessages()
inboxMessages = json.loads(api.getAllInboxMessages())
print inboxMessages

print 'Uncomment this next line to decode the actual message data in the first message:'
#print inboxMessages['inboxMessages'][0]['message'].decode('base64')

print 'Uncomment this next line in the code to delete a message'
#print api.trashMessage('584e5826947242a82cb883c8b39ac4a14959f14c228c0fbe6399f73e2cba5b59')

"""print 'Now let\'s send a message. The example addresses are invalid. You will have to put your own in.'
subject = 'subject!'.encode('base64')
message = 'Hello, this is the message'.encode('base64')
print api.sendMessage('BM-oqmocYzqK74y3qSRi8c3YqyenyEKiMyLB', 'BM-omzGU4MtzSUCQhMNm5kPR6UNrJ4Q4zeFe', subject,message)"""

"""print 'Now let\'s send a broadcast. The example address is invalid; you will have to put your own in.'
subject = 'subject within broadcast'.encode('base64')
message = 'Hello, this is the message within a broadcast.'.encode('base64')
print api.sendBroadcast('BM-onf6V1RELPgeNN6xw9yhpAiNiRexSRD4e', subject,message)"""