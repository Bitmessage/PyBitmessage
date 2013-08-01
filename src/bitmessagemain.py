#!/usr/bin/env python2.7
# Copyright (c) 2012 Jonathan Warren
# Copyright (c) 2012 The Bitmessage developers
# Distributed under the MIT/X11 software license. See the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Right now, PyBitmessage only support connecting to stream 1. It doesn't
# yet contain logic to expand into further streams.

# The software version variable is now held in shared.py

# import ctypes
try:
    from gevent import monkey
    monkey.patch_all()
except ImportError as ex:
    print "Not using the gevent module as it was not found. No need to worry."

import signal  # Used to capture a Ctrl-C keypress so that Bitmessage can shutdown gracefully.
# The next 3 are used for the API
from SimpleXMLRPCServer import *
import json
import singleton
import os

# Classes
from class_sqlThread import *
from class_singleCleaner import *
from class_singleWorker import *
from class_outgoingSynSender import *
from class_singleListener import *
from class_addressGenerator import *

# Helper Functions
import helper_bootstrap

import sys
if sys.platform == 'darwin':
    if float("{1}.{2}".format(*sys.version_info)) < 7.5:
        print "You should use python 2.7.5 or greater."
        print "Your version: {0}.{1}.{2}".format(*sys.version_info)
        sys.exit(0)

def connectToStream(streamNumber):
    selfInitiatedConnections[streamNumber] = {}
    if sys.platform[0:3] == 'win':
        maximumNumberOfHalfOpenConnections = 9
    else:
        maximumNumberOfHalfOpenConnections = 32
    for i in range(maximumNumberOfHalfOpenConnections):
        a = outgoingSynSender()
        a.setup(streamNumber, selfInitiatedConnections)
        a.start()


# This is one of several classes that constitute the API
# This class was written by Vaibhav Bhatia. Modified by Jonathan Warren (Atheros).
# http://code.activestate.com/recipes/501148-xmlrpc-serverclient-which-does-cookie-handling-and/
class MySimpleXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):

    def do_POST(self):
        # Handles the HTTP POST request.
        # Attempts to interpret all HTTP POST requests as XML-RPC calls,
        # which are forwarded to the server's _dispatch method for handling.

        # Note: this method is the same as in SimpleXMLRPCRequestHandler,
        # just hacked to handle cookies

        # Check that the path is legal
        if not self.is_rpc_path_valid():
            self.report_404()
            return

        try:
            # Get arguments by reading body of request.
            # We read this in chunks to avoid straining
            # socket.read(); around the 10 or 15Mb mark, some platforms
            # begin to have problems (bug #792570).
            max_chunk_size = 10 * 1024 * 1024
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                L.append(self.rfile.read(chunk_size))
                size_remaining -= len(L[-1])
            data = ''.join(L)

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(
                data, getattr(self, '_dispatch', None)
            )
        except:  # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))

            # HACK :start -> sends cookies here
            if self.cookies:
                for cookie in self.cookies:
                    self.send_header('Set-Cookie', cookie.output(header=''))
            # HACK :end

            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown(1)

    def APIAuthenticateClient(self):
        if 'Authorization' in self.headers:
            # handle Basic authentication
            (enctype, encstr) = self.headers.get('Authorization').split()
            (emailid, password) = encstr.decode('base64').split(':')
            if emailid == shared.config.get('bitmessagesettings', 'apiusername') and password == shared.config.get('bitmessagesettings', 'apipassword'):
                return True
            else:
                return False
        else:
            print 'Authentication failed because header lacks Authentication field'
            time.sleep(2)
            return False

        return False

    def _dispatch(self, method, params):
        self.cookies = []

        validuser = self.APIAuthenticateClient()
        if not validuser:
            time.sleep(2)
            return "RPC Username or password incorrect or HTTP header lacks authentication at all."
        # handle request
        if method == 'helloWorld':
            (a, b) = params
            return a + '-' + b
        elif method == 'add':
            (a, b) = params
            return a + b
        elif method == 'statusBar':
            message, = params
            shared.UISignalQueue.put(('updateStatusBar', message))
        elif method == 'listAddresses':
            data = '{"addresses":['
            configSections = shared.config.sections()
            for addressInKeysFile in configSections:
                if addressInKeysFile != 'bitmessagesettings':
                    status, addressVersionNumber, streamNumber, hash = decodeAddress(
                        addressInKeysFile)
                    data
                    if len(data) > 20:
                        data += ','
                    data += json.dumps({'label': shared.config.get(addressInKeysFile, 'label'), 'address': addressInKeysFile, 'stream':
                                       streamNumber, 'enabled': shared.config.getboolean(addressInKeysFile, 'enabled')}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'createRandomAddress':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            elif len(params) == 1:
                label, = params
                eighteenByteRipe = False
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 2:
                label, eighteenByteRipe = params
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 3:
                label, eighteenByteRipe, totalDifficulty = params
                nonceTrialsPerByte = int(
                    shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 4:
                label, eighteenByteRipe, totalDifficulty, smallMessageDifficulty = params
                nonceTrialsPerByte = int(
                    shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
                payloadLengthExtraBytes = int(
                    shared.networkDefaultPayloadLengthExtraBytes * smallMessageDifficulty)
            else:
                return 'API Error 0000: Too many parameters!'
            label = label.decode('base64')
            try:
                unicode(label, 'utf-8')
            except:
                return 'API Error 0017: Label is not valid UTF-8 data.'
            shared.apiAddressGeneratorReturnQueue.queue.clear()
            streamNumberForAddress = 1
            shared.addressGeneratorQueue.put((
                'createRandomAddress', 3, streamNumberForAddress, label, 1, "", eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes))
            return shared.apiAddressGeneratorReturnQueue.get()
        elif method == 'createDeterministicAddresses':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            elif len(params) == 1:
                passphrase, = params
                numberOfAddresses = 1
                addressVersionNumber = 0
                streamNumber = 0
                eighteenByteRipe = False
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 2:
                passphrase, numberOfAddresses = params
                addressVersionNumber = 0
                streamNumber = 0
                eighteenByteRipe = False
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 3:
                passphrase, numberOfAddresses, addressVersionNumber = params
                streamNumber = 0
                eighteenByteRipe = False
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 4:
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber = params
                eighteenByteRipe = False
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 5:
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe = params
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 6:
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe, totalDifficulty = params
                nonceTrialsPerByte = int(
                    shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 7:
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe, totalDifficulty, smallMessageDifficulty = params
                nonceTrialsPerByte = int(
                    shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
                payloadLengthExtraBytes = int(
                    shared.networkDefaultPayloadLengthExtraBytes * smallMessageDifficulty)
            else:
                return 'API Error 0000: Too many parameters!'
            if len(passphrase) == 0:
                return 'API Error 0001: The specified passphrase is blank.'
            passphrase = passphrase.decode('base64')
            if addressVersionNumber == 0:  # 0 means "just use the proper addressVersionNumber"
                addressVersionNumber = 3
            if addressVersionNumber != 3:
                return 'API Error 0002: The address version number currently must be 3 (or 0 which means auto-select). ' + addressVersionNumber + ' isn\'t supported.'
            if streamNumber == 0:  # 0 means "just use the most available stream"
                streamNumber = 1
            if streamNumber != 1:
                return 'API Error 0003: The stream number must be 1 (or 0 which means auto-select). Others aren\'t supported.'
            if numberOfAddresses == 0:
                return 'API Error 0004: Why would you ask me to generate 0 addresses for you?'
            if numberOfAddresses > 999:
                return 'API Error 0005: You have (accidentally?) specified too many addresses to make. Maximum 999. This check only exists to prevent mischief; if you really want to create more addresses than this, contact the Bitmessage developers and we can modify the check or you can do it yourself by searching the source code for this message.'
            shared.apiAddressGeneratorReturnQueue.queue.clear()
            print 'Requesting that the addressGenerator create', numberOfAddresses, 'addresses.'
            shared.addressGeneratorQueue.put(
                ('createDeterministicAddresses', addressVersionNumber, streamNumber,
                 'unused API address', numberOfAddresses, passphrase, eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes))
            data = '{"addresses":['
            queueReturn = shared.apiAddressGeneratorReturnQueue.get()
            for item in queueReturn:
                if len(data) > 20:
                    data += ','
                data += "\"" + item + "\""
            data += ']}'
            return data
        elif method == 'getDeterministicAddress':
            if len(params) != 3:
                return 'API Error 0000: I need exactly 3 parameters.'
            passphrase, addressVersionNumber, streamNumber = params
            numberOfAddresses = 1
            eighteenByteRipe = False
            if len(passphrase) == 0:
                return 'API Error 0001: The specified passphrase is blank.'
            passphrase = passphrase.decode('base64')
            if addressVersionNumber != 3:
                return 'API Error 0002: The address version number currently must be 3. ' + addressVersionNumber + ' isn\'t supported.'
            if streamNumber != 1:
                return 'API Error 0003: The stream number must be 1. Others aren\'t supported.'
            shared.apiAddressGeneratorReturnQueue.queue.clear()
            print 'Requesting that the addressGenerator create', numberOfAddresses, 'addresses.'
            shared.addressGeneratorQueue.put(
                ('getDeterministicAddress', addressVersionNumber,
                 streamNumber, 'unused API address', numberOfAddresses, passphrase, eighteenByteRipe))
            return shared.apiAddressGeneratorReturnQueue.get()
        elif method == 'getAllInboxMessages':
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype, read FROM inbox where folder='inbox' ORDER BY received''')
            shared.sqlSubmitQueue.put('')
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"inboxMessages":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype, read = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                if len(data) > 25:
                    data += ','
                data += json.dumps({'msgid': msgid.encode('hex'), 'toAddress': toAddress, 'fromAddress': fromAddress, 'subject': subject.encode(
                    'base64'), 'message': message.encode('base64'), 'encodingType': encodingtype, 'receivedTime': received, 'read': read}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getAllInboxMessageIds' or method == 'getAllInboxMessageIDs':
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT msgid FROM inbox where folder='inbox' ORDER BY received''')
            shared.sqlSubmitQueue.put('')
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"inboxMessageIds":['
            for row in queryreturn:
                msgid = row[0]
                if len(data) > 25:
                    data += ','
                data += json.dumps({'msgid': msgid.encode('hex')}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getInboxMessageById' or method == 'getInboxMessageByID':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            msgid = params[0].decode('hex')
            v = (msgid,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype, read FROM inbox WHERE msgid=?''')
            shared.sqlSubmitQueue.put(v)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"inboxMessage":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype, read = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                data += json.dumps({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'receivedTime':received, 'read': read}, indent=4, separators=(',', ': '))
                data += ']}'
                return data
        elif method == 'getAllSentMessages':
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent where folder='sent' ORDER BY lastactiontime''')
            shared.sqlSubmitQueue.put('')
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"sentMessages":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                if len(data) > 25:
                    data += ','
                data += json.dumps({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getAllSentMessageIds' or method == 'getAllSentMessageIDs':
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid FROM sent where folder='sent' ORDER BY lastactiontime''')
            shared.sqlSubmitQueue.put('')
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"sentMessageIds":['
            for row in queryreturn:
                msgid = row[0]
                if len(data) > 25:
                    data += ','
                data += json.dumps({'msgid':msgid.encode('hex')}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getInboxMessagesByReceiver' or method == 'getInboxMessagesByAddress': #after some time getInboxMessagesByAddress should be removed
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            toAddress = params[0]
            v = (toAddress,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype FROM inbox WHERE folder='inbox' AND toAddress=?''')
            shared.sqlSubmitQueue.put(v)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"inboxMessages":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                if len(data) > 25:
                    data += ','
                data += json.dumps({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'receivedTime':received}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getSentMessageById' or method == 'getSentMessageByID':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            msgid = params[0].decode('hex')
            v = (msgid,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE msgid=?''')
            shared.sqlSubmitQueue.put(v)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"sentMessage":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                data += json.dumps({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')}, indent=4, separators=(',', ': '))
                data += ']}'
                return data
        elif method == 'getSentMessagesByAddress' or method == 'getSentMessagesBySender':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            fromAddress = params[0]
            v = (fromAddress,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE folder='sent' AND fromAddress=? ORDER BY lastactiontime''')
            shared.sqlSubmitQueue.put(v)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"sentMessages":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                if len(data) > 25:
                    data += ','
                data += json.dumps({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getSentMessageByAckData':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            ackData = params[0].decode('hex')
            v = (ackData,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE ackdata=?''')
            shared.sqlSubmitQueue.put(v)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"sentMessage":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                data += json.dumps({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'trashMessage':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            msgid = params[0].decode('hex')
            
            # Trash if in inbox table
            helper_inbox.trash(msgid)
            # Trash if in sent table
            t = (msgid,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''UPDATE sent SET folder='trash' WHERE msgid=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            # shared.UISignalQueue.put(('removeSentRowByMsgid',msgid)) This function doesn't exist yet.
            return 'Trashed message (assuming message existed).'
        elif method == 'trashInboxMessage':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            msgid = params[0].decode('hex')
            helper_inbox.trash(msgid)
            return 'Trashed inbox message (assuming message existed).'
        elif method == 'trashSentMessage':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            msgid = params[0].decode('hex')
            t = (msgid,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''UPDATE sent SET folder='trash' WHERE msgid=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            # shared.UISignalQueue.put(('removeSentRowByMsgid',msgid)) This function doesn't exist yet.
            return 'Trashed sent message (assuming message existed).'
        elif method == 'sendMessage':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            elif len(params) == 4:
                toAddress, fromAddress, subject, message = params
                encodingType = 2
            elif len(params) == 5:
                toAddress, fromAddress, subject, message, encodingType = params
            if encodingType != 2:
                return 'API Error 0006: The encoding type must be 2 because that is the only one this program currently supports.'
            subject = subject.decode('base64')
            message = message.decode('base64')
            status, addressVersionNumber, streamNumber, toRipe = decodeAddress(
                toAddress)
            if status != 'success':
                with shared.printLock:
                    print 'API Error 0007: Could not decode address:', toAddress, ':', status

                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + toAddress
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: ' + toAddress
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + toAddress
                return 'API Error 0007: Could not decode address: ' + toAddress + ' : ' + status
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                return 'API Error 0011: The address version number currently must be 2 or 3. Others aren\'t supported. Check the toAddress.'
            if streamNumber != 1:
                return 'API Error 0012: The stream number must be 1. Others aren\'t supported. Check the toAddress.'
            status, addressVersionNumber, streamNumber, fromRipe = decodeAddress(
                fromAddress)
            if status != 'success':
                with shared.printLock:
                    print 'API Error 0007: Could not decode address:', fromAddress, ':', status

                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + fromAddress
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: ' + fromAddress
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + fromAddress
                return 'API Error 0007: Could not decode address: ' + fromAddress + ' : ' + status
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                return 'API Error 0011: The address version number currently must be 2 or 3. Others aren\'t supported. Check the fromAddress.'
            if streamNumber != 1:
                return 'API Error 0012: The stream number must be 1. Others aren\'t supported. Check the fromAddress.'
            toAddress = addBMIfNotPresent(toAddress)
            fromAddress = addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = shared.config.getboolean(
                    fromAddress, 'enabled')
            except:
                return 'API Error 0013: Could not find your fromAddress in the keys.dat file.'
            if not fromAddressEnabled:
                return 'API Error 0014: Your fromAddress is disabled. Cannot send.'

            ackdata = OpenSSL.rand(32)

            t = ('', toAddress, toRipe, fromAddress, subject, message, ackdata, int(
                time.time()), 'msgqueued', 1, 1, 'sent', 2)
            helper_sent.insert(t)

            toLabel = ''
            t = (toAddress,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''select label from addressbook where address=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn != []:
                for row in queryreturn:
                    toLabel, = row
            # apiSignalQueue.put(('displayNewSentMessage',(toAddress,toLabel,fromAddress,subject,message,ackdata)))
            shared.UISignalQueue.put(('displayNewSentMessage', (
                toAddress, toLabel, fromAddress, subject, message, ackdata)))

            shared.workerQueue.put(('sendmessage', toAddress))

            return ackdata.encode('hex')

        elif method == 'sendBroadcast':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            if len(params) == 3:
                fromAddress, subject, message = params
                encodingType = 2
            elif len(params) == 4:
                fromAddress, subject, message, encodingType = params
            if encodingType != 2:
                return 'API Error 0006: The encoding type must be 2 because that is the only one this program currently supports.'
            subject = subject.decode('base64')
            message = message.decode('base64')

            status, addressVersionNumber, streamNumber, fromRipe = decodeAddress(
                fromAddress)
            if status != 'success':
                with shared.printLock:
                    print 'API Error 0007: Could not decode address:', fromAddress, ':', status

                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + fromAddress
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: ' + fromAddress
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + fromAddress
                return 'API Error 0007: Could not decode address: ' + fromAddress + ' : ' + status
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                return 'API Error 0011: the address version number currently must be 2 or 3. Others aren\'t supported. Check the fromAddress.'
            if streamNumber != 1:
                return 'API Error 0012: the stream number must be 1. Others aren\'t supported. Check the fromAddress.'
            fromAddress = addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = shared.config.getboolean(
                    fromAddress, 'enabled')
            except:
                return 'API Error 0013: could not find your fromAddress in the keys.dat file.'
            ackdata = OpenSSL.rand(32)
            toAddress = '[Broadcast subscribers]'
            ripe = ''


            t = ('', toAddress, ripe, fromAddress, subject, message, ackdata, int(
                time.time()), 'broadcastqueued', 1, 1, 'sent', 2)
            helper_sent.insert(t)

            toLabel = '[Broadcast subscribers]'
            shared.UISignalQueue.put(('displayNewSentMessage', (
                toAddress, toLabel, fromAddress, subject, message, ackdata)))
            shared.workerQueue.put(('sendbroadcast', ''))

            return ackdata.encode('hex')
        elif method == 'getStatus':
            if len(params) != 1:
                return 'API Error 0000: I need one parameter!'
            ackdata, = params
            if len(ackdata) != 64:
                return 'API Error 0015: The length of ackData should be 32 bytes (encoded in hex thus 64 characters).'
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT status FROM sent where ackdata=?''')
            shared.sqlSubmitQueue.put((ackdata.decode('hex'),))
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn == []:
                return 'notfound'
            for row in queryreturn:
                status, = row
                return status
        elif method == 'addSubscription':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            if len(params) == 1:
                address, = params
                label == ''
            if len(params) == 2:
                address, label = params
                label = label.decode('base64')
                try:
                    unicode(label, 'utf-8')
                except:
                    return 'API Error 0017: Label is not valid UTF-8 data.'
            if len(params) > 2:
                return 'API Error 0000: I need either 1 or 2 parameters!'
            address = addBMIfNotPresent(address)
            status, addressVersionNumber, streamNumber, toRipe = decodeAddress(
                address)
            if status != 'success':
                with shared.printLock:
                    print 'API Error 0007: Could not decode address:', address, ':', status

                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + address
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: ' + address
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + address
                return 'API Error 0007: Could not decode address: ' + address + ' : ' + status
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                return 'API Error 0011: The address version number currently must be 2 or 3. Others aren\'t supported.'
            if streamNumber != 1:
                return 'API Error 0012: The stream number must be 1. Others aren\'t supported.'
            # First we must check to see if the address is already in the
            # subscriptions list.
            shared.sqlLock.acquire()
            t = (address,)
            shared.sqlSubmitQueue.put(
                '''select * from subscriptions where address=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn != []:
                return 'API Error 0016: You are already subscribed to that address.'
            t = (label, address, True)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO subscriptions VALUES (?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            shared.reloadBroadcastSendersForWhichImWatching()
            shared.UISignalQueue.put(('rerenderInboxFromLabels', ''))
            shared.UISignalQueue.put(('rerenderSubscriptions', ''))
            return 'Added subscription.'

        elif method == 'deleteSubscription':
            if len(params) != 1:
                return 'API Error 0000: I need 1 parameter!'
            address, = params
            address = addBMIfNotPresent(address)
            t = (address,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''DELETE FROM subscriptions WHERE address=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            shared.reloadBroadcastSendersForWhichImWatching()
            shared.UISignalQueue.put(('rerenderInboxFromLabels', ''))
            shared.UISignalQueue.put(('rerenderSubscriptions', ''))
            return 'Deleted subscription if it existed.'
        elif method == 'listSubscriptions':
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT label, address, enabled FROM subscriptions''')
            shared.sqlSubmitQueue.put('')
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"subscriptions":['
            for row in queryreturn:
                label, address, enabled = row
                label = shared.fixPotentiallyInvalidUTF8Data(label)
                if len(data) > 20:
                    data += ','
                data += json.dumps({'label':label.encode('base64'), 'address': address, 'enabled': enabled == 1}, indent=4, separators=(',',': '))
            data += ']}'
            return data
        elif method == 'clientStatus':
            return '{ "networkConnections" : "%s" }' % str(len(shared.connectedHostsList))
        else:
            return 'API Error 0020: Invalid method: %s' % method

# This thread, of which there is only one, runs the API.


class singleAPI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        se = SimpleXMLRPCServer((shared.config.get('bitmessagesettings', 'apiinterface'), shared.config.getint(
            'bitmessagesettings', 'apiport')), MySimpleXMLRPCRequestHandler, True, True)
        se.register_introspection_functions()
        se.serve_forever()

selfInitiatedConnections = {}
    # This is a list of current connections (the thread pointers at least)





if shared.useVeryEasyProofOfWorkForTesting:
    shared.networkDefaultProofOfWorkNonceTrialsPerByte = int(
        shared.networkDefaultProofOfWorkNonceTrialsPerByte / 16)
    shared.networkDefaultPayloadLengthExtraBytes = int(
        shared.networkDefaultPayloadLengthExtraBytes / 7000)

if __name__ == "__main__":
    # is the application already running?  If yes then exit.
    thisapp = singleton.singleinstance()

    signal.signal(signal.SIGINT, helper_generic.signal_handler)
    # signal.signal(signal.SIGINT, signal.SIG_DFL)

    helper_bootstrap.knownNodes()
    # Start the address generation thread
    addressGeneratorThread = addressGenerator()
    addressGeneratorThread.daemon = True  # close the main program even if there are threads left
    addressGeneratorThread.start()

    # Start the thread that calculates POWs
    singleWorkerThread = singleWorker()
    singleWorkerThread.daemon = True  # close the main program even if there are threads left
    singleWorkerThread.start()

    # Start the SQL thread
    sqlLookup = sqlThread()
    sqlLookup.daemon = False  # DON'T close the main program even if there are threads left. The closeEvent should command this thread to exit gracefully.
    sqlLookup.start()

    # Start the cleanerThread
    singleCleanerThread = singleCleaner()
    singleCleanerThread.daemon = True  # close the main program even if there are threads left
    singleCleanerThread.start()

    shared.reloadMyAddressHashes()
    shared.reloadBroadcastSendersForWhichImWatching()

    if shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
        try:
            apiNotifyPath = shared.config.get(
                'bitmessagesettings', 'apinotifypath')
        except:
            apiNotifyPath = ''
        if apiNotifyPath != '':
            with shared.printLock:
                print 'Trying to call', apiNotifyPath

            call([apiNotifyPath, "startingUp"])
        singleAPIThread = singleAPI()
        singleAPIThread.daemon = True  # close the main program even if there are threads left
        singleAPIThread.start()

    connectToStream(1)

    singleListenerThread = singleListener()
    singleListenerThread.setup(selfInitiatedConnections)
    singleListenerThread.daemon = True  # close the main program even if there are threads left
    singleListenerThread.start()

    if not shared.safeConfigGetBoolean('bitmessagesettings', 'daemon'):
        try:
            from PyQt4 import QtCore, QtGui
        except Exception as err:
            print 'PyBitmessage requires PyQt unless you want to run it as a daemon and interact with it using the API. You can download PyQt from http://www.riverbankcomputing.com/software/pyqt/download   or by searching Google for \'PyQt Download\'. If you want to run in daemon mode, see https://bitmessage.org/wiki/Daemon'
            print 'Error message:', err
            os._exit(0)

        import bitmessageqt
        bitmessageqt.run()
    else:
        shared.config.remove_option('bitmessagesettings', 'dontconnect')
        with shared.printLock:
            print 'Running as a daemon. You can use Ctrl+C to exit.'

        while True:
            time.sleep(20)

# So far, the creation of and management of the Bitmessage protocol and this
# client is a one-man operation. Bitcoin tips are quite appreciated.
# 1H5XaDA6fYENLbknwZyjiYXYPQaFjjLX2u
