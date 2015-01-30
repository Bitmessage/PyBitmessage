import shared
import time
import hashlib

# Classes
from helper_sql import sqlQuery,sqlExecute,SqlBulkExecute
from debug import logger

# Helper Functions
import proofofwork

from addresses import decodeAddress,addBMIfNotPresent,decodeVarint,calculateInventoryHash,varintDecodeError
import helper_inbox
import helper_sent
from pyelliptic.openssl import OpenSSL

str_chan = '[chan]'

class Message:
    def __init__(self, query):
        self.data = []

class Sent( Message ):
    def __init__( self, query ):
        super( Sent, self).__init__()
        # lastactiontime, status, ackdata = query[6:8]
        for entry in query:
            self.data.append({
            'msgid':entry[0].encode(),
            'toAddress':entry[1],
            'fromAddress':entry[2],
            'subject':entry[3].encode(),
            'message':entry[4].encode(),
            'encodingType':entry[5],
            'lastactiontime':lastactiontime,
            'status':status,
            'ackdata': ackdata.endcode("hex"),
            })

class Recieved( Message ):
    def __init__( self, query ):
        super( Recieved, self ).__init__(query)
        for entry in query:
            self.data.append({
            'msgid':entry[0].encode(),
            'toAddress':entry[1],
            'fromAddress':entry[2],
            'subject':entry[3].encode(),
            'message':entry[4].encode(),
            'encodingType':entry[5],
            'receivedTime':entry[6],
            'read': entry[7],
            })

class _handle_request( object ):
    def ping( self, *args ):
        data = { 'pong': args }
        return 200, data

    def statusBar( self, *args ):
        message, = args
        shared.UISignalQueue.put( ('updateStatusBar', message) )
        return 200, True

    def listAddresses( self, *args ):
        data = []
        configSections = shared.config.sections()
        for addressInKeysFile in configSections:
            if addressInKeysFile != 'bitmessagesettings':
                status, addressVersionNumber, streamNumber, hash01 = decodeAddress( addressInKeysFile )

                if shared.config.has_option( addressInKeysFile, 'chan' ):
                    chan = shared.config.getboolean( addressInKeysFile, 'chan' )
                else:
                    chan = False
                label = shared.config.get( addressInKeysFile, 'label' ).encode( 'base64' )

                data.append({
                    'label': label,
                    'address': addressInKeysFile,
                    'stream': streamNumber,
                    'enabled': shared.config.getboolean(addressInKeysFile, 'enabled'),
                    'chan': chan
                })
        return 200, data

    def listAddressBookEntries( self, *args ):
        queryreturn = sqlQuery( '''SELECT label, address from addressbook''' )
        data = []

        # if address book is empty, return nothing and stop for loop from firing.
        if not queryreturn: 
            return data

        for row in queryreturn:
            label, address = row
            label = shared.fixPotentiallyInvalidUTF8Data( label )
            data.append({
                'label':label.encode( 'base64' ),
                'address': address
            })

        return 200, data

    ''' test below this line '''

    def addAddressBookEntry( self, *args ): ## fix verifyAddress!
        if len( args ) != 2:
            return 0, "I need label and address"

        address, label = args
        label = self._decode( label, "base64" )
        address = addBMIfNotPresent( address )
        self._verifyAddress( address )
        queryreturn = sqlQuery( "SELECT address FROM addressbook WHERE address=?", address )

        if queryreturn != []:
            return 16, 'You already have this address in your address book.'

        sqlExecute( "INSERT INTO addressbook VALUES(?,?)", label, address )
        shared.UISignalQueue.put(('rerenderInboxFromLabels',''))
        shared.UISignalQueue.put(('rerenderSentToLabels',''))
        shared.UISignalQueue.put(('rerenderAddressBook',''))
        return 200, address

    def deleteAddressBookEntry( self, *args ): ## fix verifyAddress!
        if len( args ) != 1:
            return 0, 'I need an address'

        address, = args
        address = addBMIfNotPresent(address)
        self._verifyAddress(address)
        sqlExecute('DELETE FROM addressbook WHERE address=?', address)
        shared.UISignalQueue.put(('rerenderInboxFromLabels',''))
        shared.UISignalQueue.put(('rerenderSentToLabels',''))
        shared.UISignalQueue.put(('rerenderAddressBook',''))
        return 200, "Deleted address book entry for %s if it existed" % address

    ''' not tested above this line '''
    def createRandomAddress( self, *args ):
        if not args:
            return 0, 'I need parameters!'

        if len( args ) == 1:
            label, = args
            eighteenByteRipe = False
            nonceTrialsPerByte = shared.config.get(
                'bitmessagesettings',
                'defaultnoncetrialsperbyte'
            )
            payloadLengthExtraBytes = shared.config.get(
                'bitmessagesettings',
                'defaultpayloadlengthextrabytes'
            )
        elif len( args ) == 2:

            label, eighteenByteRipe = args
            nonceTrialsPerByte = shared.config.get(
                'bitmessagesettings',
                'defaultnoncetrialsperbyte'
            )
            payloadLengthExtraBytes = shared.config.get(
                'bitmessagesettings',
                'defaultpayloadlengthextrabytes'
            )
        elif len( args ) == 3:
            label, eighteenByteRipe, totalDifficulty = args
            nonceTrialsPerByte = int(
                shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
            payloadLengthExtraBytes = shared.config.get(
                'bitmessagesettings',
                'defaultpayloadlengthextrabytes'
            )
        elif len( args ) == 4:
            label, eighteenByteRipe, totalDifficulty, smallMessageDifficulty = args
            nonceTrialsPerByte = int(
                shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
            payloadLengthExtraBytes = int(
                shared.networkDefaultPayloadLengthExtraBytes * smallMessageDifficulty)
        else:
            return 0, 'Too many parameters!'

        label = self._decode(label, "base64")
        try:
            unicode(label, 'utf-8')
        except:
            return 17, 'Label is not valid UTF-8 data.'

        shared.apiAddressGeneratorReturnQueue.queue.clear()
        streamNumberForAddress = 1
        shared.addressGeneratorQueue.put((
            'createRandomAddress',
            4,
            streamNumberForAddress,
            label,
            1,
            "",
            eighteenByteRipe,
            nonceTrialsPerByte,
            payloadLengthExtraBytes
        ))

        data = {
            'address': shared.apiAddressGeneratorReturnQueue.get(),
            'label': label
        }
        return 200, data

    def createDeterministicAddresses( self, *args ): # needs to be tested
        if not args:
            return 0, 'I need parameters!'

        if len( args ) == 1:
            passphrase, = args
            numberOfAddresses = 1
            addressVersionNumber = 0
            streamNumber = 0
            eighteenByteRipe = False
            nonceTrialsPerByte = shared.config.get(
                'bitmessagesettings',
                'defaultnoncetrialsperbyte'
            )
            payloadLengthExtraBytes = shared.config.get(
                'bitmessagesettings',
                'defaultpayloadlengthextrabytes'
            )
        elif len( args ) == 2:
            passphrase, numberOfAddresses = args
            addressVersionNumber = 0
            streamNumber = 0
            eighteenByteRipe = False
            nonceTrialsPerByte = shared.config.get(
                'bitmessagesettings',
                'defaultnoncetrialsperbyte'
            )
            payloadLengthExtraBytes = shared.config.get(
                'bitmessagesettings',
                'defaultpayloadlengthextrabytes'
            )
        elif len( args ) == 3:
            passphrase, numberOfAddresses, addressVersionNumber = args
            streamNumber = 0
            eighteenByteRipe = False
            nonceTrialsPerByte = shared.config.get(
                'bitmessagesettings',
                'defaultnoncetrialsperbyte'
            )
            payloadLengthExtraBytes = shared.config.get(
                'bitmessagesettings',
                'defaultpayloadlengthextrabytes'
            )
        elif len( args ) == 4:
            passphrase, numberOfAddresses, addressVersionNumber, streamNumber = args
            eighteenByteRipe = False
            nonceTrialsPerByte = shared.config.get(
                'bitmessagesettings',
                'defaultnoncetrialsperbyte'
            )
            payloadLengthExtraBytes = shared.config.get(
                'bitmessagesettings',
                'defaultpayloadlengthextrabytes'
            )
        elif len( args ) == 5:
            passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe = args
            nonceTrialsPerByte = shared.config.get(
                'bitmessagesettings',
                'defaultnoncetrialsperbyte'
            )
            payloadLengthExtraBytes = shared.config.get(
                'bitmessagesettings',
                'defaultpayloadlengthextrabytes'
            )
        elif len( args ) == 6:
            passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe, totalDifficulty = args
            nonceTrialsPerByte = int(
                shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
            payloadLengthExtraBytes = shared.config.get(
                'bitmessagesettings',
                'defaultpayloadlengthextrabytes'
                )
        elif len( args ) == 7:
            passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe, totalDifficulty, smallMessageDifficulty = args
            nonceTrialsPerByte = int(
                shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
            payloadLengthExtraBytes = int(
                shared.networkDefaultPayloadLengthExtraBytes * smallMessageDifficulty)
        else:
            return 0, 'Too many parameters!'

        if len(passphrase) == 0:
            return 1, 'The specified passphrase is blank.'

        if not isinstance(eighteenByteRipe, bool):
            return 23, 'Bool expected in eighteenByteRipe, saw %s instead' % type(eighteenByteRipe)

        passphrase = self._decode(passphrase, "base64")
        if addressVersionNumber == 0:  # 0 means "just use the proper addressVersionNumber"
            addressVersionNumber = 4

        if addressVersionNumber != 3 and addressVersionNumber != 4:
            return 2, 'The address version number currently must be 3, 4, or 0 (which means auto-select). ' + addressVersionNumber + ' isn\'t supported.'
        
        if streamNumber == 0:  # 0 means "just use the most available stream"
            streamNumber = 1
        
        if streamNumber != 1:
            return 3, 'The stream number must be 1 (or 0 which means auto-select). Others aren\'t supported.'

        if numberOfAddresses == 0:
            return 4, 'Why would you ask me to generate 0 addresses for you?'

        if numberOfAddresses > 999:
            return 5, 'You have (accidentally?) specified too many addresses to make. Maximum 999. This check only exists to prevent mischief; if you really want to create more addresses than this, contact the Bitmessage developers and we can modify the check or you can do it yourself by searching the source code for this message.'

        shared.apiAddressGeneratorReturnQueue.queue.clear()
        logger.debug('Requesting that the addressGenerator create %s addresses.', numberOfAddresses)
        shared.addressGeneratorQueue.put((
            'createDeterministicAddresses',
            addressVersionNumber,
            streamNumber,
            'unused API address',
            numberOfAddresses,
            passphrase,
            eighteenByteRipe,
            nonceTrialsPerByte,
            payloadLengthExtraBytes
        ))
        data = []
        queueReturn = shared.apiAddressGeneratorReturnQueue.get()
        for item in queueReturn:
            data.append( item )

        return 200, data

    def getDeterministicAddress( self, *args ): # needs to be tested
        if len( args ) != 3:
            return 0, 'I need exactly 3 parameters.'

        passphrase, addressVersionNumber, streamNumber = args
        numberOfAddresses = 1
        eighteenByteRipe = False

        if len( passphrase ) == 0:
            return 1, 'The specified passphrase is blank.'

        passphrase = self._decode(passphrase, "base64")
        if addressVersionNumber != 3 and addressVersionNumber != 4:
            return 2, 'The address version number currently must be 3 or 4. ' + addressVersionNumber + ' isn\'t supported.'
        
        if streamNumber != 1:
            return 3, ' The stream number must be 1. Others aren\'t supported.'

        shared.apiAddressGeneratorReturnQueue.queue.clear()
        logger.debug('Requesting that the addressGenerator create %s addresses.', numberOfAddresses)
        shared.addressGeneratorQueue.put((
            'getDeterministicAddress',
            addressVersionNumber,
            streamNumber,
            'unused API address',
            numberOfAddresses,
            passphrase,
            eighteenByteRipe
        ))
        return 200, shared.apiAddressGeneratorReturnQueue.get()

    def createChan( self, *args ):
        if not args:
            return 0, 'I need parameters.'

        if len( args ) == 1:
            passphrase, = args

        passphrase = self._decode( passphrase, "base64" )
        if len( passphrase ) == 0:
            return 1, 'The specified passphrase is blank.'
        # It would be nice to make the label the passphrase but it is
        # possible that the passphrase contains non-utf-8 characters. -wtf!
        try:
            unicode( passphrase, 'utf-8' )
            label = str_chan + ' ' + passphrase
        except:
            label = str_chan + ' ' + repr( passphrase )

        addressVersionNumber = 4
        streamNumber = 1
        shared.apiAddressGeneratorReturnQueue.queue.clear()
        logger.debug('Requesting that the addressGenerator create chan %s.', passphrase)
        shared.addressGeneratorQueue.put((
            'createChan',
            addressVersionNumber,
            streamNumber,
            label,
            passphrase
        ))
        queueReturn = shared.apiAddressGeneratorReturnQueue.get()
        if len(queueReturn) == 0:
            return 24, 'Chan address is already present.'
        address = queueReturn[0]
        data = {
            'address': address,
            'label': label
        }
        return 200, data

    def joinChan( self, *args ):
        if len( args ) != 2:
            return 0, 'I need two parameters.'

        passphrase, suppliedAddress = args
        passphrase = self._decode( passphrase, "base64" )

        if len( passphrase ) == 0:
            return 1, 'The specified passphrase is blank.'

        # It would be nice to make the label the passphrase but it is
        # possible that the passphrase contains non-utf-8 characters.
        try:
            unicode( passphrase, 'utf-8' )
            label = str_chan + ' ' + passphrase
        except:
            label = str_chan + ' ' + repr( passphrase )

        status, addressVersionNumber, streamNumber, toRipe = self._verifyAddress(suppliedAddress)
        suppliedAddress = addBMIfNotPresent(suppliedAddress)
        shared.apiAddressGeneratorReturnQueue.queue.clear()
        shared.addressGeneratorQueue.put(('joinChan', suppliedAddress, label, passphrase))
        addressGeneratorReturnValue = shared.apiAddressGeneratorReturnQueue.get()

        if addressGeneratorReturnValue == 'chan name does not match address':
            return 18, 'Chan name does not match address.'

        if len(addressGeneratorReturnValue) == 0:
            return 24, 'Chan address is already present.'
        
        data ={
            #TODO: this variable is not used to anything
            'createdAddress': addressGeneratorReturnValue[0] # in case we ever want it for anything.
        }
        return 200, data

    def leaveChan( self, *args ):
        if len( args ) != 1:
            return 0, 'I need parameters.'

        address, = args
        status, addressVersionNumber, streamNumber, toRipe = self._verifyAddress(address)
        address = addBMIfNotPresent(address)

        if not shared.config.has_section(address):
            return 13, 'Could not find this address in your keys.dat file.'

        if not shared.safeConfigGetBoolean(address, 'chan'):
            return 25, 'Specified address is not a chan address. Use deleteAddress API call instead.'

        shared.config.remove_section(address)
        shared.writeKeysFile()

        return 200, {}

    def deleteAddress( self, *args ):
        if len( args ) != 0:
            return 0, 'I need parameters.'

        address, = args
        status, addressVersionNumber, streamNumber, toRipe = self._verifyAddress( address )
        address = addBMIfNotPresent( address )
        if not shared.config.has_section(address):
            return 13, 'Could not find this address in your keys.dat file.'

        shared.config.remove_section(address)
        shared.writeKeysFile()
        shared.UISignalQueue.put(('rerenderInboxFromLabels',''))
        shared.UISignalQueue.put(('rerenderSentToLabels',''))
        shared.reloadMyAddressHashes()

        return 200, {}

    def getAllInboxMessages( self, *args ):
        queryreturn = sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype, read FROM inbox where folder='inbox' ORDER BY received''')
        # data = rowMessage( queryreturn )
        print queryreturn
        return 200, queryreturn

    # def getAllInboxMessageIDs( self, *args ):
    #     queryreturn = sqlQuery(
    #         '''SELECT msgid FROM inbox where folder='inbox' ORDER BY received''')
    #     data = []
    #     for row in queryreturn:
    #         msgid = row[0]
    #         data.append({
    #             'msgid': msgid.encode('hex')
    #         })

    #     return 200, data

    # def getInboxMessageByID( self, *args ):
    #     if len( args ) not in range(1,2):
    #         return 0, 'I need parameters!'

    #     if len(args) == 1:
    #         msgid = self._decode(args[0], "hex")
    #     elif len(args) >= 2:
    #         msgid = self._decode(args[0], "hex")
    #         readStatus = args[1]
    #         if not isinstance(readStatus, bool):
    #             return 23, 'Bool expected in readStatus, saw %s instead.' % type(readStatus)

    #         queryreturn = sqlQuery('''SELECT read FROM inbox WHERE msgid=?''', msgid)
    #         # UPDATE is slow, only update if status is different
    #         if queryreturn != [] and (queryreturn[0][0] == 1) != readStatus:
    #             sqlExecute('''UPDATE inbox set read = ? WHERE msgid=?''', readStatus, msgid)
    #             shared.UISignalQueue.put(('changedInboxUnread', None))

    #     queryreturn = sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype, read FROM inbox WHERE msgid=?''', msgid)
    #     data = rowMessage( queryreturn )

    #     return 200, data

    # def getAllSentMessages( self, *args ):
    #     queryreturn = sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent where folder='sent' ORDER BY lastactiontime''')
    #     data = []
    #     for row in queryreturn:
    #         msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
    #         subject = shared.fixPotentiallyInvalidUTF8Data(subject)
    #         message = shared.fixPotentiallyInvalidUTF8Data(message)
    #         data.append({
    #             'msgid':msgid.encode('hex'),
    #             'toAddress':toAddress,
    #             'fromAddress':fromAddress,
    #             'subject':subject.encode('base64'),
    #             'message':message.encode('base64'),
    #             'encodingType':encodingtype,
    #             'lastActionTime':lastactiontime,
    #             'status':status,
    #             'ackData':ackdata.encode('hex')
    #         })
    #     return 200, data

    # def getAllSentMessageIDs( self, *args ): # undocumented
    #     queryreturn = sqlQuery('''SELECT msgid FROM sent where folder='sent' ORDER BY lastactiontime''')
    #     data = []
    #     for row in queryreturn:
    #         msgid = row[0]
    #         data.append({ 'msgid':msgid.encode('hex') })

    #     return 200, data

    # def getInboxMessagesByToAddress( self, *args ): # renamed from getInboxMessagesByReceiver / undocumented
    #     if len( args ) == 0:
    #         return 0, 'I need parameters!'

    #     toAddress = args[0]
    #     queryreturn = sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype, read FROM inbox WHERE folder='inbox' AND toAddress=?''', toAddress)
    #     data = rowMessage( queryreturn )
    #     return 200, data

    # def getSentMessagesBySender( self, *args ):
    #         if len( args ) == 0:
    #             return 0, 'I need parameters!'
    #         fromAddress = args[0]
    #         queryreturn = sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE folder='sent' AND fromAddress=? ORDER BY lastactiontime''',
    #                                fromAddress)
    #         data = []
    #         for row in queryreturn:
    #             msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
    #             subject = shared.fixPotentiallyInvalidUTF8Data(subject)
    #             message = shared.fixPotentiallyInvalidUTF8Data(message)
    #             data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')}, indent=4, separators=(',', ': '))
    #         return data

    # def getSentMessageByID( self, *args ):
    #     if len( args ) == 0:
    #         return 0, 'I need parameters!'

    #     msgid = self._decode( args[0], "hex")
    #     queryreturn = sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE msgid=?''', msgid)
    #     data = []
    #     for row in queryreturn:
    #         msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
    #         subject = shared.fixPotentiallyInvalidUTF8Data(subject)
    #         message = shared.fixPotentiallyInvalidUTF8Data(message)
    #         data.append({
    #             'msgid':msgid.encode('hex'),
    #             'toAddress':toAddress,
    #             'fromAddress':fromAddress,
    #             'subject':subject.encode('base64'),
    #             'message':message.encode('base64'),
    #             'encodingType':encodingtype,
    #             'lastActionTime':lastactiontime,
    #             'status':status,
    #             'ackData':ackdata.encode('hex')
    #         })

    #     return 200, data

    # def getSentMessageByAckData( self, *args ):
    #     if len( args ) == 0:
    #         return 0, 'I need parameters!'
    #     ackData = self._decode( args[0], "hex" )
    #     queryreturn = sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE ackdata=?''',
    #                            ackData)
    #     data = sentMessageRow( queryreturn )
    #     return data

    #  def trashMessage( self, *args ):
    #     if len( args ) == 0:
    #         return 0, 'I need parameters!'
    #     msgid = self._decode(args[0], "hex")

    #     # Trash if in inbox table
    #     helper_inbox.trash(msgid)
    #     # Trash if in sent table
    #     sqlExecute('''UPDATE sent SET folder='trash' WHERE msgid=?''', msgid)
    #     return 200, 'Trashed message (assuming message existed).'

    # def trashInboxMessage( self, *args ):
    #     if len( args ) == 0:
    #         return 0, 'I need parameters!'
    #     msgid = self._decode(args[0], "hex")
    #     helper_inbox.trash(msgid)
    #     return 200, 'Trashed inbox message (assuming message existed).'

    # def trashInboxMessage( self, *args ):
    #     if len( args ) == 0:
    #         return 0, 'I need parameters!'
    #     msgid = self._decode(args[0], "hex")
    #     helper_inbox.trash(msgid)
    #     return 200, 'Trashed inbox message (assuming message existed).'

    # def trashSentMessage( self, *args ):
    #     if len( args ) == 0:
    #         return 0, 'I need parameters!'
    #     msgid = self._decode(args[0], "hex")
    #     sqlExecute('''UPDATE sent SET folder='trash' WHERE msgid=?''', msgid)
    #     return 200, 'Trashed sent message (assuming message existed).'

    # def trashSentMessageByAckData( self, *args ):
    #     # This API method should only be used when msgid is not available
    #     if len( args ) == 0:
    #         return 0, 'I need parameters!'
    #     ackdata = self._decode(args[0], "hex")
    #     sqlExecute('''UPDATE sent SET folder='trash' WHERE ackdata=?''',
    #                ackdata)
    #     return 200, 'Trashed sent message (assuming message existed).'

    # def sendMessage( self, *args ):
    #     if len( args ) not in [4,5]:
    #         return 0, 'I need parameters!'

    #     elif len( args ) == 4:
    #         toAddress, fromAddress, subject, message = args
    #         encodingType = 2
    #     elif len( args ) == 5:
    #         toAddress, fromAddress, subject, message, encodingType = args

    #     if encodingType != 2:
    #         return 6, 'The encoding type must be 2 because that is the only one this program currently supports.'

    #     subject = self._decode(subject, "base64")
    #     message = self._decode(message, "base64")
    #     if len(subject + message) > (2 ** 18 - 500):
    #         return 27, 'Message is too long.'

    #     toAddress = addBMIfNotPresent(toAddress)
    #     fromAddress = addBMIfNotPresent(fromAddress)
    #     status, addressVersionNumber, streamNumber, toRipe = self._verifyAddress(toAddress)
    #     self._verifyAddress(fromAddress)
    #     try:
    #         fromAddressEnabled = shared.config.getboolean(
    #             fromAddress, 'enabled')
    #     except:
    #         return 13, 'Could not find your fromAddress in the keys.dat file.'

    #     if not fromAddressEnabled:
    #         return 14, 'Your fromAddress is disabled. Cannot send.'

    #     ackdata = OpenSSL.rand(32)

    #     t = ('', toAddress, toRipe, fromAddress, subject, message, ackdata, int(
    #         time.time()), 'msgqueued', 1, 1, 'sent', 2)
    #     helper_sent.insert(t)

    #     toLabel = ''
    #     queryreturn = sqlQuery('''select label from addressbook where address=?''', toAddress)
    #     if queryreturn != []:
    #         for row in queryreturn:
    #             toLabel, = row
    #     # apiSignalQueue.put(('displayNewSentMessage',(toAddress,toLabel,fromAddress,subject,message,ackdata)))
    #     shared.UISignalQueue.put(('displayNewSentMessage', (
    #         toAddress, toLabel, fromAddress, subject, message, ackdata)))

    #     shared.workerQueue.put(('sendmessage', toAddress))

    #     return 200, ackdata.encode('hex')

    # def sendBroadcast( self, *args ):
    #     if len(params) not in [3,4]:
    #         return 0, 'I need parameters!'

    #     if len( args ) == 3:
    #         fromAddress, subject, message = args
    #         encodingType = 2
    #     elif len(params) == 4:
    #         fromAddress, subject, message, encodingType = args

    #     if encodingType != 2:
    #         return 6, 'The encoding type must be 2 because that is the only one this program currently supports.'

    #     subject = self._decode(subject, "base64")
    #     message = self._decode(message, "base64")
    #     if len(subject + message) > (2 ** 18 - 500):
    #         return 27, 'Message is too long.'

    #     fromAddress = addBMIfNotPresent(fromAddress)
    #     self._verifyAddress(fromAddress)
    #     try:
    #         fromAddressEnabled = shared.config.getboolean(
    #             fromAddress, 'enabled')
    #     except:
    #         return 13, 'could not find your fromAddress in the keys.dat file.'

    #     ackdata = OpenSSL.rand(32)
    #     toAddress = '[Broadcast subscribers]'
    #     ripe = ''

    #     t = ('', toAddress, ripe, fromAddress, subject, message, ackdata, int(
    #         time.time()), 'broadcastqueued', 1, 1, 'sent', 2)
    #     helper_sent.insert(t)

    #     toLabel = '[Broadcast subscribers]'
    #     shared.UISignalQueue.put(('displayNewSentMessage', (
    #         toAddress, toLabel, fromAddress, subject, message, ackdata)))
    #     shared.workerQueue.put(('sendbroadcast', ''))

    #     return 200, ackdata.encode('hex')

    # def getStatus( self, *args ):
    #     if len( args ) != 1:
    #         return 0, 'I need one parameter!'

    #     ackdata, = args
    #     if len(ackdata) != 64:
    #         return 15, 'The length of ackData should be 32 bytes (encoded in hex thus 64 characters).'

    #     ackdata = self._decode(ackdata, "hex")
    #     queryreturn = sqlQuery(
    #         '''SELECT status FROM sent where ackdata=?''',
    #         ackdata)
    #     if queryreturn == []:
    #         return 404, 'notfound'
    #     for row in queryreturn:
    #         status, = row
    #         return 200, status

    # def addSubscription( self, *args ):
    #     if len( args ) not in [1,2]:
    #         return 0, 'I need parameters!'

    #     if len( args ) == 1:
    #         address, = args
    #         label = ''
    #     if len( args ) == 2:
    #         address, label = args
    #         label = self._decode(label, "base64")
    #         try:
    #             unicode(label, 'utf-8')
    #         except:
    #             return 17, 'Label is not valid UTF-8 data.'

    #     address = addBMIfNotPresent(address)
    #     self._verifyAddress(address)
    #     # First we must check to see if the address is already in the
    #     # subscriptions list.
    #     queryreturn = sqlQuery('''select * from subscriptions where address=?''', address)
    #     if queryreturn != []:
    #         return 16, 'You are already subscribed to that address.'
    #     sqlExecute('''INSERT INTO subscriptions VALUES (?,?,?)''',label, address, True)
    #     shared.reloadBroadcastSendersForWhichImWatching()
    #     shared.UISignalQueue.put(('rerenderInboxFromLabels', ''))
    #     shared.UISignalQueue.put(('rerenderSubscriptions', ''))
    #     return 200, 'Added subscription.'

    # def addAddressToBlackWhiteList( self, *args ):
    #     if len(params) not in [1,2]:
    #         return 0, 'I need parameters!'

    #     if len( args ) == 1:
    #         address, = args
    #         label = ''

    #     if len( args ) == 2:
    #         address, label = args
    #         label = self._decode(label, "base64")
    #         try:
    #             unicode(label, 'utf-8')
    #         except:
    #             return 17, 'Label is not valid UTF-8 data.'

    #     if len( args ) > 2:
    #         return 0, 'I need either 1 or 2 parameters!'

    #     address = addBMIfNotPresent(address)
    #     self._verifyAddress(address)

    #     table = ''
    #     if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
    #         table = 'blacklist'
    #     else:
    #         table = 'whitelist'

    #     # First we must check to see if the address is already in the
    #     # black-/white-list.
    #     queryreturn = sqlQuery('''select * from '''+table+''' where address=?''', address)
    #     if queryreturn != []:
    #         return 28, 'You have already black-/white-listed that address.'

    #     sqlExecute('''INSERT INTO '''+table+''' VALUES (?,?,?)''',label, address, True)
    #     shared.UISignalQueue.put(('rerenderBlackWhiteList', ''))

    #     return 200, 'Added black-/white-list entry.'

    # def removeAddressFromBlackWhiteList':
    #     if len( args ) != 1:
    #         return 0, 'I need 1 parameter!'

    #     address, = args
    #     address = addBMIfNotPresent(address)

    #     table = ''
    #     if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
    #         table = 'blacklist'
    #     else:
    #         table = 'whitelist'

    #     # First we must check to see if the address is already in the
    #     # black-/white-list.
    #     queryreturn = sqlQuery('''select * from '''+table+''' where address=?''', address)
    #     if queryreturn == []:
    #         return 29, 'That entry does not exist in the black-/white-list.'

    #     sqlExecute('''DELETE FROM '''+table+''' WHERE address=?''', address)
    #     shared.UISignalQueue.put(('rerenderBlackWhiteList', ''))
    #     return 200, 'Deleted black-/white-list entry if it existed.'

    # def deleteSubscription( self, *args):
    #     if len( args ) != 1:
    #         return 0, 'I need 1 parameter!'

    #     address, = args
    #     address = addBMIfNotPresent(address)
    #     sqlExecute('''DELETE FROM subscriptions WHERE address=?''', address)
    #     shared.reloadBroadcastSendersForWhichImWatching()
    #     shared.UISignalQueue.put(('rerenderInboxFromLabels', ''))
    #     shared.UISignalQueue.put(('rerenderSubscriptions', ''))
    #     return 200, 'Deleted subscription if it existed.'