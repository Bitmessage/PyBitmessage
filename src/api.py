# Copyright (c) 2012-2016 Jonathan Warren
# Copyright (c) 2012-2018 The Bitmessage developers

"""
This is not what you run to run the Bitmessage API. Instead, enable the API
( https://bitmessage.org/wiki/API ) and optionally enable daemon mode
( https://bitmessage.org/wiki/Daemon ) then run bitmessagemain.py.
"""

import base64
import hashlib
import json
import socket
import threading
import time
from binascii import hexlify, unhexlify
from random import randint
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer
from struct import pack
import errno
import Queue

import shared
from addresses import (
    decodeAddress, addBMIfNotPresent, decodeVarint,
    calculateInventoryHash, varintDecodeError)
from bmconfigparser import BMConfigParser
import defaults
import helper_inbox
import helper_sent
import helper_threading
import helper_random

import state
import queues
import shutdown
import network.stats
import protocol

# Classes
from helper_sql import sqlQuery, sqlExecute, SqlBulkExecute, sqlStoredProcedure
from helper_ackPayload import genAckPayload
from debug import logger
from inventory import Inventory
from version import softwareVersion

str_chan = '[chan]'

queuedRawObjects = {}

class APIError(Exception):
    def __init__(self, error_number, error_message):
        super(APIError, self).__init__()
        self.error_number = error_number
        self.error_message = error_message

    def __str__(self):
        return "API Error %04i: %s" % (self.error_number, self.error_message)


class StoppableXMLRPCServer(SimpleXMLRPCServer):
    allow_reuse_address = True

    def serve_forever(self):
        while state.shutdown == 0:
            self.handle_request()


# This is one of several classes that constitute the API
# This class was written by Vaibhav Bhatia.
# Modified by Jonathan Warren (Atheros).
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
            enctype, encstr = self.headers.get('Authorization').split()
            emailid, password = encstr.decode('base64').split(':')
            return (
                emailid ==
                BMConfigParser().get('bitmessagesettings', 'apiusername')
                and password ==
                BMConfigParser().get('bitmessagesettings', 'apipassword')
            )
        else:
            logger.warning(
                'Authentication failed because header lacks'
                ' Authentication field')
            time.sleep(2)
            return False

        return False

    def _decode(self, text, decode_type):
        try:
            if decode_type == 'hex':
                return unhexlify(text)
            elif decode_type == 'base64':
                return base64.b64decode(text)
        except Exception as e:
            raise APIError(
                22, "Decode error - %s. Had trouble while decoding string: %r"
                % (e, text)
            )

    def _verifyAddress(self, address):
        status, addressVersionNumber, streamNumber, ripe = \
            decodeAddress(address)
        if status != 'success':
            logger.warning(
                'API Error 0007: Could not decode address %s. Status: %s.',
                address, status
            )

            if status == 'checksumfailed':
                raise APIError(8, 'Checksum failed for address: ' + address)
            if status == 'invalidcharacters':
                raise APIError(9, 'Invalid characters in address: ' + address)
            if status == 'versiontoohigh':
                raise APIError(
                    10,
                    'Address version number too high (or zero) in address: '
                    + address
                )
            if status == 'varintmalformed':
                raise APIError(26, 'Malformed varint in address: ' + address)
            raise APIError(
                7, 'Could not decode address: %s : %s' % (address, status))
        if addressVersionNumber < 2 or addressVersionNumber > 4:
            raise APIError(
                11, 'The address version number currently must be 2, 3 or 4.'
                ' Others aren\'t supported. Check the address.'
            )
        if streamNumber != 1:
            raise APIError(
                12, 'The stream number must be 1. Others aren\'t supported.'
                ' Check the address.'
            )

        return (status, addressVersionNumber, streamNumber, ripe)

    # Request Handlers

    def HandleListAddresses(self, method):
        data = '{"addresses":['
        for addressInKeysFile in BMConfigParser().addresses():
            status, addressVersionNumber, streamNumber, hash01 = decodeAddress(
                addressInKeysFile)
            if len(data) > 20:
                data += ','
            if BMConfigParser().has_option(addressInKeysFile, 'chan'):
                chan = BMConfigParser().getboolean(addressInKeysFile, 'chan')
            else:
                chan = False
            label = BMConfigParser().get(addressInKeysFile, 'label')
            if method == 'listAddresses2':
                label = base64.b64encode(label)
            data += json.dumps({
                'label': label,
                'address': addressInKeysFile,
                'stream': streamNumber,
                'enabled':
                BMConfigParser().getboolean(addressInKeysFile, 'enabled'),
                'chan': chan
                }, indent=4, separators=(',', ': '))
        data += ']}'
        return data

    def HandleListAddressBookEntries(self, params):
        if len(params) == 1:
            label, = params
            label = self._decode(label, "base64")
            queryreturn = sqlQuery(
                "SELECT label, address from addressbook WHERE label = ?",
                label)
        elif len(params) > 1:
            raise APIError(0, "Too many paremeters, max 1")
        else:
            queryreturn = sqlQuery("SELECT label, address from addressbook")
        data = '{"addresses":['
        for row in queryreturn:
            label, address = row
            label = shared.fixPotentiallyInvalidUTF8Data(label)
            if len(data) > 20:
                data += ','
            data += json.dumps({
                'label': base64.b64encode(label),
                'address': address}, indent=4, separators=(',', ': '))
        data += ']}'
        return data

    def HandleAddAddressBookEntry(self, params):
        if len(params) != 2:
            raise APIError(0, "I need label and address")
        address, label = params
        label = self._decode(label, "base64")
        address = addBMIfNotPresent(address)
        self._verifyAddress(address)
        queryreturn = sqlQuery(
            "SELECT address FROM addressbook WHERE address=?", address)
        if queryreturn != []:
            raise APIError(
                16, 'You already have this address in your address book.')

        sqlExecute("INSERT INTO addressbook VALUES(?,?)", label, address)
        queues.UISignalQueue.put(('rerenderMessagelistFromLabels', ''))
        queues.UISignalQueue.put(('rerenderMessagelistToLabels', ''))
        queues.UISignalQueue.put(('rerenderAddressBook', ''))
        return "Added address %s to address book" % address

    def HandleDeleteAddressBookEntry(self, params):
        if len(params) != 1:
            raise APIError(0, "I need an address")
        address, = params
        address = addBMIfNotPresent(address)
        self._verifyAddress(address)
        sqlExecute('DELETE FROM addressbook WHERE address=?', address)
        queues.UISignalQueue.put(('rerenderMessagelistFromLabels', ''))
        queues.UISignalQueue.put(('rerenderMessagelistToLabels', ''))
        queues.UISignalQueue.put(('rerenderAddressBook', ''))
        return "Deleted address book entry for %s if it existed" % address

    def HandleCreateRandomAddress(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        elif len(params) == 1:
            label, = params
            eighteenByteRipe = False
            nonceTrialsPerByte = BMConfigParser().get(
                'bitmessagesettings', 'defaultnoncetrialsperbyte')
            payloadLengthExtraBytes = BMConfigParser().get(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes')
        elif len(params) == 2:
            label, eighteenByteRipe = params
            nonceTrialsPerByte = BMConfigParser().get(
                'bitmessagesettings', 'defaultnoncetrialsperbyte')
            payloadLengthExtraBytes = BMConfigParser().get(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes')
        elif len(params) == 3:
            label, eighteenByteRipe, totalDifficulty = params
            nonceTrialsPerByte = int(
                defaults.networkDefaultProofOfWorkNonceTrialsPerByte
                * totalDifficulty)
            payloadLengthExtraBytes = BMConfigParser().get(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes')
        elif len(params) == 4:
            label, eighteenByteRipe, totalDifficulty, \
                smallMessageDifficulty = params
            nonceTrialsPerByte = int(
                defaults.networkDefaultProofOfWorkNonceTrialsPerByte
                * totalDifficulty)
            payloadLengthExtraBytes = int(
                defaults.networkDefaultPayloadLengthExtraBytes
                * smallMessageDifficulty)
        else:
            raise APIError(0, 'Too many parameters!')
        label = self._decode(label, "base64")
        try:
            unicode(label, 'utf-8')
        except:
            raise APIError(17, 'Label is not valid UTF-8 data.')
        queues.apiAddressGeneratorReturnQueue.queue.clear()
        streamNumberForAddress = 1
        queues.addressGeneratorQueue.put((
            'createRandomAddress', 4, streamNumberForAddress, label, 1, "",
            eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes
        ))
        return queues.apiAddressGeneratorReturnQueue.get()

    def HandleCreateDeterministicAddresses(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        elif len(params) == 1:
            passphrase, = params
            numberOfAddresses = 1
            addressVersionNumber = 0
            streamNumber = 0
            eighteenByteRipe = False
            nonceTrialsPerByte = BMConfigParser().get(
                'bitmessagesettings', 'defaultnoncetrialsperbyte')
            payloadLengthExtraBytes = BMConfigParser().get(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes')
        elif len(params) == 2:
            passphrase, numberOfAddresses = params
            addressVersionNumber = 0
            streamNumber = 0
            eighteenByteRipe = False
            nonceTrialsPerByte = BMConfigParser().get(
                'bitmessagesettings', 'defaultnoncetrialsperbyte')
            payloadLengthExtraBytes = BMConfigParser().get(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes')
        elif len(params) == 3:
            passphrase, numberOfAddresses, addressVersionNumber = params
            streamNumber = 0
            eighteenByteRipe = False
            nonceTrialsPerByte = BMConfigParser().get(
                'bitmessagesettings', 'defaultnoncetrialsperbyte')
            payloadLengthExtraBytes = BMConfigParser().get(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes')
        elif len(params) == 4:
            passphrase, numberOfAddresses, addressVersionNumber, \
                streamNumber = params
            eighteenByteRipe = False
            nonceTrialsPerByte = BMConfigParser().get(
                'bitmessagesettings', 'defaultnoncetrialsperbyte')
            payloadLengthExtraBytes = BMConfigParser().get(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes')
        elif len(params) == 5:
            passphrase, numberOfAddresses, addressVersionNumber, \
                streamNumber, eighteenByteRipe = params
            nonceTrialsPerByte = BMConfigParser().get(
                'bitmessagesettings', 'defaultnoncetrialsperbyte')
            payloadLengthExtraBytes = BMConfigParser().get(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes')
        elif len(params) == 6:
            passphrase, numberOfAddresses, addressVersionNumber, \
                streamNumber, eighteenByteRipe, totalDifficulty = params
            nonceTrialsPerByte = int(
                defaults.networkDefaultProofOfWorkNonceTrialsPerByte
                * totalDifficulty)
            payloadLengthExtraBytes = BMConfigParser().get(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes')
        elif len(params) == 7:
            passphrase, numberOfAddresses, addressVersionNumber, \
                streamNumber, eighteenByteRipe, totalDifficulty, \
                smallMessageDifficulty = params
            nonceTrialsPerByte = int(
                defaults.networkDefaultProofOfWorkNonceTrialsPerByte
                * totalDifficulty)
            payloadLengthExtraBytes = int(
                defaults.networkDefaultPayloadLengthExtraBytes
                * smallMessageDifficulty)
        else:
            raise APIError(0, 'Too many parameters!')
        if len(passphrase) == 0:
            raise APIError(1, 'The specified passphrase is blank.')
        if not isinstance(eighteenByteRipe, bool):
            raise APIError(
                23, 'Bool expected in eighteenByteRipe, saw %s instead' %
                type(eighteenByteRipe))
        passphrase = self._decode(passphrase, "base64")
        # 0 means "just use the proper addressVersionNumber"
        if addressVersionNumber == 0:
            addressVersionNumber = 4
        if addressVersionNumber != 3 and addressVersionNumber != 4:
            raise APIError(
                2, 'The address version number currently must be 3, 4, or 0'
                ' (which means auto-select). %i isn\'t supported.' %
                addressVersionNumber)
        if streamNumber == 0:  # 0 means "just use the most available stream"
            streamNumber = 1
        if streamNumber != 1:
            raise APIError(
                3, 'The stream number must be 1 (or 0 which means'
                ' auto-select). Others aren\'t supported.')
        if numberOfAddresses == 0:
            raise APIError(
                4, 'Why would you ask me to generate 0 addresses for you?')
        if numberOfAddresses > 999:
            raise APIError(
                5, 'You have (accidentally?) specified too many addresses to'
                ' make. Maximum 999. This check only exists to prevent'
                ' mischief; if you really want to create more addresses than'
                ' this, contact the Bitmessage developers and we can modify'
                ' the check or you can do it yourself by searching the source'
                ' code for this message.')
        queues.apiAddressGeneratorReturnQueue.queue.clear()
        logger.debug(
            'Requesting that the addressGenerator create %s addresses.',
            numberOfAddresses)
        queues.addressGeneratorQueue.put((
            'createDeterministicAddresses', addressVersionNumber, streamNumber,
            'unused API address', numberOfAddresses, passphrase,
            eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes
        ))
        data = '{"addresses":['
        queueReturn = queues.apiAddressGeneratorReturnQueue.get()
        for item in queueReturn:
            if len(data) > 20:
                data += ','
            data += "\"" + item + "\""
        data += ']}'
        return data

    def HandleGetDeterministicAddress(self, params):
        if len(params) != 3:
            raise APIError(0, 'I need exactly 3 parameters.')
        passphrase, addressVersionNumber, streamNumber = params
        numberOfAddresses = 1
        eighteenByteRipe = False
        if len(passphrase) == 0:
            raise APIError(1, 'The specified passphrase is blank.')
        passphrase = self._decode(passphrase, "base64")
        if addressVersionNumber != 3 and addressVersionNumber != 4:
            raise APIError(
                2, 'The address version number currently must be 3 or 4. %i'
                ' isn\'t supported.' % addressVersionNumber)
        if streamNumber != 1:
            raise APIError(
                3, ' The stream number must be 1. Others aren\'t supported.')
        queues.apiAddressGeneratorReturnQueue.queue.clear()
        logger.debug(
            'Requesting that the addressGenerator create %s addresses.',
            numberOfAddresses)
        queues.addressGeneratorQueue.put((
            'getDeterministicAddress', addressVersionNumber, streamNumber,
            'unused API address', numberOfAddresses, passphrase,
            eighteenByteRipe
        ))
        return queues.apiAddressGeneratorReturnQueue.get()

    def HandleCreateChan(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters.')
        elif len(params) == 1:
            passphrase, = params
        passphrase = self._decode(passphrase, "base64")
        if len(passphrase) == 0:
            raise APIError(1, 'The specified passphrase is blank.')
        # It would be nice to make the label the passphrase but it is
        # possible that the passphrase contains non-utf-8 characters.
        try:
            unicode(passphrase, 'utf-8')
            label = str_chan + ' ' + passphrase
        except:
            label = str_chan + ' ' + repr(passphrase)

        addressVersionNumber = 4
        streamNumber = 1
        queues.apiAddressGeneratorReturnQueue.queue.clear()
        logger.debug(
            'Requesting that the addressGenerator create chan %s.', passphrase)
        queues.addressGeneratorQueue.put((
            'createChan', addressVersionNumber, streamNumber, label,
            passphrase, True
        ))
        queueReturn = queues.apiAddressGeneratorReturnQueue.get()
        if len(queueReturn) == 0:
            raise APIError(24, 'Chan address is already present.')
        address = queueReturn[0]
        return address

    def HandleJoinChan(self, params):
        if len(params) < 2:
            raise APIError(0, 'I need two parameters.')
        elif len(params) == 2:
            passphrase, suppliedAddress = params
        passphrase = self._decode(passphrase, "base64")
        if len(passphrase) == 0:
            raise APIError(1, 'The specified passphrase is blank.')
        # It would be nice to make the label the passphrase but it is
        # possible that the passphrase contains non-utf-8 characters.
        try:
            unicode(passphrase, 'utf-8')
            label = str_chan + ' ' + passphrase
        except:
            label = str_chan + ' ' + repr(passphrase)

        status, addressVersionNumber, streamNumber, toRipe = \
            self._verifyAddress(suppliedAddress)
        suppliedAddress = addBMIfNotPresent(suppliedAddress)
        queues.apiAddressGeneratorReturnQueue.queue.clear()
        queues.addressGeneratorQueue.put((
            'joinChan', suppliedAddress, label, passphrase, True
        ))
        addressGeneratorReturnValue = \
            queues.apiAddressGeneratorReturnQueue.get()

        if addressGeneratorReturnValue[0] == \
                'chan name does not match address':
            raise APIError(18, 'Chan name does not match address.')
        if len(addressGeneratorReturnValue) == 0:
            raise APIError(24, 'Chan address is already present.')
        # TODO: this variable is not used to anything
        # in case we ever want it for anything.
        # createdAddress = addressGeneratorReturnValue[0]
        return "success"

    def HandleLeaveChan(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters.')
        elif len(params) == 1:
            address, = params
        status, addressVersionNumber, streamNumber, toRipe = \
            self._verifyAddress(address)
        address = addBMIfNotPresent(address)
        if not BMConfigParser().has_section(address):
            raise APIError(
                13, 'Could not find this address in your keys.dat file.')
        if not BMConfigParser().safeGetBoolean(address, 'chan'):
            raise APIError(
                25, 'Specified address is not a chan address.'
                ' Use deleteAddress API call instead.')
        BMConfigParser().remove_section(address)
        with open(state.appdata + 'keys.dat', 'wb') as configfile:
            BMConfigParser().write(configfile)
        return 'success'

    def HandleDeleteAddress(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters.')
        elif len(params) == 1:
            address, = params
        status, addressVersionNumber, streamNumber, toRipe = \
            self._verifyAddress(address)
        address = addBMIfNotPresent(address)
        if not BMConfigParser().has_section(address):
            raise APIError(
                13, 'Could not find this address in your keys.dat file.')
        BMConfigParser().remove_section(address)
        with open(state.appdata + 'keys.dat', 'wb') as configfile:
            BMConfigParser().write(configfile)
        queues.UISignalQueue.put(('rerenderMessagelistFromLabels', ''))
        queues.UISignalQueue.put(('rerenderMessagelistToLabels', ''))
        shared.reloadMyAddressHashes()
        return 'success'

    def HandleGetAllInboxMessages(self, params):
        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, received, message,"
            " encodingtype, read FROM inbox where folder='inbox'"
            " ORDER BY received"
        )
        data = '{"inboxMessages":['
        for row in queryreturn:
            msgid, toAddress, fromAddress, subject, received, message, \
                encodingtype, read = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            message = shared.fixPotentiallyInvalidUTF8Data(message)
            if len(data) > 25:
                data += ','
            data += json.dumps({
                'msgid': hexlify(msgid),
                'toAddress': toAddress,
                'fromAddress': fromAddress,
                'subject': base64.b64encode(subject),
                'message': base64.b64encode(message),
                'encodingType': encodingtype,
                'receivedTime': received,
                'read': read}, indent=4, separators=(',', ': '))
        data += ']}'
        return data

    def HandleGetAllInboxMessageIds(self, params):
        queryreturn = sqlQuery(
            "SELECT msgid FROM inbox where folder='inbox' ORDER BY received")
        data = '{"inboxMessageIds":['
        for row in queryreturn:
            msgid = row[0]
            if len(data) > 25:
                data += ','
            data += json.dumps(
                {'msgid': hexlify(msgid)}, indent=4, separators=(',', ': '))
        data += ']}'
        return data

    def HandleGetInboxMessageById(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        elif len(params) == 1:
            msgid = self._decode(params[0], "hex")
        elif len(params) >= 2:
            msgid = self._decode(params[0], "hex")
            readStatus = params[1]
            if not isinstance(readStatus, bool):
                raise APIError(
                    23, 'Bool expected in readStatus, saw %s instead.' %
                    type(readStatus))
            queryreturn = sqlQuery(
                "SELECT read FROM inbox WHERE msgid=?", msgid)
            # UPDATE is slow, only update if status is different
            if queryreturn != [] and (queryreturn[0][0] == 1) != readStatus:
                sqlExecute(
                    "UPDATE inbox set read = ? WHERE msgid=?",
                    readStatus, msgid)
                queues.UISignalQueue.put(('changedInboxUnread', None))
        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, received, message,"
            " encodingtype, read FROM inbox WHERE msgid=?", msgid
        )
        data = '{"inboxMessage":['
        for row in queryreturn:
            msgid, toAddress, fromAddress, subject, received, message, \
                encodingtype, read = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            message = shared.fixPotentiallyInvalidUTF8Data(message)
            data += json.dumps({
                'msgid': hexlify(msgid),
                'toAddress': toAddress,
                'fromAddress': fromAddress,
                'subject': base64.b64encode(subject),
                'message': base64.b64encode(message),
                'encodingType': encodingtype,
                'receivedTime': received,
                'read': read}, indent=4, separators=(',', ': '))
            data += ']}'
            return data

    def HandleGetAllSentMessages(self, params):
        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, lastactiontime,"
            " message, encodingtype, status, ackdata FROM sent"
            " WHERE folder='sent' ORDER BY lastactiontime"
        )
        data = '{"sentMessages":['
        for row in queryreturn:
            msgid, toAddress, fromAddress, subject, lastactiontime, message, \
                encodingtype, status, ackdata = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            message = shared.fixPotentiallyInvalidUTF8Data(message)
            if len(data) > 25:
                data += ','
            data += json.dumps({
                'msgid': hexlify(msgid),
                'toAddress': toAddress,
                'fromAddress': fromAddress,
                'subject': base64.b64encode(subject),
                'message': base64.b64encode(message),
                'encodingType': encodingtype,
                'lastActionTime': lastactiontime,
                'status': status,
                'ackData': hexlify(ackdata)}, indent=4, separators=(',', ': '))
        data += ']}'
        return data

    def HandleGetAllSentMessageIds(self, params):
        queryreturn = sqlQuery(
            "SELECT msgid FROM sent where folder='sent'"
            " ORDER BY lastactiontime"
        )
        data = '{"sentMessageIds":['
        for row in queryreturn:
            msgid = row[0]
            if len(data) > 25:
                data += ','
            data += json.dumps(
                {'msgid': hexlify(msgid)}, indent=4, separators=(',', ': '))
        data += ']}'
        return data

    def HandleInboxMessagesByReceiver(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        toAddress = params[0]
        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, received, message,"
            " encodingtype FROM inbox WHERE folder='inbox' AND toAddress=?",
            toAddress)
        data = '{"inboxMessages":['
        for row in queryreturn:
            msgid, toAddress, fromAddress, subject, received, message, \
                encodingtype = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            message = shared.fixPotentiallyInvalidUTF8Data(message)
            if len(data) > 25:
                data += ','
            data += json.dumps({
                'msgid': hexlify(msgid),
                'toAddress': toAddress,
                'fromAddress': fromAddress,
                'subject': base64.b64encode(subject),
                'message': base64.b64encode(message),
                'encodingType': encodingtype,
                'receivedTime': received}, indent=4, separators=(',', ': '))
        data += ']}'
        return data

    def HandleGetSentMessageById(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        msgid = self._decode(params[0], "hex")
        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, lastactiontime,"
            " message, encodingtype, status, ackdata FROM sent WHERE msgid=?",
            msgid
        )
        data = '{"sentMessage":['
        for row in queryreturn:
            msgid, toAddress, fromAddress, subject, lastactiontime, message, \
                encodingtype, status, ackdata = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            message = shared.fixPotentiallyInvalidUTF8Data(message)
            data += json.dumps({
                'msgid': hexlify(msgid),
                'toAddress': toAddress,
                'fromAddress': fromAddress,
                'subject': base64.b64encode(subject),
                'message': base64.b64encode(message),
                'encodingType': encodingtype,
                'lastActionTime': lastactiontime,
                'status': status,
                'ackData': hexlify(ackdata)}, indent=4, separators=(',', ': '))
            data += ']}'
            return data

    def HandleGetSentMessagesByAddress(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        fromAddress = params[0]
        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, lastactiontime,"
            " message, encodingtype, status, ackdata FROM sent"
            " WHERE folder='sent' AND fromAddress=? ORDER BY lastactiontime",
            fromAddress
        )
        data = '{"sentMessages":['
        for row in queryreturn:
            msgid, toAddress, fromAddress, subject, lastactiontime, message, \
                encodingtype, status, ackdata = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            message = shared.fixPotentiallyInvalidUTF8Data(message)
            if len(data) > 25:
                data += ','
            data += json.dumps({
                'msgid': hexlify(msgid),
                'toAddress': toAddress,
                'fromAddress': fromAddress,
                'subject': base64.b64encode(subject),
                'message': base64.b64encode(message),
                'encodingType': encodingtype,
                'lastActionTime': lastactiontime,
                'status': status,
                'ackData': hexlify(ackdata)}, indent=4, separators=(',', ': '))
        data += ']}'
        return data

    def HandleGetSentMessagesByAckData(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        ackData = self._decode(params[0], "hex")
        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, lastactiontime,"
            " message, encodingtype, status, ackdata FROM sent"
            " WHERE ackdata=?", ackData
        )
        data = '{"sentMessage":['
        for row in queryreturn:
            msgid, toAddress, fromAddress, subject, lastactiontime, message, \
                encodingtype, status, ackdata = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            message = shared.fixPotentiallyInvalidUTF8Data(message)
            data += json.dumps({
                'msgid': hexlify(msgid),
                'toAddress': toAddress,
                'fromAddress': fromAddress,
                'subject': base64.b64encode(subject),
                'message': base64.b64encode(message),
                'encodingType': encodingtype,
                'lastActionTime': lastactiontime,
                'status': status,
                'ackData': hexlify(ackdata)}, indent=4, separators=(',', ': '))
        data += ']}'
        return data

    def HandleTrashMessage(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        msgid = self._decode(params[0], "hex")

        # Trash if in inbox table
        helper_inbox.trash(msgid)
        # Trash if in sent table
        sqlExecute('''UPDATE sent SET folder='trash' WHERE msgid=?''', msgid)
        return 'Trashed message (assuming message existed).'

    def HandleTrashInboxMessage(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        msgid = self._decode(params[0], "hex")
        helper_inbox.trash(msgid)
        return 'Trashed inbox message (assuming message existed).'

    def HandleTrashSentMessage(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        msgid = self._decode(params[0], "hex")
        sqlExecute('''UPDATE sent SET folder='trash' WHERE msgid=?''', msgid)
        return 'Trashed sent message (assuming message existed).'

    def HandleSendMessage(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        elif len(params) == 4:
            toAddress, fromAddress, subject, message = params
            encodingType = 2
            TTL = 4 * 24 * 60 * 60
        elif len(params) == 5:
            toAddress, fromAddress, subject, message, encodingType = params
            TTL = 4 * 24 * 60 * 60
        elif len(params) == 6:
            toAddress, fromAddress, subject, message, encodingType, TTL = \
                params
        if encodingType not in [2, 3]:
            raise APIError(6, 'The encoding type must be 2 or 3.')
        subject = self._decode(subject, "base64")
        message = self._decode(message, "base64")
        if len(subject + message) > (2 ** 18 - 500):
            raise APIError(27, 'Message is too long.')
        if TTL < 60 * 60:
            TTL = 60 * 60
        if TTL > 28 * 24 * 60 * 60:
            TTL = 28 * 24 * 60 * 60
        toAddress = addBMIfNotPresent(toAddress)
        fromAddress = addBMIfNotPresent(fromAddress)
        status, addressVersionNumber, streamNumber, toRipe = \
            self._verifyAddress(toAddress)
        self._verifyAddress(fromAddress)
        try:
            fromAddressEnabled = BMConfigParser().getboolean(
                fromAddress, 'enabled')
        except:
            raise APIError(
                13, 'Could not find your fromAddress in the keys.dat file.')
        if not fromAddressEnabled:
            raise APIError(14, 'Your fromAddress is disabled. Cannot send.')

        stealthLevel = BMConfigParser().safeGetInt(
            'bitmessagesettings', 'ackstealthlevel')
        ackdata = genAckPayload(streamNumber, stealthLevel)

        t = ('',
             toAddress,
             toRipe,
             fromAddress,
             subject,
             message,
             ackdata,
             int(time.time()),  # sentTime (this won't change)
             int(time.time()),  # lastActionTime
             0,
             'msgqueued',
             0,
             'sent',
             2,
             TTL)
        helper_sent.insert(t)

        toLabel = ''
        queryreturn = sqlQuery(
            "SELECT label FROM addressbook WHERE address=?", toAddress)
        if queryreturn != []:
            for row in queryreturn:
                toLabel, = row
        # apiSignalQueue.put(('displayNewSentMessage',(toAddress,toLabel,fromAddress,subject,message,ackdata)))
        queues.UISignalQueue.put(('displayNewSentMessage', (
            toAddress, toLabel, fromAddress, subject, message, ackdata)))

        queues.workerQueue.put(('sendmessage', toAddress))

        return hexlify(ackdata)

    def HandleSendBroadcast(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        if len(params) == 3:
            fromAddress, subject, message = params
            encodingType = 2
            TTL = 4 * 24 * 60 * 60
        elif len(params) == 4:
            fromAddress, subject, message, encodingType = params
            TTL = 4 * 24 * 60 * 60
        elif len(params) == 5:
            fromAddress, subject, message, encodingType, TTL = params
        if encodingType not in [2, 3]:
            raise APIError(6, 'The encoding type must be 2 or 3.')
        subject = self._decode(subject, "base64")
        message = self._decode(message, "base64")
        if len(subject + message) > (2 ** 18 - 500):
            raise APIError(27, 'Message is too long.')
        if TTL < 60 * 60:
            TTL = 60 * 60
        if TTL > 28 * 24 * 60 * 60:
            TTL = 28 * 24 * 60 * 60
        fromAddress = addBMIfNotPresent(fromAddress)
        self._verifyAddress(fromAddress)
        try:
            BMConfigParser().getboolean(fromAddress, 'enabled')
        except:
            raise APIError(
                13, 'could not find your fromAddress in the keys.dat file.')
        streamNumber = decodeAddress(fromAddress)[2]
        ackdata = genAckPayload(streamNumber, 0)
        toAddress = '[Broadcast subscribers]'
        ripe = ''

        t = ('',
             toAddress,
             ripe,
             fromAddress,
             subject,
             message,
             ackdata,
             int(time.time()),  # sentTime (this doesn't change)
             int(time.time()),  # lastActionTime
             0,
             'broadcastqueued',
             0,
             'sent',
             2,
             TTL)
        helper_sent.insert(t)

        toLabel = '[Broadcast subscribers]'
        queues.UISignalQueue.put(('displayNewSentMessage', (
            toAddress, toLabel, fromAddress, subject, message, ackdata)))
        queues.workerQueue.put(('sendbroadcast', ''))

        return hexlify(ackdata)

    def HandleGetStatus(self, params):
        if len(params) != 1:
            raise APIError(0, 'I need one parameter!')
        ackdata, = params
        if len(ackdata) < 76:
            # The length of ackData should be at least 38 bytes (76 hex digits)
            raise APIError(15, 'Invalid ackData object size.')
        ackdata = self._decode(ackdata, "hex")
        queryreturn = sqlQuery(
            "SELECT status FROM sent where ackdata=?", ackdata)
        if queryreturn == []:
            return 'notfound'
        for row in queryreturn:
            status, = row
            return status

    def HandleAddSubscription(self, params):
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        if len(params) == 1:
            address, = params
            label = ''
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
        self._verifyAddress(address)
        # First we must check to see if the address is already in the
        # subscriptions list.
        queryreturn = sqlQuery(
            "SELECT * FROM subscriptions WHERE address=?", address)
        if queryreturn != []:
            raise APIError(16, 'You are already subscribed to that address.')
        sqlExecute(
            "INSERT INTO subscriptions VALUES (?,?,?)", label, address, True)
        shared.reloadBroadcastSendersForWhichImWatching()
        queues.UISignalQueue.put(('rerenderMessagelistFromLabels', ''))
        queues.UISignalQueue.put(('rerenderSubscriptions', ''))
        return 'Added subscription.'

    def HandleDeleteSubscription(self, params):
        if len(params) != 1:
            raise APIError(0, 'I need 1 parameter!')
        address, = params
        address = addBMIfNotPresent(address)
        sqlExecute('''DELETE FROM subscriptions WHERE address=?''', address)
        shared.reloadBroadcastSendersForWhichImWatching()
        queues.UISignalQueue.put(('rerenderMessagelistFromLabels', ''))
        queues.UISignalQueue.put(('rerenderSubscriptions', ''))
        return 'Deleted subscription if it existed.'

    def ListSubscriptions(self, params):
        queryreturn = sqlQuery(
            "SELECT label, address, enabled FROM subscriptions")
        data = {'subscriptions': []}
        for row in queryreturn:
            label, address, enabled = row
            label = shared.fixPotentiallyInvalidUTF8Data(label)
            data['subscriptions'].append({
                'label': base64.b64encode(label),
                'address': address,
                'enabled': enabled == 1
            })
        return json.dumps(data, indent=4, separators=(',', ': '))

    def HandleTrashSentMessageByAckDAta(self, params):
        # This API method should only be used when msgid is not available
        if len(params) == 0:
            raise APIError(0, 'I need parameters!')
        ackdata = self._decode(params[0], "hex")
        sqlExecute("UPDATE sent SET folder='trash' WHERE ackdata=?", ackdata)
        return 'Trashed sent message (assuming message existed).'

    def HandleDisseminateRawObject(self, arguments):
        if len(arguments) != 1:
            raise APIError(0, "1 argument needed")

        payload = self._decode(arguments[0], "hex")

        inventoryHash = protocol.checkAndShareObjectWithPeers(payload)

        if inventoryHash is None:
            raise APIError(30, "Invalid object or insufficient POW")
        else:
            return hexlify(inventoryHash)

    def HandleGetRawObject(self, arguments):
        if len(arguments) != 1:
            raise APIError(0, "1 argument needed")

        inventoryHash, = arguments

        if len(inventoryHash) != 64:
            raise APIError(19, "The length of hash should be 32 bytes (encoded in hex thus 64 characters)")

        inventoryHash = self._decode(inventoryHash, "hex")

        try:
            inventoryItem = Inventory()[inventoryHash]
        except KeyError:
            raise APIError(31, "Object not found")

        return json.dumps({
            "hash": hexlify(inventoryHash),
            "expiryTime": inventoryItem.expires,
            "objectType": inventoryItem.type,
            "stream": inventoryItem.stream,
            "tag": hexlify(inventoryItem.tag),
            "payload": hexlify(inventoryItem.payload)
        }, indent = 4, separators = (",", ": "))

    def HandleListRawObjects(self, arguments):
        if len(arguments) != 3:
            raise APIError(0, "3 arguments needed")

        objectType, stream, tag = arguments

        if tag is not None:
            tag = buffer(self._decode(tag, "hex"))

        result = []

        inventory = Inventory()

        for i in inventory:
            inventoryItem = inventory[str(i)]

            if objectType is not None and inventoryItem.type != objectType:
                continue

            if stream is not None and inventoryItem.stream != stream:
                continue

            if tag is not None and inventoryItem.tag != tag:
                continue

            result.append(hexlify(i))

        return json.dumps(result, indent = 4, separators = (",", ": "))

    def HandleQueueRawObject(self, arguments):
        if len(arguments) != 2:
            raise APIError(0, "2 arguments needed")

        TTL, headlessPayload = arguments
        headlessPayload = self._decode(headlessPayload, "hex")

        if type(TTL) is not int or TTL < 300 or TTL > 28 * 24 * 60 * 60:
            raise APIError(33, "TTL must be an integer between 300 and 28 * 24 * 60 * 60 seconds")

        ID = helper_random.randomBytes(32)

        queues.workerQueue.put(("sendRawObject", ID, TTL, headlessPayload))
        queuedRawObjects[ID] = "queued",

        return hexlify(ID)

    def HandleCancelQueuedRawObject(self, arguments):
        if len(arguments) != 1:
            raise APIError(0, "1 argument needed")

        ID, = arguments

        if len(ID) != 64:
            raise APIError(19, "The length of queue item ID should be 32 bytes (encoded in hex thus 64 characters)")

        ID = self._decode(ID, 'hex')

        queues.workerQueue.put(("cancelRawObject", ID))

    def HandleCheckQueuedRawObject(self, arguments):
        if len(arguments) != 1:
            raise APIError(0, "1 argument needed")

        ID, = arguments

        if len(ID) != 64:
            raise APIError(19, "The length of queue item ID should be 32 bytes (encoded in hex thus 64 characters)")

        ID = self._decode(ID, 'hex')

        while True:
            try:
                queueItem = queues.processedRawObjectsQueue.get_nowait()
                command, randomID, arguments = queueItem[0], queueItem[1], queueItem[2: ]

                if command == "sent":
                    queuedRawObjects[randomID] = command, hexlify(arguments[0])
                else:
                    queuedRawObjects[randomID] = (command, ) + arguments
            except Queue.Empty:
                break

        status = queuedRawObjects.get(ID, ("notfound", ))

        if status[0] in ["failed", "sent", "canceled"]:
            del queuedRawObjects[ID]

        return status

    def HandleClientStatus(self, params):
        if len(network.stats.connectedHostsList()) == 0:
            networkStatus = 'notConnected'
        elif len(network.stats.connectedHostsList()) > 0 \
                and not shared.clientHasReceivedIncomingConnections:
            networkStatus = 'connectedButHaveNotReceivedIncomingConnections'
        else:
            networkStatus = 'connectedAndReceivingIncomingConnections'
        return json.dumps({
            'networkConnections': len(network.stats.connectedHostsList()),
            'numberOfMessagesProcessed': shared.numberOfMessagesProcessed,
            'numberOfBroadcastsProcessed': shared.numberOfBroadcastsProcessed,
            'numberOfPubkeysProcessed': shared.numberOfPubkeysProcessed,
            'networkStatus': networkStatus,
            'softwareName': 'PyBitmessage',
            'softwareVersion': softwareVersion
            }, indent=4, separators=(',', ': '))

    def HandleDecodeAddress(self, params):
        # Return a meaningful decoding of an address.
        if len(params) != 1:
            raise APIError(0, 'I need 1 parameter!')
        address, = params
        status, addressVersion, streamNumber, ripe = decodeAddress(address)
        return json.dumps({
            'status': status,
            'addressVersion': addressVersion,
            'streamNumber': streamNumber,
            'ripe': base64.b64encode(ripe)
            }, indent=4, separators=(',', ': '))

    def HandleHelloWorld(self, params):
        a, b = params
        return a + '-' + b

    def HandleAdd(self, params):
        a, b = params
        return a + b

    def HandleStatusBar(self, params):
        message, = params
        queues.UISignalQueue.put(('updateStatusBar', message))

    def HandleDeleteAndVacuum(self, params):
        if not params:
            sqlStoredProcedure('deleteandvacuume')
            return 'done'

    def HandleShutdown(self, params):
        if not params:
            shutdown.doCleanShutdown()
            return 'done'

    handlers = {}
    handlers['helloWorld'] = HandleHelloWorld
    handlers['add'] = HandleAdd
    handlers['statusBar'] = HandleStatusBar
    handlers['listAddresses'] = HandleListAddresses
    handlers['listAddressBookEntries'] = HandleListAddressBookEntries
    # the listAddressbook alias should be removed eventually.
    handlers['listAddressbook'] = HandleListAddressBookEntries
    handlers['addAddressBookEntry'] = HandleAddAddressBookEntry
    # the addAddressbook alias should be deleted eventually.
    handlers['addAddressbook'] = HandleAddAddressBookEntry
    handlers['deleteAddressBookEntry'] = HandleDeleteAddressBookEntry
    # The deleteAddressbook alias should be deleted eventually.
    handlers['deleteAddressbook'] = HandleDeleteAddressBookEntry
    handlers['createRandomAddress'] = HandleCreateRandomAddress
    handlers['createDeterministicAddresses'] = \
        HandleCreateDeterministicAddresses
    handlers['getDeterministicAddress'] = HandleGetDeterministicAddress
    handlers['createChan'] = HandleCreateChan
    handlers['joinChan'] = HandleJoinChan
    handlers['leaveChan'] = HandleLeaveChan
    handlers['deleteAddress'] = HandleDeleteAddress
    handlers['getAllInboxMessages'] = HandleGetAllInboxMessages
    handlers['getAllInboxMessageIds'] = HandleGetAllInboxMessageIds
    handlers['getAllInboxMessageIDs'] = HandleGetAllInboxMessageIds
    handlers['getInboxMessageById'] = HandleGetInboxMessageById
    handlers['getInboxMessageByID'] = HandleGetInboxMessageById
    handlers['getAllSentMessages'] = HandleGetAllSentMessages
    handlers['getAllSentMessageIds'] = HandleGetAllSentMessageIds
    handlers['getAllSentMessageIDs'] = HandleGetAllSentMessageIds
    handlers['getInboxMessagesByReceiver'] = HandleInboxMessagesByReceiver
    # after some time getInboxMessagesByAddress should be removed
    handlers['getInboxMessagesByAddress'] = HandleInboxMessagesByReceiver
    handlers['getSentMessageById'] = HandleGetSentMessageById
    handlers['getSentMessageByID'] = HandleGetSentMessageById
    handlers['getSentMessagesByAddress'] = HandleGetSentMessagesByAddress
    handlers['getSentMessagesBySender'] = HandleGetSentMessagesByAddress
    handlers['getSentMessageByAckData'] = HandleGetSentMessagesByAckData
    handlers['trashMessage'] = HandleTrashMessage
    handlers['trashInboxMessage'] = HandleTrashInboxMessage
    handlers['trashSentMessage'] = HandleTrashSentMessage
    handlers['trashSentMessageByAckData'] = HandleTrashSentMessageByAckDAta
    handlers['sendMessage'] = HandleSendMessage
    handlers['sendBroadcast'] = HandleSendBroadcast
    handlers['getStatus'] = HandleGetStatus
    handlers['addSubscription'] = HandleAddSubscription
    handlers['deleteSubscription'] = HandleDeleteSubscription
    handlers['listSubscriptions'] = ListSubscriptions
    handlers["disseminateRawObject"] = HandleDisseminateRawObject
    handlers["getRawObject"] = HandleGetRawObject
    handlers["listRawObjects"] = HandleListRawObjects
    handlers["queueRawObject"] = HandleQueueRawObject
    handlers["cancelQueuedRawObject"] = HandleCancelQueuedRawObject
    handlers["checkQueuedRawObject"] = HandleCheckQueuedRawObject
    handlers['clientStatus'] = HandleClientStatus
    handlers['decodeAddress'] = HandleDecodeAddress
    handlers['deleteAndVacuum'] = HandleDeleteAndVacuum
    handlers['shutdown'] = HandleShutdown

    def _handle_request(self, method, params):
        if method not in self.handlers:
            raise APIError(20, 'Invalid method: %s' % method)
        return self.handlers[method](self, params)

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
        except varintDecodeError as e:
            logger.error(e)
            return "API Error 0026: Data contains a malformed varint. Some details: %s" % e
        except Exception as e:
            logger.exception(e)

            return "API Error 0021: Unexpected API Failure - %s" % e

# This thread, of which there is only one, runs the API.
class singleAPI(threading.Thread, helper_threading.StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="singleAPI")
        self.initStop()

    def stopThread(self):
        super(singleAPI, self).stopThread()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((
                BMConfigParser().get('bitmessagesettings', 'apiinterface'),
                BMConfigParser().getint('bitmessagesettings', 'apiport')
            ))
            s.shutdown(socket.SHUT_RDWR)
            s.close()
        except:
            pass

    def run(self):
        port = BMConfigParser().getint('bitmessagesettings', 'apiport')
        try:
            from errno import WSAEADDRINUSE
        except (ImportError, AttributeError):
            errno.WSAEADDRINUSE = errno.EADDRINUSE
        for attempt in range(50):
            try:
                if attempt > 0:
                    port = randint(32767, 65535)
                se = StoppableXMLRPCServer(
                    (BMConfigParser().get(
                        'bitmessagesettings', 'apiinterface'),
                     port),
                    MySimpleXMLRPCRequestHandler, True, True)
            except socket.error as e:
                if e.errno in (errno.EADDRINUSE, errno.WSAEADDRINUSE):
                    continue
            else:
                if attempt > 0:
                    BMConfigParser().set(
                        "bitmessagesettings", "apiport", str(port))
                    BMConfigParser().save()
                break
        se.register_introspection_functions()
        se.serve_forever()
