# Copyright (c) 2012-2016 Jonathan Warren
# Copyright (c) 2012-2020 The Bitmessage developers
# pylint: disable=too-many-lines,no-self-use,unused-variable,unused-argument

"""
This is not what you run to run the Bitmessage API. Instead, enable the API
( https://bitmessage.org/wiki/API ) and optionally enable daemon mode
( https://bitmessage.org/wiki/Daemon ) then run bitmessagemain.py.
"""

import base64
import ConfigParser
import errno
import hashlib
import json
import random  # nosec
import socket
import subprocess
import time
from binascii import hexlify, unhexlify
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer
from struct import pack

import defaults
import helper_inbox
import helper_sent
import network.stats
import proofofwork
import queues
import shared
import shutdown
import state
from addresses import (
    addBMIfNotPresent,
    calculateInventoryHash,
    decodeAddress,
    decodeVarint,
    varintDecodeError
)
from bmconfigparser import BMConfigParser
from debug import logger
from helper_ackPayload import genAckPayload
from helper_sql import SqlBulkExecute, sqlExecute, sqlQuery, sqlStoredProcedure
from inventory import Inventory
from network.threads import StoppableThread
from version import softwareVersion

str_chan = '[chan]'
str_broadcast_subscribers = '[Broadcast subscribers]'


class APIError(Exception):
    """APIError exception class"""

    def __init__(self, error_number, error_message):
        super(APIError, self).__init__()
        self.error_number = error_number
        self.error_message = error_message

    def __str__(self):
        return "API Error %04i: %s" % (self.error_number, self.error_message)


class StoppableXMLRPCServer(SimpleXMLRPCServer):
    """A SimpleXMLRPCServer that honours state.shutdown"""
    allow_reuse_address = True

    def serve_forever(self):
        """Start the SimpleXMLRPCServer"""
        # pylint: disable=arguments-differ
        while state.shutdown == 0:
            self.handle_request()


# This thread, of which there is only one, runs the API.
class singleAPI(StoppableThread):
    """API thread"""

    name = "singleAPI"

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
        except BaseException:
            pass

    def run(self):
        port = BMConfigParser().getint('bitmessagesettings', 'apiport')
        try:
            getattr(errno, 'WSAEADDRINUSE')
        except AttributeError:
            errno.WSAEADDRINUSE = errno.EADDRINUSE
        for attempt in range(50):
            try:
                if attempt > 0:
                    logger.warning(
                        'Failed to start API listener on port %s', port)
                    port = random.randint(32767, 65535)
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
                    logger.warning('Setting apiport to %s', port)
                    BMConfigParser().set(
                        'bitmessagesettings', 'apiport', str(port))
                    BMConfigParser().save()
                break
        se.register_introspection_functions()

        apiNotifyPath = BMConfigParser().safeGet(
            'bitmessagesettings', 'apinotifypath')

        if apiNotifyPath:
            logger.info('Trying to call %s', apiNotifyPath)
            try:
                subprocess.call([apiNotifyPath, "startingUp"])
            except OSError:
                logger.warning(
                    'Failed to call %s, removing apinotifypath setting',
                    apiNotifyPath)
                BMConfigParser().remove_option(
                    'bitmessagesettings', 'apinotifypath')

        se.serve_forever()


class CommandHandler(type):
    """
    The metaclass for `BMRPCDispatcher` which fills _handlers dict by
    methods decorated with @command
    """
    def __new__(mcs, name, bases, namespace):
        # pylint: disable=protected-access
        result = super(CommandHandler, mcs).__new__(
            mcs, name, bases, namespace)
        result._handlers = {}
        for func in namespace.values():
            try:
                for alias in getattr(func, '_cmd'):
                    result._handlers[alias] = func
            except AttributeError:
                pass
        return result


class command(object):
    """Decorator for API command method"""
    def __init__(self, *aliases):
        self.aliases = aliases

    def __call__(self, func):
        def wrapper(*args):
            # return json.dumps(func(*args), indent=4)
            return func(*args)
        # pylint: disable=protected-access
        wrapper._cmd = self.aliases
        return wrapper


# This is one of several classes that constitute the API
# This class was written by Vaibhav Bhatia.
# Modified by Jonathan Warren (Atheros).
# Further modified by the Bitmessage developers
# http://code.activestate.com/recipes/501148
class MySimpleXMLRPCRequestHandler(SimpleXMLRPCRequestHandler, object):
    """The main API handler"""
    __metaclass__ = CommandHandler

    def do_POST(self):
        """
        Handles the HTTP POST request.

        Attempts to interpret all HTTP POST requests as XML-RPC calls,
        which are forwarded to the server's _dispatch method for handling.

        Note: this method is the same as in SimpleXMLRPCRequestHandler,
        just hacked to handle cookies
        """

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
            # pylint: disable=protected-access
            response = self.server._marshaled_dispatch(
                data, getattr(self, '_dispatch', None)
            )
        except BaseException:  # This should only happen if the module is buggy
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

            # actually handle shutdown command after sending response
            if state.shutdown is False:
                shutdown.doCleanShutdown()

    def APIAuthenticateClient(self):
        """Predicate to check for valid API credentials in the request header"""

        if 'Authorization' in self.headers:
            # handle Basic authentication
            encstr = self.headers.get('Authorization').split()[1]
            emailid, password = encstr.decode('base64').split(':')
            return (
                emailid == BMConfigParser().get(
                    'bitmessagesettings', 'apiusername') and
                password == BMConfigParser().get(
                    'bitmessagesettings', 'apipassword')
            )
        else:
            logger.warning(
                'Authentication failed because header lacks'
                ' Authentication field')
            time.sleep(2)

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
        return None

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
                    'Address version number too high (or zero) in address: ' +
                    address)
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

    @staticmethod
    def _dump_inbox_message(
            msgid, toAddress, fromAddress, subject, received,
            message, encodingtype, read):
        subject = shared.fixPotentiallyInvalidUTF8Data(subject)
        message = shared.fixPotentiallyInvalidUTF8Data(message)
        return {
            'msgid': hexlify(msgid),
            'toAddress': toAddress,
            'fromAddress': fromAddress,
            'subject': base64.b64encode(subject),
            'message': base64.b64encode(message),
            'encodingType': encodingtype,
            'receivedTime': received,
            'read': read
        }

    @staticmethod
    def _dump_sent_message(
            msgid, toAddress, fromAddress, subject, lastactiontime,
            message, encodingtype, status, ackdata):
        subject = shared.fixPotentiallyInvalidUTF8Data(subject)
        message = shared.fixPotentiallyInvalidUTF8Data(message)
        return {
            'msgid': hexlify(msgid),
            'toAddress': toAddress,
            'fromAddress': fromAddress,
            'subject': base64.b64encode(subject),
            'message': base64.b64encode(message),
            'encodingType': encodingtype,
            'lastActionTime': lastactiontime,
            'status': status,
            'ackData': hexlify(ackdata)
        }

    # Request Handlers

    @command('listAddresses', 'listAddresses2')
    def HandleListAddresses(self):
        data = []
        for address in BMConfigParser().addresses():
            streamNumber = decodeAddress(address)[2]
            label = BMConfigParser().get(address, 'label')
            if self._method == 'listAddresses2':
                label = base64.b64encode(label)
            data.append({
                'label': label,
                'address': address,
                'stream': streamNumber,
                'enabled': BMConfigParser().safeGetBoolean(address, 'enabled'),
                'chan': BMConfigParser().safeGetBoolean(address, 'chan')
            })
        return {'addresses': data}

    # the listAddressbook alias should be removed eventually.
    @command('listAddressBookEntries', 'listAddressbook')
    def HandleListAddressBookEntries(self, label=None):
        queryreturn = sqlQuery(
            "SELECT label, address from addressbook WHERE label = ?",
            label
        ) if label else sqlQuery("SELECT label, address from addressbook")
        data = []
        for label, address in queryreturn:
            label = shared.fixPotentiallyInvalidUTF8Data(label)
            data.append({
                'label': base64.b64encode(label),
                'address': address
            })
        return {'addresses': data}

    # the addAddressbook alias should be deleted eventually.
    @command('addAddressBookEntry', 'addAddressbook')
    def HandleAddAddressBookEntry(self, address, label):
        label = self._decode(label, "base64")
        address = addBMIfNotPresent(address)
        self._verifyAddress(address)
        # TODO: add unique together constraint in the table
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

    # the deleteAddressbook alias should be deleted eventually.
    @command('deleteAddressBookEntry', 'deleteAddressbook')
    def HandleDeleteAddressBookEntry(self, address):
        address = addBMIfNotPresent(address)
        self._verifyAddress(address)
        sqlExecute('DELETE FROM addressbook WHERE address=?', address)
        queues.UISignalQueue.put(('rerenderMessagelistFromLabels', ''))
        queues.UISignalQueue.put(('rerenderMessagelistToLabels', ''))
        queues.UISignalQueue.put(('rerenderAddressBook', ''))
        return "Deleted address book entry for %s if it existed" % address

    @command('createRandomAddress')
    def HandleCreateRandomAddress(
        self, label, eighteenByteRipe=False, totalDifficulty=0,
        smallMessageDifficulty=0
    ):
        """Handle a request to create a random address"""

        nonceTrialsPerByte = BMConfigParser().get(
            'bitmessagesettings', 'defaultnoncetrialsperbyte'
        ) if not totalDifficulty else int(
            defaults.networkDefaultProofOfWorkNonceTrialsPerByte *
            totalDifficulty)
        payloadLengthExtraBytes = BMConfigParser().get(
            'bitmessagesettings', 'defaultpayloadlengthextrabytes'
        ) if not smallMessageDifficulty else int(
            defaults.networkDefaultPayloadLengthExtraBytes *
            smallMessageDifficulty)

        if not isinstance(eighteenByteRipe, bool):
            raise APIError(
                23, 'Bool expected in eighteenByteRipe, saw %s instead' %
                type(eighteenByteRipe))
        label = self._decode(label, "base64")
        try:
            unicode(label, 'utf-8')
        except UnicodeDecodeError:
            raise APIError(17, 'Label is not valid UTF-8 data.')
        queues.apiAddressGeneratorReturnQueue.queue.clear()
        # FIXME hard coded stream no
        streamNumberForAddress = 1
        queues.addressGeneratorQueue.put((
            'createRandomAddress', 4, streamNumberForAddress, label, 1, "",
            eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes
        ))
        return queues.apiAddressGeneratorReturnQueue.get()

    @command('createDeterministicAddresses')
    def HandleCreateDeterministicAddresses(
        self, passphrase, numberOfAddresses=1, addressVersionNumber=0,
        streamNumber=0, eighteenByteRipe=False, totalDifficulty=0,
        smallMessageDifficulty=0
    ):
        """Handle a request to create a deterministic address"""
        # pylint: disable=too-many-branches, too-many-statements

        nonceTrialsPerByte = BMConfigParser().get(
            'bitmessagesettings', 'defaultnoncetrialsperbyte'
        ) if not totalDifficulty else int(
            defaults.networkDefaultProofOfWorkNonceTrialsPerByte *
            totalDifficulty)
        payloadLengthExtraBytes = BMConfigParser().get(
            'bitmessagesettings', 'defaultpayloadlengthextrabytes'
        ) if not smallMessageDifficulty else int(
            defaults.networkDefaultPayloadLengthExtraBytes *
            smallMessageDifficulty)

        if not passphrase:
            raise APIError(1, 'The specified passphrase is blank.')
        if not isinstance(eighteenByteRipe, bool):
            raise APIError(
                23, 'Bool expected in eighteenByteRipe, saw %s instead' %
                type(eighteenByteRipe))
        passphrase = self._decode(passphrase, "base64")
        # 0 means "just use the proper addressVersionNumber"
        if addressVersionNumber == 0:
            addressVersionNumber = 4
        if addressVersionNumber not in (3, 4):
            raise APIError(
                2, 'The address version number currently must be 3, 4, or 0'
                ' (which means auto-select). %i isn\'t supported.' %
                addressVersionNumber)
        if streamNumber == 0:  # 0 means "just use the most available stream"
            streamNumber = 1  # FIXME hard coded stream no
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

        return {'addresses': queues.apiAddressGeneratorReturnQueue.get()}

    @command('getDeterministicAddress')
    def HandleGetDeterministicAddress(
            self, passphrase, addressVersionNumber, streamNumber):
        """Handle a request to get a deterministic address"""

        numberOfAddresses = 1
        eighteenByteRipe = False
        if not passphrase:
            raise APIError(1, 'The specified passphrase is blank.')
        passphrase = self._decode(passphrase, "base64")
        if addressVersionNumber not in (3, 4):
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

    @command('createChan')
    def HandleCreateChan(self, passphrase):
        """Handle a request to create a chan"""

        passphrase = self._decode(passphrase, "base64")
        if not passphrase:
            raise APIError(1, 'The specified passphrase is blank.')
        # It would be nice to make the label the passphrase but it is
        # possible that the passphrase contains non-utf-8 characters.
        try:
            unicode(passphrase, 'utf-8')
            label = str_chan + ' ' + passphrase
        except UnicodeDecodeError:
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
        try:
            return queueReturn[0]
        except IndexError:
            raise APIError(24, 'Chan address is already present.')

    @command('joinChan')
    def HandleJoinChan(self, passphrase, suppliedAddress):
        """Handle a request to join a chan"""

        passphrase = self._decode(passphrase, "base64")
        if not passphrase:
            raise APIError(1, 'The specified passphrase is blank.')
        # It would be nice to make the label the passphrase but it is
        # possible that the passphrase contains non-utf-8 characters.
        try:
            unicode(passphrase, 'utf-8')
            label = str_chan + ' ' + passphrase
        except UnicodeDecodeError:
            label = str_chan + ' ' + repr(passphrase)

        self._verifyAddress(suppliedAddress)
        suppliedAddress = addBMIfNotPresent(suppliedAddress)
        queues.apiAddressGeneratorReturnQueue.queue.clear()
        queues.addressGeneratorQueue.put((
            'joinChan', suppliedAddress, label, passphrase, True
        ))
        queueReturn = queues.apiAddressGeneratorReturnQueue.get()
        try:
            if queueReturn[0] == 'chan name does not match address':
                raise APIError(18, 'Chan name does not match address.')
        except IndexError:
            raise APIError(24, 'Chan address is already present.')

        return "success"

    @command('leaveChan')
    def HandleLeaveChan(self, address):
        """Handle a request to leave a chan"""
        self._verifyAddress(address)
        address = addBMIfNotPresent(address)
        if not BMConfigParser().safeGetBoolean(address, 'chan'):
            raise APIError(
                25, 'Specified address is not a chan address.'
                ' Use deleteAddress API call instead.')
        try:
            BMConfigParser().remove_section(address)
        except ConfigParser.NoSectionError:
            raise APIError(
                13, 'Could not find this address in your keys.dat file.')
        BMConfigParser().save()
        queues.UISignalQueue.put(('rerenderMessagelistFromLabels', ''))
        queues.UISignalQueue.put(('rerenderMessagelistToLabels', ''))
        return "success"

    @command('deleteAddress')
    def HandleDeleteAddress(self, address):
        """Handle a request to delete an address"""
        self._verifyAddress(address)
        address = addBMIfNotPresent(address)
        try:
            BMConfigParser().remove_section(address)
        except ConfigParser.NoSectionError:
            raise APIError(
                13, 'Could not find this address in your keys.dat file.')
        BMConfigParser().save()
        queues.UISignalQueue.put(('writeNewAddressToTable', ('', '', '')))
        shared.reloadMyAddressHashes()
        return "success"

    @command('getAllInboxMessages')
    def HandleGetAllInboxMessages(self):
        """Handle a request to get all inbox messages"""

        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, received, message,"
            " encodingtype, read FROM inbox WHERE folder='inbox'"
            " ORDER BY received"
        )
        return {"inboxMessages": [
            self._dump_inbox_message(*data) for data in queryreturn
        ]}

    @command('getAllInboxMessageIds', 'getAllInboxMessageIDs')
    def HandleGetAllInboxMessageIds(self):
        """Handle a request to get all inbox message IDs"""

        queryreturn = sqlQuery(
            "SELECT msgid FROM inbox where folder='inbox' ORDER BY received")

        return {"inboxMessageIds": [
            {'msgid': hexlify(msgid)} for msgid, in queryreturn
        ]}

    @command('getInboxMessageById', 'getInboxMessageByID')
    def HandleGetInboxMessageById(self, hid, readStatus=None):
        """Handle a request to get an inbox messsage by ID"""

        msgid = self._decode(hid, "hex")
        if readStatus is not None:
            if not isinstance(readStatus, bool):
                raise APIError(
                    23, 'Bool expected in readStatus, saw %s instead.' %
                    type(readStatus))
            queryreturn = sqlQuery(
                "SELECT read FROM inbox WHERE msgid=?", msgid)
            # UPDATE is slow, only update if status is different
            try:
                if (queryreturn[0][0] == 1) != readStatus:
                    sqlExecute(
                        "UPDATE inbox set read = ? WHERE msgid=?",
                        readStatus, msgid)
                    queues.UISignalQueue.put(('changedInboxUnread', None))
            except IndexError:
                pass
        queryreturn = sqlQuery(
            "SELECT toaddress, fromaddress, subject, received, message,"
            " encodingtype, read FROM inbox WHERE msgid=?", msgid
        )
        try:
            return {"inboxMessage": [
                self._dump_inbox_message(*queryreturn[0])]}
        except IndexError:
            pass  # FIXME inconsistent

    @command('getAllSentMessages')
    def HandleGetAllSentMessages(self):
        """Handle a request to get all sent messages"""

        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, lastactiontime,"
            " message, encodingtype, status, ackdata FROM sent"
            " WHERE folder='sent' ORDER BY lastactiontime"
        )
        return {"sentMessages": [
            self._dump_sent_message(*data) for data in queryreturn
        ]}

    @command('getAllSentMessageIds', 'getAllSentMessageIDs')
    def HandleGetAllSentMessageIds(self):
        """Handle a request to get all sent message IDs"""

        queryreturn = sqlQuery(
            "SELECT msgid FROM sent WHERE folder='sent'"
            " ORDER BY lastactiontime"
        )
        return {"sentMessageIds": [
            {'msgid': hexlify(msgid)} for msgid, in queryreturn
        ]}

    # after some time getInboxMessagesByAddress should be removed
    @command('getInboxMessagesByReceiver', 'getInboxMessagesByAddress')
    def HandleInboxMessagesByReceiver(self, toAddress):
        """Handle a request to get inbox messages by receiver"""

        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, received,"
            " message, encodingtype, read FROM inbox WHERE folder='inbox'"
            " AND toAddress=?", toAddress)
        return {"inboxMessages": [
            self._dump_inbox_message(*data) for data in queryreturn
        ]}

    @command('getSentMessageById', 'getSentMessageByID')
    def HandleGetSentMessageById(self, hid):
        """Handle a request to get a sent message by ID"""

        msgid = self._decode(hid, "hex")
        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, lastactiontime,"
            " message, encodingtype, status, ackdata FROM sent WHERE msgid=?",
            msgid
        )
        try:
            return {"sentMessage": [
                self._dump_sent_message(*queryreturn[0])
            ]}
        except IndexError:
            pass  # FIXME inconsistent

    @command('getSentMessagesByAddress', 'getSentMessagesBySender')
    def HandleGetSentMessagesByAddress(self, fromAddress):
        """Handle a request to get sent messages by address"""

        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, lastactiontime,"
            " message, encodingtype, status, ackdata FROM sent"
            " WHERE folder='sent' AND fromAddress=? ORDER BY lastactiontime",
            fromAddress
        )
        return {"sentMessages": [
            self._dump_sent_message(*data) for data in queryreturn
        ]}

    @command('getSentMessageByAckData')
    def HandleGetSentMessagesByAckData(self, ackData):
        """Handle a request to get sent messages by ack data"""

        ackData = self._decode(ackData, "hex")
        queryreturn = sqlQuery(
            "SELECT msgid, toaddress, fromaddress, subject, lastactiontime,"
            " message, encodingtype, status, ackdata FROM sent"
            " WHERE ackdata=?", ackData
        )

        try:
            return {"sentMessage": [
                self._dump_sent_message(*queryreturn[0])
            ]}
        except IndexError:
            pass  # FIXME inconsistent

    @command('trashMessage')
    def HandleTrashMessage(self, msgid):
        """Handle a request to trash a message by ID"""
        msgid = self._decode(msgid, "hex")
        # Trash if in inbox table
        helper_inbox.trash(msgid)
        # Trash if in sent table
        sqlExecute("UPDATE sent SET folder='trash' WHERE msgid=?", msgid)
        return 'Trashed message (assuming message existed).'

    @command('trashInboxMessage')
    def HandleTrashInboxMessage(self, msgid):
        """Handle a request to trash an inbox message by ID"""
        msgid = self._decode(msgid, "hex")
        helper_inbox.trash(msgid)
        return 'Trashed inbox message (assuming message existed).'

    @command('trashSentMessage')
    def HandleTrashSentMessage(self, msgid):
        """Handle a request to trash a sent message by ID"""
        msgid = self._decode(msgid, "hex")
        sqlExecute('''UPDATE sent SET folder='trash' WHERE msgid=?''', msgid)
        return 'Trashed sent message (assuming message existed).'

    @command('sendMessage')
    def HandleSendMessage(
        self, toAddress, fromAddress, subject, message,
        encodingType=2, TTL=4 * 24 * 60 * 60
    ):
        """Handle a request to send a message"""

        if encodingType not in (2, 3):
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
        streamNumber, toRipe = self._verifyAddress(toAddress)[2:]
        self._verifyAddress(fromAddress)
        try:
            fromAddressEnabled = BMConfigParser().getboolean(
                fromAddress, 'enabled')
        except BaseException:
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
        try:
            toLabel, = queryreturn[0][0]
        except IndexError:
            pass

        queues.UISignalQueue.put(('displayNewSentMessage', (
            toAddress, toLabel, fromAddress, subject, message, ackdata)))
        queues.workerQueue.put(('sendmessage', toAddress))

        return hexlify(ackdata)

    @command('sendBroadcast')
    def HandleSendBroadcast(
        self, fromAddress, subject, message, encodingType=2,
            TTL=4 * 24 * 60 * 60):
        """Handle a request to send a broadcast message"""

        if encodingType not in (2, 3):
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
        except BaseException:
            raise APIError(
                13, 'could not find your fromAddress in the keys.dat file.')
        streamNumber = decodeAddress(fromAddress)[2]
        ackdata = genAckPayload(streamNumber, 0)
        toAddress = str_broadcast_subscribers
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

        toLabel = str_broadcast_subscribers
        queues.UISignalQueue.put(('displayNewSentMessage', (
            toAddress, toLabel, fromAddress, subject, message, ackdata)))
        queues.workerQueue.put(('sendbroadcast', ''))

        return hexlify(ackdata)

    @command('getStatus')
    def HandleGetStatus(self, ackdata):
        """Handle a request to get the status of a sent message"""

        if len(ackdata) < 76:
            # The length of ackData should be at least 38 bytes (76 hex digits)
            raise APIError(15, 'Invalid ackData object size.')
        ackdata = self._decode(ackdata, "hex")
        queryreturn = sqlQuery(
            "SELECT status FROM sent where ackdata=?", ackdata)
        try:
            return queryreturn[0][0]
        except IndexError:
            return 'notfound'

    @command('addSubscription')
    def HandleAddSubscription(self, address, label=''):
        """Handle a request to add a subscription"""

        if label:
            label = self._decode(label, "base64")
            try:
                unicode(label, 'utf-8')
            except UnicodeDecodeError:
                raise APIError(17, 'Label is not valid UTF-8 data.')
        self._verifyAddress(address)
        address = addBMIfNotPresent(address)
        # First we must check to see if the address is already in the
        # subscriptions list.
        queryreturn = sqlQuery(
            "SELECT * FROM subscriptions WHERE address=?", address)
        if queryreturn:
            raise APIError(16, 'You are already subscribed to that address.')
        sqlExecute(
            "INSERT INTO subscriptions VALUES (?,?,?)", label, address, True)
        shared.reloadBroadcastSendersForWhichImWatching()
        queues.UISignalQueue.put(('rerenderMessagelistFromLabels', ''))
        queues.UISignalQueue.put(('rerenderSubscriptions', ''))
        return 'Added subscription.'

    @command('deleteSubscription')
    def HandleDeleteSubscription(self, address):
        """Handle a request to delete a subscription"""

        address = addBMIfNotPresent(address)
        sqlExecute("DELETE FROM subscriptions WHERE address=?", address)
        shared.reloadBroadcastSendersForWhichImWatching()
        queues.UISignalQueue.put(('rerenderMessagelistFromLabels', ''))
        queues.UISignalQueue.put(('rerenderSubscriptions', ''))
        return 'Deleted subscription if it existed.'

    @command('listSubscriptions')
    def ListSubscriptions(self):
        """Handle a request to list susbcriptions"""

        queryreturn = sqlQuery(
            "SELECT label, address, enabled FROM subscriptions")
        data = []
        for label, address, enabled in queryreturn:
            label = shared.fixPotentiallyInvalidUTF8Data(label)
            data.append({
                'label': base64.b64encode(label),
                'address': address,
                'enabled': enabled == 1
            })
        return {'subscriptions': data}

    @command('disseminatePreEncryptedMsg')
    def HandleDisseminatePreEncryptedMsg(
        self, encryptedPayload, requiredAverageProofOfWorkNonceTrialsPerByte,
            requiredPayloadLengthExtraBytes):
        """Handle a request to disseminate an encrypted message"""

        # The device issuing this command to PyBitmessage supplies a msg
        # object that has already been encrypted but which still needs the POW
        # to be done. PyBitmessage accepts this msg object and sends it out
        # to the rest of the Bitmessage network as if it had generated
        # the message itself. Please do not yet add this to the api doc.
        encryptedPayload = self._decode(encryptedPayload, "hex")
        # Let us do the POW and attach it to the front
        target = 2**64 / ((
            len(encryptedPayload) + requiredPayloadLengthExtraBytes + 8) *
            requiredAverageProofOfWorkNonceTrialsPerByte)
        logger.info(
            '(For msg message via API) Doing proof of work. Total  required'
            ' difficulty: %s\nRequired small message difficulty: %s',
            float(requiredAverageProofOfWorkNonceTrialsPerByte) /
            defaults.networkDefaultProofOfWorkNonceTrialsPerByte,
            float(requiredPayloadLengthExtraBytes) /
            defaults.networkDefaultPayloadLengthExtraBytes,
        )
        powStartTime = time.time()
        initialHash = hashlib.sha512(encryptedPayload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        logger.info(
            '(For msg message via API) Found proof of work %s\nNonce: %s\n'
            'POW took %s seconds. %s nonce trials per second.',
            trialValue, nonce, int(time.time() - powStartTime),
            nonce / (time.time() - powStartTime)
        )
        encryptedPayload = pack('>Q', nonce) + encryptedPayload
        toStreamNumber = decodeVarint(encryptedPayload[16:26])[0]
        inventoryHash = calculateInventoryHash(encryptedPayload)
        objectType = 2
        TTL = 2.5 * 24 * 60 * 60
        Inventory()[inventoryHash] = (
            objectType, toStreamNumber, encryptedPayload,
            int(time.time()) + TTL, ''
        )
        logger.info(
            'Broadcasting inv for msg(API disseminatePreEncryptedMsg'
            ' command): %s', hexlify(inventoryHash))
        queues.invQueue.put((toStreamNumber, inventoryHash))

    @command('trashSentMessageByAckData')
    def HandleTrashSentMessageByAckDAta(self, ackdata):
        """Handle a request to trash a sent message by ackdata"""
        # This API method should only be used when msgid is not available
        ackdata = self._decode(ackdata, "hex")
        sqlExecute("UPDATE sent SET folder='trash' WHERE ackdata=?", ackdata)
        return 'Trashed sent message (assuming message existed).'

    @command('disseminatePubkey')
    def HandleDissimatePubKey(self, payload):
        """Handle a request to disseminate a public key"""

        # The device issuing this command to PyBitmessage supplies a pubkey
        # object to be disseminated to the rest of the Bitmessage network.
        # PyBitmessage accepts this pubkey object and sends it out to the rest
        # of the Bitmessage network as if it had generated the pubkey object
        # itself. Please do not yet add this to the api doc.
        payload = self._decode(payload, "hex")

        # Let us do the POW
        target = 2 ** 64 / ((
            len(payload) + defaults.networkDefaultPayloadLengthExtraBytes + 8
        ) * defaults.networkDefaultProofOfWorkNonceTrialsPerByte)
        logger.info('(For pubkey message via API) Doing proof of work...')
        initialHash = hashlib.sha512(payload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        logger.info(
            '(For pubkey message via API) Found proof of work %s Nonce: %s',
            trialValue, nonce
        )
        payload = pack('>Q', nonce) + payload

        pubkeyReadPosition = 8  # bypass the nonce
        if payload[pubkeyReadPosition:pubkeyReadPosition + 4] == \
                '\x00\x00\x00\x00':  # if this pubkey uses 8 byte time
            pubkeyReadPosition += 8
        else:
            pubkeyReadPosition += 4
        addressVersionLength = decodeVarint(
            payload[pubkeyReadPosition:pubkeyReadPosition + 10])[1]
        pubkeyReadPosition += addressVersionLength
        pubkeyStreamNumber = decodeVarint(
            payload[pubkeyReadPosition:pubkeyReadPosition + 10])[0]
        inventoryHash = calculateInventoryHash(payload)
        objectType = 1  # .. todo::: support v4 pubkeys
        TTL = 28 * 24 * 60 * 60
        Inventory()[inventoryHash] = (
            objectType, pubkeyStreamNumber, payload, int(time.time()) + TTL, ''
        )
        logger.info(
            'broadcasting inv within API command disseminatePubkey with'
            ' hash: %s', hexlify(inventoryHash))
        queues.invQueue.put((pubkeyStreamNumber, inventoryHash))

    @command(
        'getMessageDataByDestinationHash', 'getMessageDataByDestinationTag')
    def HandleGetMessageDataByDestinationHash(self, requestedHash):
        """Handle a request to get message data by destination hash"""

        # Method will eventually be used by a particular Android app to
        # select relevant messages. Do not yet add this to the api
        # doc.
        if len(requestedHash) != 32:
            raise APIError(
                19, 'The length of hash should be 32 bytes (encoded in hex'
                ' thus 64 characters).')
        requestedHash = self._decode(requestedHash, "hex")

        # This is not a particularly commonly used API function. Before we
        # use it we'll need to fill out a field in our inventory database
        # which is blank by default (first20bytesofencryptedmessage).
        queryreturn = sqlQuery(
            "SELECT hash, payload FROM inventory WHERE tag = ''"
            " and objecttype = 2")
        with SqlBulkExecute() as sql:
            for hash01, payload in queryreturn:
                readPosition = 16  # Nonce length + time length
                # Stream Number length
                readPosition += decodeVarint(
                    payload[readPosition:readPosition + 10])[1]
                t = (payload[readPosition:readPosition + 32], hash01)
                sql.execute("UPDATE inventory SET tag=? WHERE hash=?", *t)

        queryreturn = sqlQuery(
            "SELECT payload FROM inventory WHERE tag = ?", requestedHash)
        return {"receivedMessageDatas": [
            {'data': hexlify(payload)} for payload, in queryreturn
        ]}

    @command('clientStatus')
    def HandleClientStatus(self):
        """Handle a request to get the status of the client"""

        connections_num = len(network.stats.connectedHostsList())
        if connections_num == 0:
            networkStatus = 'notConnected'
        elif state.clientHasReceivedIncomingConnections:
            networkStatus = 'connectedAndReceivingIncomingConnections'
        else:
            networkStatus = 'connectedButHaveNotReceivedIncomingConnections'
        return {
            'networkConnections': connections_num,
            'numberOfMessagesProcessed': state.numberOfMessagesProcessed,
            'numberOfBroadcastsProcessed': state.numberOfBroadcastsProcessed,
            'numberOfPubkeysProcessed': state.numberOfPubkeysProcessed,
            'networkStatus': networkStatus,
            'softwareName': 'PyBitmessage',
            'softwareVersion': softwareVersion
        }

    @command('decodeAddress')
    def HandleDecodeAddress(self, address):
        """Handle a request to decode an address"""
        # Return a meaningful decoding of an address.
        status, addressVersion, streamNumber, ripe = decodeAddress(address)
        return {
            'status': status,
            'addressVersion': addressVersion,
            'streamNumber': streamNumber,
            'ripe': base64.b64encode(ripe)
        }

    @command('helloWorld')
    def HandleHelloWorld(self, a, b):
        """Test two string params"""
        return a + '-' + b

    @command('add')
    def HandleAdd(self, a, b):
        """Test two numeric params"""
        return a + b

    @command('statusBar')
    def HandleStatusBar(self, message):
        """Handle a request to update the status bar"""
        queues.UISignalQueue.put(('updateStatusBar', message))

    @command('deleteAndVacuum')
    def HandleDeleteAndVacuum(self):
        """Handle a request to run the deleteandvacuum stored procedure"""
        sqlStoredProcedure('deleteandvacuume')
        return 'done'

    @command('shutdown')
    def HandleShutdown(self):
        """Handle a request to shutdown the node"""
        # backward compatible trick because False == 0 is True
        state.shutdown = False
        return 'done'

    def _handle_request(self, method, params):
        try:
            # pylint: disable=attribute-defined-outside-init
            self._method = method
            return self._handlers[method](self, *params)
        except KeyError:
            raise APIError(20, 'Invalid method: %s' % method)
        finally:
            state.last_api_response = time.time()

    def _dispatch(self, method, params):
        # pylint: disable=attribute-defined-outside-init
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
