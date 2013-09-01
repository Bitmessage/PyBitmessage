import os
import sys
import time

def getAPI(workingdir=None,silent=False):
    
    if workingdir:
        os.environ["BITMESSAGE_HOME"] = workingdir
    
    #Workaround while logging is not ready 
    if silent:
        import StringIO
        fobj = StringIO.StringIO()
        sys.stdout = fobj    
        
    import bitmessagemain
    class MainAPI(bitmessagemain.Main):
        
        def markInboxMessageAsRead(self,msgid):
            msgid = msgid.decode('hex')
            t = (msgid,)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''UPDATE inbox SET read='1' WHERE msgid=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlSubmitQueue.put('commit')
            bitmessagemain.shared.sqlLock.release()
            
        def markInboxMessageAsUnread(self,msgid):
            msgid = msgid.decode('hex')
            t = (msgid,)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''UPDATE inbox SET read='0' WHERE msgid=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlSubmitQueue.put('commit')
            bitmessagemain.shared.sqlLock.release()
        
        def getAllInboxMessages(self):
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put(
                '''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype, read FROM inbox where folder='inbox' ORDER BY received''')
            bitmessagemain.shared.sqlSubmitQueue.put('')
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            
            messages = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype, read = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                
                messages.append({'msgid': msgid.encode('hex'), 'toAddress': toAddress, 'fromAddress': fromAddress, 'subject': subject, 'message': message, 'encodingType': encodingtype, 'receivedTime': received, 'read': read})
            
            return messages
        
        
        def getAllInboxMessageIDs(self):
            
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''SELECT msgid FROM inbox where folder='inbox' ORDER BY received''')
            bitmessagemain.shared.sqlSubmitQueue.put('')
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            
            data = []
            for msgid in queryreturn:
                data.append(msgid[0].encode('hex'))
            return data

        def getInboxMessageByID(self, msgid):

            msgid = msgid.decode('hex')
            v = (msgid,)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype, read FROM inbox WHERE msgid=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(v)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype, read = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject, 'message':message, 'encodingType':encodingtype, 'receivedTime':received, 'read': read})

            return data

            
        def trashInboxMessage(self,msgid):

            msgid = msgid.decode('hex')
            bitmessagemain.helper_inbox.trash(msgid)


        def listAddresses(self):
            
            addresses = []
            configSections = bitmessagemain.shared.config.sections()
            for addressInKeysFile in configSections:
                if addressInKeysFile != 'bitmessagesettings':
                    status, addressVersionNumber, streamNumber, hash = bitmessagemain.decodeAddress(addressInKeysFile)

                    addresses.append({'label': bitmessagemain.shared.config.get(addressInKeysFile, 'label'), 'address': addressInKeysFile, 'stream':streamNumber, 'enabled': bitmessagemain.shared.config.getboolean(addressInKeysFile, 'enabled')})
            return addresses
            
        def createRandomAddress(self,label,eighteenByteRipe=False,totalDifficulty=1,smallMessageDifficulty=1):

            nonceTrialsPerByte = int(bitmessagemain.shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
            payloadLengthExtraBytes = int(bitmessagemain.shared.networkDefaultPayloadLengthExtraBytes * smallMessageDifficulty)
            
            unicode(label, 'utf-8')

            bitmessagemain.shared.apiAddressGeneratorReturnQueue.queue.clear()
            streamNumberForAddress = 1
            bitmessagemain.shared.addressGeneratorQueue.put((
                'createRandomAddress', 3, streamNumberForAddress, label, 1, "", eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes))
            return bitmessagemain.shared.apiAddressGeneratorReturnQueue.get()

        def createDeterministicAddresses(self,passphrase,label=None,numberOfAddresses=1,addressVersionNumber=3,streamNumber=1,eighteenByteRipe=False,totalDifficulty=1,smallMessageDifficulty=1):
            assert addressVersionNumber == 3, 'Only 3 is supported'
            assert streamNumber == 1, 'only 1 is supported'
            if not label:
                label = passphrase
            
            nonceTrialsPerByte = int(bitmessagemain.shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
            payloadLengthExtraBytes = int(bitmessagemain.shared.networkDefaultPayloadLengthExtraBytes * smallMessageDifficulty)

            bitmessagemain.shared.apiAddressGeneratorReturnQueue.queue.clear()

            bitmessagemain.shared.addressGeneratorQueue.put(
                ('createDeterministicAddresses', addressVersionNumber, streamNumber,
                 label, numberOfAddresses, passphrase, eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes))

            queueReturn = bitmessagemain.shared.apiAddressGeneratorReturnQueue.get()

            return queueReturn

        def getDeterministicAddress(self,passphrase, addressVersionNumber=3, streamNumber=1):
            assert addressVersionNumber == 3, 'Only 3 is supported'
            assert streamNumber == 1, 'only 1 is supported'
            
            numberOfAddresses = 1
            eighteenByteRipe = False
            bitmessagemain.shared.addressGeneratorQueue.put(
                ('getDeterministicAddress', addressVersionNumber,
                 streamNumber, 'unused API address', numberOfAddresses, passphrase, eighteenByteRipe))
            return bitmessagemain.shared.apiAddressGeneratorReturnQueue.get()


        def sendMessage(self, fromAddress, toAddress, subject, message, encodingType=2):
            
            assert encodingType == 2, 'other values not supported jet'
            
            status, addressVersionNumber, streamNumber, toRipe = bitmessagemain.decodeAddress(toAddress)
            if status != 'success':
                with bitmessagemain.shared.printLock:
                    print 'ToAddress Error: %s , %s'%(toAddress,status)
                return (toAddress,status)

            status, addressVersionNumber, streamNumber, fromRipe = bitmessagemain.decodeAddress(fromAddress)
            if status != 'success':
                with bitmessagemain.shared.printLock:
                    print 'fromAddress Error: %s , %s'%(fromAddress,status)
                return (fromAddress,status)
                
     
            toAddress = bitmessagemain.addBMIfNotPresent(toAddress)
            fromAddress = bitmessagemain.addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = bitmessagemain.shared.config.getboolean(fromAddress, 'enabled')
            except:
                return (fromAddress,'fromAddressNotPresentError')
            if not fromAddressEnabled:
                return (fromAddress,'fromAddressDisabledError')

            ackdata = bitmessagemain.OpenSSL.rand(32)

            t = ('', toAddress, toRipe, fromAddress, subject, message, ackdata, int(
                time.time()), 'msgqueued', 1, 1, 'sent', 2)
            bitmessagemain.helper_sent.insert(t)

            toLabel = ''
            t = (toAddress,)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put(
                '''select label from addressbook where address=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            if queryreturn != []:
                for row in queryreturn:
                    toLabel, = row

            bitmessagemain.shared.UISignalQueue.put(('displayNewSentMessage', (
                toAddress, toLabel, fromAddress, subject, message, ackdata)))

            bitmessagemain.shared.workerQueue.put(('sendmessage', toAddress))

            return ackdata.encode('hex')

        
        def getAllSentMessages(self):
            
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent where folder='sent' ORDER BY lastactiontime''')
            bitmessagemain.shared.sqlSubmitQueue.put('')
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)

                data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject, 'message':message, 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')})

            return data
            
        def getAllSentMessageIDs(self):
            
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''SELECT msgid FROM sent where folder='sent' ORDER BY lastactiontime''')
            bitmessagemain.shared.sqlSubmitQueue.put('')
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()

            data = []
            for row in queryreturn:
                msgid = row[0]
                data.append(msgid.encode('hex'))

            return data
            
        def getInboxMessagesByReceiver(self,toAddress):

            v = (toAddress,)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype FROM inbox WHERE folder='inbox' AND toAddress=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(v)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()

            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)

                data .append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'receivedTime':received})

            return data
            
        def getSentMessageByID(self,msgid):

            msgid = msgid.decode('hex')
            v = (msgid,)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE msgid=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(v)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')})
            
            return data
            
        def getSentMessagesBySender(self, fromAddress):
            v = (fromAddress,)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE folder='sent' AND fromAddress=? ORDER BY lastactiontime''')
            bitmessagemain.shared.sqlSubmitQueue.put(v)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject, 'message':message, 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')})

            return data
        
        def getSentMessageByAckData(self,ackData):

            ackData = ackData.decode('hex')
            v = (ackData,)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE ackdata=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(v)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject, 'message':message, 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')})

            return data
            
        def trashSentMessage(self,msgid):

            msgid = msgid.decode('hex')
            t = (msgid,)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''UPDATE sent SET folder='trash' WHERE msgid=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlSubmitQueue.put('commit')
            bitmessagemain.shared.sqlLock.release()

        def sendBroadcast(self,fromAddress,subject,message,encodingType=2):
            
            assert encodingType == 2, 'Only 2 is supported jet'

            status, addressVersionNumber, streamNumber, toRipe = bitmessagemain.decodeAddress(fromAddress)
            fromAddress = bitmessagemain.addBMIfNotPresent(fromAddress)
            
            try:
                fromAddressEnabled = bitmessagemain.shared.config.getboolean(fromAddress, 'enabled')
            except:
                return (fromAddress,'fromAddressNotPresentError')
            if not fromAddressEnabled:
                return (fromAddress,'fromAddressDisabledError')
                
            ackdata = bitmessagemain.OpenSSL.rand(32)
            toAddress = '[Broadcast subscribers]'
            ripe = ''


            t = ('', toAddress, ripe, fromAddress, subject, message, ackdata, int(
                time.time()), 'broadcastqueued', 1, 1, 'sent', 2)
            bitmessagemain.helper_sent.insert(t)

            toLabel = '[Broadcast subscribers]'
            bitmessagemain.shared.workerQueue.put(('sendbroadcast', ''))

            return ackdata.encode('hex')
                
        def getSentMessageStatus(self,ackdata):

            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''SELECT status FROM sent where ackdata=?''')
            bitmessagemain.shared.sqlSubmitQueue.put((ackdata.decode('hex'),))
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            if queryreturn == []:
                return 'notfound'
            for row in queryreturn:
                status, = row
                return status
                
        def addSubscription(self,address,label = ''):

            unicode(label, 'utf-8')

            address = bitmessagemain.addBMIfNotPresent(address)
            status, addressVersionNumber, streamNumber, toRipe = bitmessagemain.decodeAddress(address)
            assert status == 'success', 'Address Error: %s , %s'%(address,status)

            # First we must check to see if the address is already in the
            # subscriptions list.
            bitmessagemain.shared.sqlLock.acquire()
            t = (address,)
            bitmessagemain.shared.sqlSubmitQueue.put('''select * from subscriptions where address=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            assert queryreturn == [],'AlreadySubscribedError'

            t = (label, address, True)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''INSERT INTO subscriptions VALUES (?,?,?)''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlSubmitQueue.put('commit')
            bitmessagemain.shared.sqlLock.release()
            bitmessagemain.shared.reloadBroadcastSendersForWhichImWatching()

        def deleteSubscription(self,address):

            address = addBMIfNotPresent(address)
            t = (address,)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''DELETE FROM subscriptions WHERE address=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlSubmitQueue.put('commit')
            bitmessagemain.shared.sqlLock.release()
            bitmessagemain.shared.reloadBroadcastSendersForWhichImWatching()

        def listSubscriptions(self):
            
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''SELECT label, address, enabled FROM subscriptions''')
            bitmessagemain.shared.sqlSubmitQueue.put('')
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            data = []
            for row in queryreturn:
                label, address, enabled = row
                label = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(label)
                data.append({'label':label, 'address': address, 'enabled': enabled})
            return data
            
        def clientStatus(self):
            return {"networkConnections" : len(bitmessagemain.shared.connectedHostsList)}

        def listContacts(self):
            
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''select * from addressbook''')
            bitmessagemain.shared.sqlSubmitQueue.put('')
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            
            data = []
            for row in queryreturn:
                label, address = row
                label = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(label)
                data.append({'label':label, 'address': address})
            return data
            
        def joinChannel(self, label, testaddress=None):
            str_chan = '[chan]'

            #Add Channel to Own Addresses
            bitmessagemain.shared.apiAddressGeneratorReturnQueue.queue.clear()
            bitmessagemain.shared.addressGeneratorQueue.put(('createChan', 3, 1, str_chan + ' ' + label ,label))
            addressGeneratorReturnValue = bitmessagemain.shared.apiAddressGeneratorReturnQueue.get()
            print 'addressGeneratorReturnValue', addressGeneratorReturnValue
            assert len(addressGeneratorReturnValue) != 0, 'AddressAlreadyInsideError'
                
        
            address = addressGeneratorReturnValue[0]
            
            if testaddress:
                assert str(address) == str(testaddress),'ChannelNameDoesntMatchAddressError'

            #Add Address to Address Book
            bitmessagemain.shared.sqlLock.acquire()
            t = (address,)
            bitmessagemain.shared.sqlSubmitQueue.put('''select * from addressbook where address=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            assert queryreturn == [],'AddressAlreadyInsideError'
                
            t = (str_chan + ' ' + label, address)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''INSERT INTO addressbook VALUES (?,?)''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlSubmitQueue.put('commit')
            bitmessagemain.shared.sqlLock.release()
            
            return address
            
            

        def addContact(self,label,address):

            #Add Address to Address Book
            bitmessagemain.shared.sqlLock.acquire()
            t = (address,)
            bitmessagemain.shared.sqlSubmitQueue.put('''select * from addressbook where address=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()

            if queryreturn != []:
                return 'AddressAlreadyInsideError'

            t = (label, address)
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''INSERT INTO addressbook VALUES (?,?)''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlSubmitQueue.put('commit')
            bitmessagemain.shared.sqlLock.release()
            
        def deleteContact(self,address):
            bitmessagemain.shared.sqlLock.acquire()
            t = (address,)
            bitmessagemain.shared.sqlSubmitQueue.put('''delete from addressbook where address=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlSubmitQueue.put('commit')
            bitmessagemain.shared.sqlLock.release()
        
        def getBlackWhitelist(self):
            
            return bitmessagemain.shared.config.get('bitmessagesettings', 'blackwhitelist')

        def setBlackWhitelist(self, value):
            
            assert value == 'black' or value == 'white'
            bitmessagemain.shared.config.set('bitmessagesettings', 'blackwhitelist', value)
            
        def addToBlacklist(self, label, address, enabled=True):
        
            bitmessagemain.shared.sqlLock.acquire()
            t = (label,address,enabled)
            bitmessagemain.shared.sqlSubmitQueue.put('''INSERT INTO blacklist VALUES (?,?,?)''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlSubmitQueue.put('commit')
            bitmessagemain.shared.sqlLock.release()

        def addToWhitelist(self, label, address, enabled=True):
        
            bitmessagemain.shared.sqlLock.acquire()
            t = (label,address,enabled)
            bitmessagemain.shared.sqlSubmitQueue.put('''INSERT INTO whitelist VALUES (?,?,?)''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlSubmitQueue.put('commit')
            bitmessagemain.shared.sqlLock.release()
            
        def listBlacklist(self):
            
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''select * from blacklist''')
            bitmessagemain.shared.sqlSubmitQueue.put('')
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            
            data = []
            for row in queryreturn:
                label, address, enabled = row
                label = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(label)
                data.append({'label':label, 'address': address, 'enabled': bool(enabled)})
            return data
            
        def listWhitelist(self):
            
            bitmessagemain.shared.sqlLock.acquire()
            bitmessagemain.shared.sqlSubmitQueue.put('''select * from whitelist''')
            bitmessagemain.shared.sqlSubmitQueue.put('')
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            
            data = []
            for row in queryreturn:
                label, address, enabled = row
                label = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(label)
                data.append({'label':label, 'address': address, 'enabled': bool(enabled)})
            return data
            
        def deleteFromBlacklist(self,address):
            
            bitmessagemain.shared.sqlLock.acquire()
            t = (address,)
            bitmessagemain.shared.sqlSubmitQueue.put('''delete from blacklist where address=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
            
        def deleteFromWhitelist(self,address):
            
            bitmessagemain.shared.sqlLock.acquire()
            t = (address,)
            bitmessagemain.shared.sqlSubmitQueue.put('''delete from whitelist where address=?''')
            bitmessagemain.shared.sqlSubmitQueue.put(t)
            queryreturn = bitmessagemain.shared.sqlReturnQueue.get()
            bitmessagemain.shared.sqlLock.release()
        
    api = MainAPI()
    api.start(daemon=True)
    time.sleep(5)
    return api

import unittest
class TestFeed(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        global path
        import tempfile
        path = tempfile.mkdtemp()
        
        global api
        api = getAPI(workingdir=path,silent=True)
        import time
        time.sleep(5)
        
    @classmethod
    def tearDownClass(cls):
        import shutil
        import time
        api.stop()
        time.sleep(5)
        shutil.rmtree(path)

    def test_01_create_addresses(self):
        api.createRandomAddress('a')
        assert api.listAddresses()[0]['label'] == 'a',api.listAddresses()[0]
        api.createDeterministicAddresses('b')
        assert api.listAddresses()[1]['label'] == 'b',api.listAddresses()[1]
        api.joinChannel('general')
        assert api.listAddresses()[2]['label'] == '[chan] general',api.listAddresses()[2]
        assert api.listContacts()[0]['label'] == '[chan] general',api.listContacts()[0]
        api.addSubscription('BM-2D9vJkoGoTBhqMyZyjvELKgBWFMr6iGCQQ','d')
        assert api.listSubscriptions()[1]['label'] == 'd',api.listSubscriptions()[1]

    def test_02_manage_contacts(self):
        api.addContact('a','a')
        assert api.listContacts()[1]['address'] == 'a',api.listContacts()[1]
        count = len(api.listContacts())
        api.deleteContact('a')
        assert len(api.listContacts()) == count - 1

    def test_03_manage_blackwhitelist(self):
        assert api.getBlackWhitelist() == 'black'
        api.setBlackWhitelist('white')
        assert api.getBlackWhitelist() == 'white'
        api.setBlackWhitelist('black')
        assert api.getBlackWhitelist() == 'black'
        
        api.addToBlacklist('a','a')
        assert api.listBlacklist()[0]['label'] == 'a'
        api.deleteFromBlacklist('a')
        assert api.listBlacklist() == []
        
        api.addToWhitelist('a','a')
        assert api.listWhitelist()[0]['label'] == 'a'
        api.deleteFromWhitelist('a')
        assert api.listWhitelist() == []
        
    def test_04_send_messages(self):
        addr = api.createRandomAddress('sendtest')
        ackdata1 = api.sendMessage(addr,'BM-2D9vJkoGoTBhqMyZyjvELKgBWFMr6iGCQQ','test','test')
        ackdata2 = api.sendBroadcast(addr,'test','test')
        while api.getSentMessageByAckData(ackdata1) == 'notfound':
            pass
        while api.getSentMessageByAckData(ackdata2) == 'notfound':
            pass
            
        assert api.getSentMessageByAckData(ackdata1)[0]['status'] in ['msgqueued', 'broadcastqueued', \
        'broadcastsent', 'doingpubkeypow', 'awaitingpubkey', 'doingmsgpow', 'forcepow', 'msgsent', \
        'msgsentnoackexpected', 'ackreceived'],api.getSentMessageByAckData(ackdata1)
        assert api.getSentMessageByAckData(ackdata2)[0]['status'] in ['msgqueued', 'broadcastqueued', \
        'broadcastsent', 'doingpubkeypow', 'awaitingpubkey', 'doingmsgpow', 'forcepow', 'msgsent', \
        'msgsentnoackexpected', 'ackreceived'],api.getSentMessageByAckData(ackdata2)

    def test_05_manage_sent_messages(self):
        
        addr = api.createRandomAddress('senttest')
        ackdata = api.sendMessage(addr,addr,'last','last')
        idnum = api.getSentMessageByAckData(ackdata)[0]['msgid']
        
        assert api.getAllSentMessages() != []
        assert api.getAllSentMessageIDs() != []
        assert api.getSentMessagesBySender(addr) != []
        assert api.getSentMessageByAckData(ackdata) != []
        assert api.getSentMessageByID(idnum) != []
        assert api.getSentMessageStatus(ackdata) in ['msgqueued'],api.getSentMessageStatus(ackdata)

        api.trashSentMessage(idnum)
        messages = api.getAllSentMessages()
        for message in messages:
            assert message['msgid'] != idnum
    
    def test_06_manage_inbox_messages(self):

        assert api.clientStatus > 0, 'Not connected'
        addr = api.createRandomAddress('senttest')
        
        while api.getAllInboxMessages() == []:
            ackdata = api.sendMessage(addr,addr,'test','test')
            time.sleep(30)
            assert api.clientStatus > 0, 'Not connected'
            
        assert api.getAllInboxMessages() != [],api.getAllInboxMessages()
        assert api.getAllInboxMessageIDs() != [],api.getAllInboxMessageIDs()
        
        msgid = api.getAllInboxMessages()[0]['msgid']
        recv = api.getAllInboxMessages()[0]['toAddress']
        assert api.getInboxMessageByID(msgid) != []
        assert api.getInboxMessagesByReceiver(recv) != []
        
        api.trashInboxMessage(msgid)
        messages = api.getAllInboxMessages()
        for msg in messages:
            assert msg['msgid'] != msgid
        
        api.getAllInboxMessages()
        
if __name__ == "__main__":
    unittest.main()
