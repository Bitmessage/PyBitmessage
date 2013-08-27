#!/usr/bin/env python2.7
# Copyright (c) 2012 Jonathan Warren
# Copyright (c) 2012 The Bitmessage developers
# Distributed under the MIT/X11 software license. See the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Right now, PyBitmessage only support connecting to stream 1. It doesn't
# yet contain logic to expand into further streams.

# The software version variable is now held in shared.py

import signal  # Used to capture a Ctrl-C keypress so that Bitmessage can shutdown gracefully.
# The next 3 are used for the API
from SimpleXMLRPCServer import *
import json
import singleton
import os

# OSX python version check
import sys
if sys.platform == 'darwin':
    if float("{1}.{2}".format(*sys.version_info)) < 7.5:
        print "You should use python 2.7.5 or greater."
        print "Your version: {0}.{1}.{2}".format(*sys.version_info)
        sys.exit(0)

# Classes
from class_sqlThread import *
from class_singleCleaner import *
from class_singleWorker import *
from class_outgoingSynSender import *
from class_singleListener import *
from class_addressGenerator import *
from debug import logger

# Helper Functions
import helper_bootstrap

import sys
if sys.platform == 'darwin':
    if float("{1}.{2}".format(*sys.version_info)) < 7.5:
        logger.critical("You should use python 2.7.5 or greater. Your version: %s", "{0}.{1}.{2}".format(*sys.version_info))
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


class APIError(Exception):
    def __init__(self, error_number, error_message):
        self.error_number = error_number
        self.error_message = error_message
    def __str__(self):
        return "API Error %04i: %s" % (self.error_number, self.error_message)

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
            logger.warn('Authentication failed because header lacks Authentication field')
            time.sleep(2)
            return False

        return False

    def _decode(self, text, decode_type):
        try:
            return text.decode(decode_type)
        except TypeError as e:
            raise APIError(22, "Decode error - " + str(e))
        
    def _handle_request(self, method, params):
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
                raise APIError(0, 'I need parameters!')
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
                raise APIError(0, 'Too many parameters!')
            label = self._decode(label, "base64")
            try:
                unicode(label, 'utf-8')
            except:
                raise APIError(17, 'Label is not valid UTF-8 data.')
            shared.apiAddressGeneratorReturnQueue.queue.clear()
            streamNumberForAddress = 1
            shared.addressGeneratorQueue.put((
                'createRandomAddress', 3, streamNumberForAddress, label, 1, "", eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes))
            return shared.apiAddressGeneratorReturnQueue.get()
        elif method == 'createDeterministicAddresses':
            if len(params) == 0:
                raise APIError(0, 'I need parameters!')
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
                raise APIError(0, 'Too many parameters!')
            if len(passphrase) == 0:
                raise APIError(1, 'The specified passphrase is blank.')
            passphrase = self._decode(passphrase, "base64")
            if addressVersionNumber == 0:  # 0 means "just use the proper addressVersionNumber"
                addressVersionNumber = 3
            if addressVersionNumber != 3:
                raise APIError(2,'The address version number currently must be 3 (or 0 which means auto-select). ' + addressVersionNumber + ' isn\'t supported.')
            if streamNumber == 0:  # 0 means "just use the most available stream"
                streamNumber = 1
            if streamNumber != 1:
                raise APIError(3,'The stream number must be 1 (or 0 which means auto-select). Others aren\'t supported.')
            if numberOfAddresses == 0:
                raise APIError(4, 'Why would you ask me to generate 0 addresses for you?')
            if numberOfAddresses > 999:
                raise APIError(5, 'You have (accidentally?) specified too many addresses to make. Maximum 999. This check only exists to prevent mischief; if you really want to create more addresses than this, contact the Bitmessage developers and we can modify the check or you can do it yourself by searching the source code for this message.')
            shared.apiAddressGeneratorReturnQueue.queue.clear()
            logger.debug('Requesting that the addressGenerator create %s addresses.', numberOfAddresses)
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
                raise APIError(0, 'I need exactly 3 parameters.')
            passphrase, addressVersionNumber, streamNumber = params
            numberOfAddresses = 1
            eighteenByteRipe = False
            if len(passphrase) == 0:
                raise APIError(1, 'The specified passphrase is blank.')
            passphrase = self._decode(passphrase, "base64")
            if addressVersionNumber != 3:
                raise APIError(2, 'The address version number currently must be 3. ' + addressVersionNumber + ' isn\'t supported.')
            if streamNumber != 1:
                raise APIError(3, ' The stream number must be 1. Others aren\'t supported.')
            shared.apiAddressGeneratorReturnQueue.queue.clear()
            logger.debug('Requesting that the addressGenerator create %s addresses.', numberOfAddresses)
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
                raise APIError(0, 'I need parameters!')
            msgid = self._decode(params[0], "hex")
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
                raise APIError(0, 'I need parameters!')
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
                raise APIError(0, 'I need parameters!')
            msgid = self._decode(params[0], "hex")
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
                raise APIError(0, 'I need parameters!')
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
                raise APIError(0, 'I need parameters!')
            ackData = self._decode(params[0], "hex")
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
                raise APIError(0, 'I need parameters!')
            msgid = self._decode(params[0], "hex")
            
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
                raise APIError(0, 'I need parameters!')
            msgid = self._decode(params[0], "hex")
            helper_inbox.trash(msgid)
            return 'Trashed inbox message (assuming message existed).'
        elif method == 'trashSentMessage':
            if len(params) == 0:
                raise APIError(0, 'I need parameters!')
            msgid = self._decode(params[0], "hex")
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
                raise APIError(0, 'I need parameters!')
            elif len(params) == 4:
                toAddress, fromAddress, subject, message = params
                encodingType = 2
            elif len(params) == 5:
                toAddress, fromAddress, subject, message, encodingType = params
            if encodingType != 2:
                raise APIError(6, 'The encoding type must be 2 because that is the only one this program currently supports.')
            subject = self._decode(subject, "base64")
            message = self._decode(message, "base64")
            status, addressVersionNumber, streamNumber, toRipe = decodeAddress(
                toAddress)
            if status != 'success':
                logger.warn('API Error 0007: Could not decode address %s. Status: %s.', toAddress, status)

                if status == 'checksumfailed':
                    raise APIError(8, 'Checksum failed for address: ' + toAddress)
                if status == 'invalidcharacters':
                    raise APIError(9, 'Invalid characters in address: ' + toAddress)
                if status == 'versiontoohigh':
                    raise APIError(10, 'Address version number too high (or zero) in address: ' + toAddress)
                raise APIError(7, 'Could not decode address: ' + toAddress + ' : ' + status)
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                raise APIError(11, 'The address version number currently must be 2 or 3. Others aren\'t supported. Check the toAddress.')
            if streamNumber != 1:
                raise APIError(12, 'The stream number must be 1. Others aren\'t supported. Check the toAddress.')
            status, addressVersionNumber, streamNumber, fromRipe = decodeAddress(
                fromAddress)
            if status != 'success':
                logger.warn('API Error 0007: Could not decode address %s. Status: %s.', fromAddress, status)

                if status == 'checksumfailed':
                    raise APIError(8, 'Checksum failed for address: ' + fromAddress)
                if status == 'invalidcharacters':
                    raise APIError(9, 'Invalid characters in address: ' + fromAddress)
                if status == 'versiontoohigh':
                    raise APIError(10, 'Address version number too high (or zero) in address: ' + fromAddress)
                raise APIError(7, 'Could not decode address: ' + fromAddress + ' : ' + status)
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                raise APIError(11, 'The address version number currently must be 2 or 3. Others aren\'t supported. Check the fromAddress.')
            if streamNumber != 1:
                raise APIError(12, 'The stream number must be 1. Others aren\'t supported. Check the fromAddress.')
            toAddress = addBMIfNotPresent(toAddress)
            fromAddress = addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = shared.config.getboolean(
                    fromAddress, 'enabled')
            except:
                raise APIError(13, 'Could not find your fromAddress in the keys.dat file.')
            if not fromAddressEnabled:
                raise APIError(14, 'Your fromAddress is disabled. Cannot send.')

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
                raise APIError(0, 'I need parameters!')
            if len(params) == 3:
                fromAddress, subject, message = params
                encodingType = 2
            elif len(params) == 4:
                fromAddress, subject, message, encodingType = params
            if encodingType != 2:
                raise APIError(6, 'The encoding type must be 2 because that is the only one this program currently supports.')
            subject = self._decode(subject, "base64")
            message = self._decode(message, "base64")

            status, addressVersionNumber, streamNumber, fromRipe = decodeAddress(
                fromAddress)
            if status != 'success':
                logger.warn('API Error 0007: Could not decode address %s. Status: %s.', fromAddress, status)

                if status == 'checksumfailed':
                    raise APIError(8, 'Checksum failed for address: ' + fromAddress)
                if status == 'invalidcharacters':
                    raise APIError(9, 'Invalid characters in address: ' + fromAddress)
                if status == 'versiontoohigh':
                    raise APIError(10, 'Address version number too high (or zero) in address: ' + fromAddress)
                raise APIError(7, 'Could not decode address: ' + fromAddress + ' : ' + status)
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                raise APIError(11, 'the address version number currently must be 2 or 3. Others aren\'t supported. Check the fromAddress.')
            if streamNumber != 1:
                raise APIError(12, 'the stream number must be 1. Others aren\'t supported. Check the fromAddress.')
            fromAddress = addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = shared.config.getboolean(
                    fromAddress, 'enabled')
            except:
                raise APIError(13, 'could not find your fromAddress in the keys.dat file.')
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
                raise APIError(0, 'I need one parameter!')
            ackdata, = params
            if len(ackdata) != 64:
                raise APIError(15, 'The length of ackData should be 32 bytes (encoded in hex thus 64 characters).')
            ackdata = self._decode(ackdata, "hex")
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT status FROM sent where ackdata=?''')
            shared.sqlSubmitQueue.put((ackdata,))
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn == []:
                return 'notfound'
            for row in queryreturn:
                status, = row
                return status
        elif method == 'addSubscription':
            if len(params) == 0:
                raise APIError(0, 'I need parameters!')
            if len(params) == 1:
                address, = params
                label == ''
            if len(params) == 2:
                address, label = params
                label = self._decode(label, "base64")
                try:
                    unicode(label, 'utf-8')
                except:
                    raise APIError(17, 'Label is not valid UTF-8 data.')
            if len(params) > 2:
                raise APIError(0, 'I need either 1 or 2 parameters!')
            address = addBMIfNotPresent(address)
            status, addressVersionNumber, streamNumber, toRipe = decodeAddress(
                address)
            if status != 'success':
                logger.warn('API Error 0007: Could not decode address %s. Status: %s.', address, status)

                if status == 'checksumfailed':
                    raise APIError(8, 'Checksum failed for address: ' + address)
                if status == 'invalidcharacters':
                    raise APIError(9, 'Invalid characters in address: ' + address)
                if status == 'versiontoohigh':
                    raise APIError(10, 'Address version number too high (or zero) in address: ' + address)
                raise APIError(7, 'Could not decode address: ' + address + ' : ' + status)
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                raise APIError(11, 'The address version number currently must be 2 or 3. Others aren\'t supported.')
            if streamNumber != 1:
                raise APIError(12, 'The stream number must be 1. Others aren\'t supported.')
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
                raise APIError(16, 'You are already subscribed to that address.')
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
                raise APIError(0, 'I need 1 parameter!')
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
        elif method == 'disseminatePreEncryptedMsg':
            # The device issuing this command to PyBitmessage supplies a msg object that has
            # already been encrypted and had the necessary proof of work done for it to be
            # disseminated to the rest of the Bitmessage network. PyBitmessage accepts this msg
            # object and sends it out to the rest of the Bitmessage network as if it had generated the
            # message itself. Please do not yet add this to the api doc.
            if len(params) != 1:
                raise APIError(0, 'I need 1 parameter!')
            encryptedPayload, = params
            encryptedPayload = self._decode(encryptedPayload, "hex")
            toStreamNumber = decodeVarint(encryptedPayload[16:26])[0]
            inventoryHash = calculateInventoryHash(encryptedPayload)
            objectType = 'msg'
            shared.inventory[inventoryHash] = (
                objectType, toStreamNumber, encryptedPayload, int(time.time()))
            with shared.printLock:
                print 'Broadcasting inv for msg(API disseminatePreEncryptedMsg command):', inventoryHash.encode('hex')
            shared.broadcastToSendDataQueues((
                toStreamNumber, 'sendinv', inventoryHash))
        elif method == 'disseminatePubkey':
            # The device issuing this command to PyBitmessage supplies a pubkey object that has
            # already had the necessary proof of work done for it to be disseminated to the rest of the 
            # Bitmessage network. PyBitmessage accepts this pubkey object and sends it out to the 
            # rest of the Bitmessage network as if it had generated the pubkey object itself. Please
            # do not yet add this to the api doc.
            if len(params) != 1:
                raise APIError(0, 'I need 1 parameter!')
            payload, = params
            payload = self._decode(payload, "hex")
            pubkeyReadPosition = 8 # bypass the nonce
            if payload[pubkeyReadPosition:pubkeyReadPosition+4] == '\x00\x00\x00\x00': # if this pubkey uses 8 byte time
                pubkeyReadPosition += 8
            else:
                pubkeyReadPosition += 4
            addressVersion, addressVersionLength = decodeVarint(payload[pubkeyReadPosition:pubkeyReadPosition+10])
            pubkeyReadPosition += addressVersionLength
            pubkeyStreamNumber = decodeVarint(payload[pubkeyReadPosition:pubkeyReadPosition+10])[0]
            inventoryHash = calculateInventoryHash(payload)
            objectType = 'pubkey'
            shared.inventory[inventoryHash] = (
                objectType, pubkeyStreamNumber, payload, int(time.time()))
            with shared.printLock:
                print 'broadcasting inv within API command disseminatePubkey with hash:', inventoryHash.encode('hex')
            shared.broadcastToSendDataQueues((
                streamNumber, 'sendinv', inventoryHash))
        elif method == 'getMessageDataByDestinationHash':
            # Method will eventually be used by a particular Android app to 
            # select relevant messages. Do not yet add this to the api
            # doc.
            
            if len(params) != 1:
                raise APIError(0, 'I need 1 parameter!')
            requestedHash, = params
            if len(requestedHash) != 40:
                raise APIError(19, 'The length of hash should be 20 bytes (encoded in hex thus 40 characters).')
            requestedHash = self._decode(requestedHash, "hex")
            
            # This is not a particularly commonly used API function. Before we 
            # use it we'll need to fill out a field in our inventory database 
            # which is blank by default (first20bytesofencryptedmessage). 
            parameters = ''
            with shared.sqlLock:
                shared.sqlSubmitQueue.put('''SELECT hash, payload FROM inventory WHERE first20bytesofencryptedmessage = '' and objecttype = 'msg' ; ''')
                shared.sqlSubmitQueue.put(parameters)
                queryreturn = shared.sqlReturnQueue.get()
            
                for row in queryreturn:
                    hash, payload = row
                    readPosition = 16 # Nonce length + time length
                    readPosition += decodeVarint(payload[readPosition:readPosition+10])[1] # Stream Number length
                    t = (payload[readPosition:readPosition+20],hash)
                    shared.sqlSubmitQueue.put('''UPDATE inventory SET first20bytesofencryptedmessage=? WHERE hash=?; ''')
                    shared.sqlSubmitQueue.put(t)
                    shared.sqlReturnQueue.get()        
                
            parameters = (requestedHash,)
            with shared.sqlLock:
                shared.sqlSubmitQueue.put('commit')
                shared.sqlSubmitQueue.put('''SELECT payload FROM inventory WHERE first20bytesofencryptedmessage = ?''')
                shared.sqlSubmitQueue.put(parameters)
                queryreturn = shared.sqlReturnQueue.get()
            data = '{"receivedMessageDatas":['
            for row in queryreturn:
                payload, = row
                if len(data) > 25:
                    data += ','
                data += json.dumps({'data':payload.encode('hex')}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getPubkeyByHash':
            # Method will eventually be used by a particular Android app to 
            # retrieve pubkeys. Please do not yet add this to the api docs.
            if len(params) != 1:
                raise APIError(0, 'I need 1 parameter!')
            requestedHash, = params
            if len(requestedHash) != 40:
                raise APIError(19, 'The length of hash should be 20 bytes (encoded in hex thus 40 characters).')
            requestedHash = self._decode(requestedHash, "hex")
            parameters = (requestedHash,)
            with shared.sqlLock:
                shared.sqlSubmitQueue.put('''SELECT transmitdata FROM pubkeys WHERE hash = ? ; ''')
                shared.sqlSubmitQueue.put(parameters)
                queryreturn = shared.sqlReturnQueue.get()
            data = '{"pubkey":['
            for row in queryreturn:
                transmitdata, = row
                data += json.dumps({'data':transmitdata.encode('hex')}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'clientStatus':
            if len(shared.connectedHostsList) == 0:
                networkStatus = 'notConnected'
            elif len(shared.connectedHostsList) > 0 and not shared.clientHasReceivedIncomingConnections:
                networkStatus = 'connectedButHaveNotReceivedIncomingConnections'
            else:
                networkStatus = 'connectedAndReceivingIncomingConnections'
            return json.dumps({'networkConnections':len(shared.connectedHostsList),'numberOfMessagesProcessed':shared.numberOfMessagesProcessed, 'numberOfBroadcastsProcessed':shared.numberOfBroadcastsProcessed, 'numberOfPubkeysProcessed':shared.numberOfPubkeysProcessed, 'networkStatus':networkStatus}, indent=4, separators=(',', ': '))
        else:
            raise APIError(20, 'Invalid method: %s' % method)

    def _dispatch(self, method, params):
        self.cookies = []

        validuser = self.APIAuthenticateClient()
        if not validuser:
            time.sleep(2)
            return "RPC Username or password incorrect or HTTP header lacks authentication at all."

        try:
            return self._handle_request(method, params)
        except APIError as e:
            return str(e)
        except Exception as e:
            logger.exception(e)
            return "API Error 0021: Unexpected API Failure - %s" % str(e)

# This thread, of which there is only one, runs the API.


class singleAPI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        se = SimpleXMLRPCServer((shared.config.get('bitmessagesettings', 'apiinterface'), shared.config.getint(
            'bitmessagesettings', 'apiport')), MySimpleXMLRPCRequestHandler, True, True)
        se.register_introspection_functions()
        se.serve_forever()

# This is a list of current connections (the thread pointers at least)
selfInitiatedConnections = {}


if shared.useVeryEasyProofOfWorkForTesting:
    shared.networkDefaultProofOfWorkNonceTrialsPerByte = int(
        shared.networkDefaultProofOfWorkNonceTrialsPerByte / 16)
    shared.networkDefaultPayloadLengthExtraBytes = int(
        shared.networkDefaultPayloadLengthExtraBytes / 7000)

class Main:
    def start(self, daemon=False):
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

        if daemon == False and shared.safeConfigGetBoolean('bitmessagesettings', 'daemon') == False:
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

            if daemon:
                with shared.printLock:
                    print 'Running as a daemon. The main program should exit this thread.'
            else:
                with shared.printLock:
                    print 'Running as a daemon. You can use Ctrl+C to exit.'
                while True:
                    time.sleep(20)
            
    def stop(self):
        with shared.printLock:
            print 'Stopping Bitmessage Deamon.'
        shared.doCleanShutdown()
        
        
    def getApiAddress(self):
        if not shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
            return None
        address = shared.config.get('bitmessagesettings', 'apiinterface')
        port = shared.config.getint('bitmessagesettings', 'apiport')
        return {'address':address,'port':port}
            
if __name__ == "__main__":
    mainprogram = Main()
    mainprogram.start()

    
# So far, the creation of and management of the Bitmessage protocol and this
# client is a one-man operation. Bitcoin tips are quite appreciated.
# 1H5XaDA6fYENLbknwZyjiYXYPQaFjjLX2u
