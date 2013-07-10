from cStringIO import StringIO
from collections import deque
import asyncore
import hashlib
import shared
import socket
import ssl
import sys

from email import parser, generator, utils

from addresses import *
import helper_inbox

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

        self.messages = None
        self.storage_size = 0
        self.address = None
        self.pw = None
        self.loggedin = False
        
        self.sendline("+OK Bitmessage POP3 server ready")

    def populateMessageIndex(self):
        if not self.loggedin:
            raise Exception("Cannot be called when not logged in.")

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
            i = subject.find('<Bitmessage Mail: ')
            if i >= 0:
                tmp = subject[i:]
                i = tmp.find('>')
                if i >= 0:
                    flags = tmp[i-21:i] # TODO - verify checksum?

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
        helper_inbox.trash(msgid)
        return True

    def sendline(self, data, END=END):
        if self.debug:
            with shared.printLock:
                sys.stdout.write("sending ")
                sys.stdout.write(data)
                sys.stdout.write("\n")
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
            with shared.printLock:
                print('data_buffer', self.data_buffer)
                print('commands', self.commands)
                print('-')

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
        if self.loggedin:
            raise Exception("Cannot login twice")

        if '@' not in data:
            yield "-ERR access denied"
            return

        capitalization, address = data.split('@', 1)
        self.address = applyBase58Capitalization(address, int(capitalization))

        status, addressVersionNumber, streamNumber, ripe = decodeAddress(self.address)
        if status != 'success':
            with shared.printLock:
                print 'Error: Could not decode address: ' + self.address + ' : ' + status
                if status == 'checksumfailed':
                    print 'Error: Checksum failed for address: ' + self.address
                if status == 'invalidcharacters':
                    print 'Error: Invalid characters in address: ' + self.address
                if status == 'versiontoohigh':
                    print 'Error: Address version number too high (or zero) in address: ' + self.address
            raise Exception("Invalid Bitmessage address: {}".format(self.address))

        username = '{}@{}'.format(getBase58Capitaliation(self.address), self.address)

        # Must login with the full E-mail address and capitalization
        if data != username:
            yield "-ERR access denied"
            return

        # Each identity must be enabled independly by setting the smtppop3password for the identity
        # If no password is set, then the identity is not available for SMTP/POP3 access.
        try:
            if shared.config.getboolean(self.address, "enabled"):
                self.pw = shared.config.get(self.address, "smtppop3password")
                yield "+OK user accepted"
                return
        except:
            pass

        yield "-ERR access denied"
        self.close()
    
    def handlePass(self, data):
        if self.pw is None:
            yield "-ERR must specify USER"
        else:
            pw = data.decode('ascii')
            if pw == self.pw: # TODO - hashed passwords?
                yield "+OK pass accepted"
                self.loggedin = True
            else:
                yield "-ERR invalid password"

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
            with shared.printLock:
                sys.stdout.write(str(msg) + ": " + str(content))
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

        self.ssl = shared.config.getboolean('bitmessagesettings', 'pop3ssl')
        if self.ssl:
            self.keyfile = shared.config.get('bitmessagesettings', 'keyfile')
            self.certfile = shared.config.get('bitmessagesettings', 'certfile')

        try:
            bindAddress = shared.config.get('bitmessagesettings', 'pop3address')
        except:
            bindAddress = '127.0.0.1'

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((bindAddress, pop3port))
        self.listen(10)

        with shared.printLock:
            print "POP3 server started: SSL enabled={}".format(str(self.ssl))

    def handle_accept(self):
        sock, peer_address = self.accept()
        if self.ssl:
            sock = ssl.wrap_socket(sock, server_side=True, certfile=self.certfile, keyfile=self.keyfile, ssl_version=ssl.PROTOCOL_SSLv23)
        _ = bitmessagePOP3Connection(sock, peer_address, debug=self.debug)

    @staticmethod
    def reformatMessageForReceipt(toAddress, fromAddress, body, subject):
        message = parser.Parser().parsestr(body)
        print(message)

        subject_is_valid = False

        i = subject.find('<Bitmessage Mail: ')
        if i >= 0:
            tmp = subject[i:]
            i = tmp.find('>')
            if i >= 0:
                flags = tmp[i-21:i]
                checksum = int(flags[-4:], 16)

                # Checksum to make sure incoming message hasn't been tampered with
                c = hashlib.sha256(body).digest()[:2]
                c = (ord(checksum[0]) << 8) | ord(checksum[1])

                # Valid Bitmessage subject line already
                if c == checksum:
                    subject_is_valid = True
                else:
                    with shared.printLock:
                        print 'Got E-Mail formatted message with incorrect checksum...'

        body_is_valid = False
        if 'Date' in message and 'From' in message:
            body_is_valid = True

        if not body_is_valid:
            fromLabel = '{}@{}'.format(getBase58Capitaliation(fromAddress), fromAddress)

            t = (fromAddress,)
            with shared.sqlLock:
                shared.sqlSubmitQueue.put(
                    '''SELECT label FROM addressbook WHERE address=?''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
            for row in queryreturn:
                fromLabel = '{} <{}>'.format(row[0], fromLabel)
                break

            message['From'] = fromLabel
            message['Date'] = utils.formatdate()

        message['X-Bitmessage-Subject'] = subject
        if not subject_is_valid and 'Subject' not in message:
            message['Subject'] = subject

        toLabel = '{}@{}'.format(getBase58Capitaliation(toAddress), toAddress)
        try:
            toLabel = '{} <{}>'.format(shared.config.get(toAddress, 'label'), toLabel)
        except:
            pass

        if "To" not in message:
            message['To'] = toLabel

        # Return-Path
        returnPath = "{}@{}".format(getBase58Capitaliation(fromAddress), fromAddress)
        message['Return-Path'] = returnPath

        # X-Delivered-To
        deliveredTo = "{}@{}".format(getBase58Capitaliation(toAddress), toAddress)
        message['X-Delivered-To'] = deliveredTo

        # X-Bitmessage-Receiving-Version
        message["X-Bitmessage-Receiving-Version"] = shared.softwareVersion

        fp = StringIO()
        gen = generator.Generator(fp, mangle_from_=False, maxheaderlen=128)
        gen.flatten(message)

        message_as_text = fp.getvalue()

        # Checksum to makesure incoming message hasn't been tampered with
        # TODO - if subject_is_valid, then don't completely overwrite the subject, instead include all the data outside of <> too
        checksum = hashlib.sha256(message_as_text).digest()[:2]
        checksum = (ord(checksum[0]) << 8) | ord(checksum[1])
        subject = "<Bitmessage Mail: 0000000000000000{:04x}>".format(checksum) # Reserved flags.

        return message_as_text, subject

    @staticmethod
    def addMailingListNameToSubject(subject, mailingListName):
        withoutre = subject = subject.strip()
        re = ''
        if subject[:3] == 'Re:' or subject[:3] == 'RE:':
            re = subject[:3] + ' '
            withoutre = subject[3:].strip()
        a = '[' + mailingListName + ']'
        if withoutre.startswith(a):
            return subject
        else:
            return re + a + ' ' + subject

    @staticmethod
    def reformatMessageForMailingList(toAddress, fromAddress, body, subject, mailingListName):
        message = parser.Parser().parsestr(body)
        print(message)

        subject_is_valid = False

        i = subject.find('<Bitmessage Mail: ')
        if i >= 0:
            tmp = subject[i:]
            i = tmp.find('>')
            if i >= 0:
                flags = tmp[i-21:i]
                checksum = int(flags[-4:], 16)

                # Checksum to make sure incoming message hasn't been tampered with
                c = hashlib.sha256(body).digest()[:2]
                c = (ord(checksum[0]) << 8) | ord(checksum[1])

                # Valid Bitmessage subject line already
                if c == checksum:
                    subject_is_valid = True
                else:
                    with shared.printLock:
                        print 'Got E-Mail formatted message with incorrect checksum...'

        # The mailing list code will override some headers, including Date and From, so
        # that the trust can be moved from the original sender to the mailing list owner.
        fromLabel = '{}@{}'.format(getBase58Capitaliation(fromAddress), fromAddress)

        if 'From' in message:
            originalFrom = message['From']
            message['X-Original-From'] = originalFrom

            i = originalFrom.find('<' + fromLabel + '>')
            if i >= 0:
                fromLabel = '{} <{}>'.format(originalFrom[:i].strip(), fromLabel)

        message['From'] = fromLabel
        message['Date'] = utils.formatdate()

        message['X-Bitmessage-Subject'] = subject
        if 'Subject' not in message:
            if not subject_is_valid:
                message['Subject'] = bitmessagePOP3Server.addMailingListNameToSubject(subject, mailingListName)
            else:
                # TODO - strip <Bitmessage Mail: ...> from bitmessage subject?
                message['Subject'] = bitmessagePOP3Server.addMailingListNameToSubject('', mailingListName)
        else:
            message['Subject'] = bitmessagePOP3Server.addMailingListNameToSubject(message['Subject'], mailingListName)

        toLabel = '{}@{}'.format(getBase58Capitaliation(toAddress), toAddress)
        try:
            toLabel = '{} <{}>'.format(shared.config.get(toAddress, 'label'), toLabel)
        except:
            pass

        if 'To' in message:
            message['X-Original-To'] = message['To']
        message['To'] = toLabel

        # X-Bitmessage-MailingList-Name
        message['X-Bitmessage-MailingList-Name'] = mailingListName

        # X-Bitmessage-MailingList-Address
        mailingListAddress = "{}@{}".format(getBase58Capitaliation(toAddress), toAddress)
        message['X-Bitmessage-MailingList-Address'] = mailingListAddress

        # X-Bitmessage-MailingList-Version
        message["X-Bitmessage-MailingList-Version"] = shared.softwareVersion

        fp = StringIO()
        gen = generator.Generator(fp, mangle_from_=False, maxheaderlen=128)
        gen.flatten(message)

        message_as_text = fp.getvalue()

        # Checksum to makesure incoming message hasn't been tampered with
        # TODO - if subject_is_valid, then don't completely overwrite the subject, instead include all the data outside of <> too
        checksum = hashlib.sha256(message_as_text).digest()[:2]
        checksum = (ord(checksum[0]) << 8) | ord(checksum[1])
        subject = bitmessagePOP3Server.addMailingListNameToSubject("<Bitmessage Mail: 0000000000000000{:04x}>".format(checksum), mailingListAddress)

        return message_as_text, subject
                        
