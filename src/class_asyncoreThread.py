from collections import deque
from pyelliptic.openssl import OpenSSL
import asyncore
import shared
import smtpd
import socket
import sys
import threading
import time
import traceback

from addresses import *
import helper_inbox
import helper_sent

class bitmessageSMTPServer(smtpd.SMTPServer):
    def __init__(self):
        # TODO - move to separate file/class
        smtpport = shared.config.getint('bitmessagesettings', 'smtpport')
        smtpd.SMTPServer.__init__(self, ('127.0.0.1', smtpport), None)

        shared.printLock.acquire()
        print "SMTP server started"
        shared.printLock.release()

    def process_message(self, peer, mailfrom, rcpttos, data):
        #print("Peer", peer)
        #print("Mail From", mailfrom)
        #print("Rcpt To", rcpttos)
        #print("Data")
        #print(data)
        #print('--------')
        #print(type(mailfrom))

        message = data

        # Determine the fromAddress and make sure it's an owned identity
        # TODO - determine the address from a SMTP authorization.
        # TODO - use the mailfrom (a legitimate email address?) when delivering
        # real e-mail.
        _, fromAddress = mailfrom.split('@', 1)
        if not (fromAddress.startswith('BM-') and '.' not in fromAddress):
            raise Exception("From Address must be a Bitmessage address.")
        else:
            status, addressVersionNumber, streamNumber, fromRipe = decodeAddress(fromAddress)
            if status != 'success':
                shared.printLock.acquire()
                print 'Error: Could not decode address: ' + fromAddress + ' : ' + status
                if status == 'checksumfailed':
                    print 'Error: Checksum failed for address: ' + fromAddress
                if status == 'invalidcharacters':
                    print 'Error: Invalid characters in address: ' + fromAddress
                if status == 'versiontoohigh':
                    print 'Error: Address version number too high (or zero) in address: ' + fromAddress
                shared.printLock.release()
                raise Exception("Invalid Bitmessage address: {}".format(fromAddress))
            #fromAddress = addBMIfNotPresent(fromAddress) # I know there's a BM-, because it's required when using SMTP

            try:
                fromAddressEnabled = shared.config.getboolean(fromAddress, 'enabled')
            except:
                shared.printLock.acquire()
                print 'Error: Could not find your fromAddress in the keys.dat file.'
                shared.printLock.release()
                raise Exception("Could not find address in keys.dat: {}".format(fromAddress))
            if not fromAddressEnabled:
                shared.printLock.acquire()
                print 'Error: Your fromAddress is disabled. Cannot send.'
                shared.printLock.release()
                raise Exception("The fromAddress is disabled: {}".format(fromAddress))

        for recipient in rcpttos:
            _, toAddress = recipient.split('@', 1)
            if not (toAddress.startswith('BM-') and '.' not in toAddress):
                # TODO - deliver message to another SMTP server.. ?
                raise Exception("Cannot yet handle normal E-mail addresses.")
            else:
                # This is now the 3rd copy of this code. There's one in the API, there's another
                # copy in __init__ for the UI.  Yet another exists here.  It needs to be refactored
                # into a utility func!
                status, addressVersionNumber, streamNumber, toRipe = decodeAddress(toAddress)
                if status != 'success':
                    shared.printLock.acquire()
                    print 'Error: Could not decode address: ' + toAddress + ' : ' + status
                    if status == 'checksumfailed':
                        print 'Error: Checksum failed for address: ' + toAddress
                    if status == 'invalidcharacters':
                        print 'Error: Invalid characters in address: ' + toAddress
                    if status == 'versiontoohigh':
                        print 'Error: Address version number too high (or zero) in address: ' + toAddress
                    shared.printLock.release()
                    raise Exception("Invalid Bitmessage address: {}".format(toAddress))
                #toAddress = addBMIfNotPresent(toAddress) # I know there's a BM-, because it's required when using SMTP

                toAddressIsOK = False
                try:
                    shared.config.get(toAddress, 'enabled')
                    # The toAddress is one owned by me. We cannot send
                    # messages to ourselves without significant changes
                    # to the codebase.
                    shared.printLock.acquire()
                    print "Error: One of the addresses to which you are sending a message, {}, is yours. Unfortunately the Bitmessage client cannot process its own messages. Please try running a second client on a different computer or within a VM.".format(toAddress)
                    shared.printLock.release()
                except:
                    toAddressIsOK = True

                if not toAddressIsOK:
                    raise Exception("Cannot send message to {}".format(toAddress))

                # The subject is specially formatted to identify it from non-E-mail messages.
                subject = "<Bitmessage Mail: 00000000000000000000>" # Reserved, flags.

                ackdata = OpenSSL.rand(32)
                t = ('', toAddress, toRipe, fromAddress, subject, message, ackdata, int(time.time()), 'msgqueued', 1, 1, 'sent', 2)
                helper_sent.insert(t)

                toLabel = ''
                t = (toAddress,)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put('''select label from addressbook where address=?''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()
                if queryreturn != []:
                    for row in queryreturn:
                        toLabel, = row
                shared.UISignalQueue.put(('displayNewSentMessage', (toAddress, toLabel, fromAddress, subject, message, ackdata)))
                shared.workerQueue.put(('sendmessage', toAddress))

                # TODO - what should we do with ackdata.encode('hex') ?

class bitmessagePOP3Connection(asyncore.dispatcher):
    END = b"\r\n"

    def __init__(self, sock, peer_address, debug=False):
        asyncore.dispatcher.__init__(self, sock)
        self.peer_address = peer_address
        self.data_buffer = []
        self.commands    = deque()
        self.debug       = debug

        self.dispatch = dict(
            USER=self.handleUser,
            PASS=self.handlePass,
            STAT=self.handleStat,
            LIST=self.handleList,
            #TOP=self.handleTop,
            RETR=self.handleRetr,
            DELE=self.handleDele,
            NOOP=self.handleNoop,
            QUIT=self.handleQuit,
        )

        #self.bitmessage = Bitmessage()
        self.messages = None #TODO self.bitmessage.getInboxMessagesByAddress(BITMAIL_ADDRESS)
        self.storage_size = 0
        self.address = None
        
        #for msg in self.messages:
        #    msg['message'] = base64.b64decode(msg['message'].encode('ascii'))
        #    msg['subject'] = base64.b64decode(msg['subject'].encode('ascii'))
        #    msg['size']    = len(msg['message'])
        #    self.storage_size += msg['size']

        #print(self.messages)

        self.sendline("+OK Bitmessage POP3 server ready")

    def populateMessageIndex(self):
        if self.address is None:
            raise Exception("Invalid address: {}".format(self.address))

        if self.messages is not None:
            return

        v = (self.address,)
        shared.sqlLock.acquire()
        # TODO LENGTH(message) needs to be the byte-length, not the character-length.
        shared.sqlSubmitQueue.put('''SELECT msgid, fromaddress, subject, LENGTH(message) FROM inbox WHERE folder='inbox' AND toAddress=?''')
        shared.sqlSubmitQueue.put(v)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()

        self.storage_size = 0
        self.messages = []
        for row in queryreturn:
            msgid, fromAddress, subject, size = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            if subject.startswith("<Bitmessage Mail: ") and subject[-1] == '>':
                subject = "<Bitmessage Mail: 00000000000000000000>" # Reserved, flags.
                flags = subject[-21:-1]
                # TODO - checksum?

                self.messages.append({
                    'msgid': msgid,
                    'fromAddress': fromAddress,
                    'subject': subject,
                    'size': size,
                })

                self.storage_size += size


    def getMessageContent(self, msgid):
        if self.address is None:
            raise Exception("Invalid address: {}".format(self.address))

        v = (msgid,)
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put('''SELECT fromaddress, received, message, encodingtype FROM inbox WHERE msgid=?''')
        shared.sqlSubmitQueue.put(v)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()

        for row in queryreturn:
            fromAddress, received, message, encodingtype = row
            message = shared.fixPotentiallyInvalidUTF8Data(message)
            return {
                'fromAddress': fromAddress,
                'received': received,
                'message': message,
                'encodingtype': encodingtype
            }

    def trashMessage(self, msgid):
        # TODO - how to determine if the update succeeded?
        if not self.debug:
            helper_inbox.trash(msgid)
        return True

    def sendline(self, data, END=END):
        if self.debug:
            shared.printLock.acquire()
            sys.stdout.write("sending ")
            sys.stdout.write(data)
            sys.stdout.write("\n")
            shared.printLock.release()
        data = data + END
        while len(data) > 4096:
            self.send(data[:4096])
            data = data[4096:]
        if len(data):
            self.send(data)

    def handle_read(self):
        chunk = self.recv(4096)

        while bitmessagePOP3Connection.END in chunk:
            # Join all the data up to the END and throw it in commands
            command = b''.join(self.data_buffer) + chunk[:chunk.index(bitmessagePOP3Connection.END)]
            chunk = chunk[chunk.index(bitmessagePOP3Connection.END)+2:]
            self.data_buffer = []
            self.commands.append(command)

        if len(chunk):
            self.data_buffer.append(chunk)

        if self.debug:
            shared.printLock.acquire()
            print('data_buffer', self.data_buffer)
            print('commands', self.commands)
            print('-')
            shared.printLock.release()

        while len(self.commands):
            line = self.commands.popleft()

            if b' ' in line:
                cmd, data = line.split(b' ', 1)
            else:
                cmd, data = line, b''

            try:
                cmd = self.dispatch[cmd.decode('ascii').upper()]
            except KeyError:
                self.sendline('-ERR unknown command')
                continue

            for response in cmd(data):
                self.sendline(response)

            if cmd is self.handleQuit:
                self.close()
                break

    def handleUser(self, data):
        self.address = data

        status, addressVersionNumber, streamNumber, ripe = decodeAddress(self.address)
        if status != 'success':
            shared.printLock.acquire()
            print 'Error: Could not decode address: ' + self.address + ' : ' + status
            if status == 'checksumfailed':
                print 'Error: Checksum failed for address: ' + self.address
            if status == 'invalidcharacters':
                print 'Error: Invalid characters in address: ' + self.address
            if status == 'versiontoohigh':
                print 'Error: Address version number too high (or zero) in address: ' + self.address
            shared.printLock.release()
            raise Exception("Invalid Bitmessage address: {}".format(self.address))

        return ["+OK user accepted"]
    
    def handlePass(self, data):
        # TODO
        return ["+OK pass accepted"]
    
    def handleStat(self, data):
        self.populateMessageIndex()
        return ["+OK {} {}".format(len(self.messages), self.storage_size)]
    
    def handleList(self, data):
        self.populateMessageIndex()
        yield "+OK {} messages ({} octets)".format(len(self.messages), self.storage_size)
        for i, msg in enumerate(self.messages):
            yield "{} {}".format(i + 1, msg['size'])
        yield "."

    #def handleTop(self, data):
    #    cmd, num, lines = data.split()
    #    assert num == "1", "unknown message number: {}".format(num)
    #    lines = int(lines)
    #    text = msg.top + "\r\n\r\n" + "\r\n".join(msg.bot[:lines])
    #    return "+OK top of message follows\r\n{}\r\n.".format(text)
    
    def handleRetr(self, data):
        index = int(data.decode('ascii')) - 1
        assert index >= 0
        self.populateMessageIndex()
        msg = self.messages[index]
        content = self.getMessageContent(msg['msgid'])
        if self.debug:
            shared.printLock.acquire()
            sys.stdout.write(str(msg) + ": " + str(content))
            shared.printLock.release()
        yield "+OK {} octets".format(msg['size'])
        yield content['message']
        yield '.'
    
    def handleDele(self, data):
        index = int(data.decode('ascii')) - 1
        assert index >= 0
        self.populateMessageIndex()
        msg = self.messages[index]
        if self.trashMessage(msg['msgid']):
            return ["+OK deleted"]
        else:
            return ["-ERR internal error"]
    
    def handleNoop(self, data):
        return ["+OK"]
    
    def handleQuit(self, data):
        return ["+OK Bitmessage POP3 server signing off"]

class bitmessagePOP3Server(asyncore.dispatcher):
    def __init__(self, debug=False):
        asyncore.dispatcher.__init__(self)
        self.debug = debug

        pop3port = shared.config.getint('bitmessagesettings', 'pop3port')
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('127.0.0.1', pop3port))
        self.listen(10)

        shared.printLock.acquire()
        print "POP3 server started"
        shared.printLock.release()

    def handle_accept(self):
        sock, peer_address = self.accept()
        _ = bitmessagePOP3Connection(sock, peer_address, debug=self.debug)

class asyncoreThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        shared.printLock.acquire()
        print "Asyncore thread started"
        shared.printLock.release()

        asyncore.loop(timeout=1) # Despite the horrible parameter name, this function will not timeout until all channels are closed.
