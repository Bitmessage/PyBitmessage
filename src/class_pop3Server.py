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
        shared.sqlSubmitQueue.put('''SELECT msgid, fromaddress, subject, message FROM inbox WHERE folder='inbox' AND toAddress=?''')
        shared.sqlSubmitQueue.put(v)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()

        self.storage_size = 0
        self.messages = []
        for row in queryreturn:
            msgid, fromAddress, subject, body = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            body    = shared.fixPotentiallyInvalidUTF8Data(body)

            message = parser.Parser().parsestr(body)
            if not ('Date' in message and 'From' in message and 'X-Bitmessage-Flags' in message):
                continue

            flags = message['X-Bitmessage-Flags'] # TODO - verify checksum?

            self.messages.append({
                'msgid'      : msgid,
                'fromAddress': fromAddress,
                'subject'    : subject,
                'size'       : len(body),
                'flags'      : flags,
            })

            self.storage_size += len(body)

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
                'fromAddress' : fromAddress,
                'received'    : received,
                'message'     : message,
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

        if '@' in data:
            data, _ = data.split('@', 1)

        self.address = data
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
        #yield content['message']
        # TODO - this is temporary until I come up with better organization for 
        # the responses.
        self.sendline(content['message'], END='')
        yield (bitmessagePOP3Connection.END + '.')
    
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
    def reformatMessageForReceipt(toAddress, fromAddress, body, subject, broadcast=False):
        originalBody = body
        ostensiblyFrom = None
        if broadcast:
            # Temporarily strip out the annoying 'message ostensibly from' to see if there are already headers
            i = body.find('Message ostensibly from')
            if i >= 0:
                e = body.find(':\n\n')
                if e >= i and '\n' not in body[i:e]:
                    line = body[:e]
                    body = body[e+3:]
                    i = line.rfind(' ')
                    if i >= 0:
                        testFromAddress = line[i+1:]
                        status, addressVersionNumber, streamNumber, ripe = decodeAddress(testFromAddress)
                        if status == 'success':
                            ostensiblyFrom = testFromAddress

        message = parser.Parser().parsestr(body)

        body_is_valid = False
        if 'Date' in message and 'From' in message:
            body_is_valid = True

        if broadcast and not body_is_valid:
            # Let's keep the "ostensibly from" stuff since beneath it does not lie an internet message
            body = originalBody
            message = parser.Parser().parsestr(body)
            if 'Date' in message and 'From' in message:
                body_is_valid = True

        print '--------'
        with shared.printLock:
            print(message)
        print '--------'

        flags = '0'
        if 'X-Bitmessage-Flags' in message:
            flags = message['X-Bitmessage-Flags']
            del message['X-Bitmessage-Flags']

        mailingListName = None
        if broadcast:
            # Determine a mailing list label, just in case
            with shared.sqlLock:
                t = (fromAddress,toAddress)
                shared.sqlSubmitQueue.put(
                    '''SELECT label FROM subscriptions WHERE address=? AND receiving_identity=?''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
            for row in queryreturn:
                mailingListName = row[0]
                break

        if not body_is_valid:
            if broadcast:
                if ostensiblyFrom is not None:
                    fromLabel = '{} <{}@bm.addr>'.format(ostensiblyFrom, ostensiblyFrom)
                    # TODO - check address book for label?
                else:
                    fromLabel = '{}@bm.addr'.format(fromAddress)
                    if mailingListName is not None:
                        fromLabel = '{} <{}>'.format(mailingListName, fromLabel)
                    else:
                        fromLabel = '{} <{}>'.format(fromAddress, fromLabel)
            else:
                fromLabel = '{}@bm.addr'.format(fromAddress)

                with shared.sqlLock:
                    t = (fromAddress,)
                    shared.sqlSubmitQueue.put(
                        '''SELECT label FROM addressbook WHERE address=?''')
                    shared.sqlSubmitQueue.put(t)
                    queryreturn = shared.sqlReturnQueue.get()
                for row in queryreturn:
                    fromLabel = '{} <{}>'.format(row[0], fromLabel)
                    break
                else:
                    fromLabel = '{} <{}>'.format(fromAddress, fromLabel)

            message['From'] = fromLabel
            message['Date'] = utils.formatdate(localtime=False)

        if 'Subject' in message:
            if mailingListName is not None:
                s = message['Subject']
                del message['Subject']
                message['Subject'] = bitmessagePOP3Server.addMailingListNameToSubject(s, mailingListName)
        else:
            message['Subject'] = subject

        if broadcast:
            # The To: field on a broadcast is the mailing list, not you
            toLabel = '{}@bm.addr'.format(fromAddress)
            if mailingListName is not None:
                toLabel = '{} <{}>'.format(mailingListName, toLabel)
            if 'To' in message:
                del message['To']
            message['To'] = toLabel
            if 'Reply-To' in message:
                del message['Reply-To']
            message['Reply-To'] = toLabel
        else:
            if 'To' not in message:
                toLabel = '{}@bm.addr'.format(toAddress)
                try:
                    toLabel = '{} <{}>'.format(shared.config.get(toAddress, 'label'), toLabel)
                except:
                    pass

                message['To'] = toLabel

        # Return-Path
        returnPath = "{}@bm.addr".format(fromAddress)
        message['Return-Path'] = returnPath

        # X-Delivered-To
        deliveredTo = "{}@bm.addr".format(toAddress)
        message['X-Delivered-To'] = deliveredTo

        # X-Bitmessage-Receiving-Version
        message["X-Bitmessage-Receiving-Version"] = shared.softwareVersion

        # Others...
        message['X-Bitmessage-Subject'] = subject
        message['X-Bitmessage-Flags'] = flags

        fp = StringIO()
        gen = generator.Generator(fp, mangle_from_=False, maxheaderlen=128)
        gen.flatten(message)

        message_as_text = fp.getvalue()
        return message_as_text, subject

    @staticmethod
    def reformatMessageForMailingList(toAddress, fromAddress, body, subject, mailingListName):
        message = parser.Parser().parsestr(body)
        with shared.printLock:
            print(message)

        flags = '0'
        if 'X-Bitmessage-Flags' in message:
            flags = message['X-Bitmessage-Flags']
            del message['X-Bitmessage-Flags']

        # The mailing list code will override some headers, including Date and From
        fromLabel = '{}@bm.addr'.format(fromAddress)

        if 'From' in message:
            originalFrom = message['From']
            message['X-Original-From'] = originalFrom

            i = originalFrom.find('<' + fromAddress + '@')
            if i >= 0:
                fromLabel = '{} <{}>'.format(originalFrom[:i].strip(), fromLabel)
            else:
                fromLabel = '{} <{}>'.format(fromAddress, fromLabel)

            del message['From']

        message['From'] = fromLabel

        if 'Date' in message:
            del message['Date']

        message['Date'] = utils.formatdate(localtime=False)

        message['X-Bitmessage-Subject'] = subject
        if 'Subject' not in message:
            message['Subject'] = bitmessagePOP3Server.addMailingListNameToSubject(subject, mailingListName)
        else:
            s = message['Subject']
            del message['Subject']
            message['Subject'] = bitmessagePOP3Server.addMailingListNameToSubject(s, mailingListName)

        toLabel = '"{}" <{}@bm.addr>'.format(mailingListName, toAddress)
        if 'To' in message:
            message['X-Original-To'] = message['To']
            del message['To']
        message['To'] = toLabel

        # X-Bitmessage-MailingList-Name
        message['X-Bitmessage-MailingList-Name'] = mailingListName

        # X-Bitmessage-MailingList-Address
        mailingListAddress = "{}@{}".format(getBase58Capitaliation(toAddress), toAddress)
        message['X-Bitmessage-MailingList-Address'] = mailingListAddress

        # X-Bitmessage-MailingList-Version
        message["X-Bitmessage-MailingList-Version"] = shared.softwareVersion

        message["X-Bitmessage-Flags"] = flags

        fp = StringIO()
        gen = generator.Generator(fp, mangle_from_=False, maxheaderlen=128)
        gen.flatten(message)

        message_as_text = fp.getvalue()
        return message_as_text, subject
                        
