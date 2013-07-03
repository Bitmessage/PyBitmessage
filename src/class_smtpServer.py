from pyelliptic.openssl import OpenSSL
import asynchat
import base64
import errno
import shared
import smtpd
import socket
import ssl
import time

from addresses import *
import helper_sent

# This is copied from Python's smtpd module and modified to support basic SMTP AUTH.
class bitmessageSMTPChannel(asynchat.async_chat):
    COMMAND = 0
    DATA = 1

    def __init__(self, server, conn, addr):
        asynchat.async_chat.__init__(self, conn)
        self.__server = server
        self.__conn = conn
        self.__addr = addr
        self.__line = []
        self.__state = self.COMMAND
        self.__greeting = 0
        self.__mailfrom = None
        self.__rcpttos = []
        self.__data = ''
        self.__fqdn = socket.getfqdn()
        self.__version = 'Python SMTP proxy version 0.2a'
        self.logged_in = False
        try:
            self.__peer = conn.getpeername()
        except socket.error, err:
            # a race condition  may occur if the other end is closing
            # before we can get the peername
            self.close()
            if err[0] != errno.ENOTCONN:
                raise
            return
        print >> smtpd.DEBUGSTREAM, 'Peer:', repr(self.__peer)
        self.push('220 %s %s' % (self.__fqdn, self.__version))
        self.set_terminator('\r\n')

    # Overrides base class for convenience
    def push(self, msg):
        asynchat.async_chat.push(self, msg + '\r\n')

    # Implementation of base class abstract method
    def collect_incoming_data(self, data):
        self.__line.append(data)

    # Implementation of base class abstract method
    def found_terminator(self):
        line = ''.join(self.__line)
        print >> smtpd.DEBUGSTREAM, 'Data:', repr(line)
        self.__line = []
        if self.__state == self.COMMAND:
            if not line:
                self.push('500 Error: bad syntax')
                return
            method = None
            i = line.find(' ')
            if i < 0:
                command = line.upper()
                arg = None
            else:
                command = line[:i].upper()
                arg = line[i+1:].strip()
            method = getattr(self, 'smtp_' + command, None)
            if not method:
                self.push('502 Error: command "%s" not implemented' % command)
                return
            method(arg)
            return
        else:
            if self.__state != self.DATA:
                self.push('451 Internal confusion')
                return
            # Remove extraneous carriage returns and de-transparency according
            # to RFC 821, Section 4.5.2.
            data = []
            for text in line.split('\r\n'):
                if text and text[0] == '.':
                    data.append(text[1:])
                else:
                    data.append(text)
            self.__data = '\n'.join(data)
            status = self.__server.process_message(self.__peer,
                                                   self.__mailfrom,
                                                   self.__rcpttos,
                                                   self.__data)
            self.__rcpttos = []
            self.__mailfrom = None
            self.__state = self.COMMAND
            self.set_terminator('\r\n')
            if not status:
                self.push('250 Ok')
            else:
                self.push(status)

    # SMTP and ESMTP commands
    def smtp_EHLO(self, arg):
        if not arg:
            self.push('501 Syntax: EHLO hostname')
            return
        if self.__greeting:
            self.push('503 Duplicate HELO/EHLO')
        else:
            self.__greeting = arg
            self.push('250-%s offers:' % self.__fqdn)
            self.push('250 AUTH PLAIN')

    def smtp_HELO(self, arg):
        if not arg:
            self.push('501 Syntax: HELO hostname')
            return
        if self.__greeting:
            self.push('503 Duplicate HELO/EHLO')
        else:
            self.__greeting = arg
            self.push('250 %s' % self.__fqdn)

    def smtp_AUTH(self, arg):
        encoding, pw = arg.split(' ')
        if encoding != 'PLAIN':
            self.push('501 encoding not understood')
            self.close_when_done()
            return
        z, self.address, pw = base64.b64decode(pw).split('\x00')
        if z != '':
            self.push('501 encoding not understood')
            self.close_when_done()
            return

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

        self.address = addBMIfNotPresent(self.address)

        # Each identity must be enabled independly by setting the smtppop3password for the identity
        # If no password is set, then the identity is not available for SMTP/POP3 access.
        try:
            if shared.config.getboolean(self.address, "enabled"):
                self.pw = shared.config.get(self.address, "smtppop3password")
                if pw == self.pw:
                    self.push('235 Authentication successful. Proceed.')
                    self.logged_in = True
                    return
        except:
            pass

        self.push('530 Access denied.')
        self.close_when_done()

    def smtp_NOOP(self, arg):
        if arg:
            self.push('501 Syntax: NOOP')
        else:
            self.push('250 Ok')

    def smtp_QUIT(self, arg):
        # args is ignored
        self.push('221 Bye')
        self.close_when_done()

    # factored
    def __getaddr(self, keyword, arg):
        address = None
        keylen = len(keyword)
        if arg[:keylen].upper() == keyword:
            address = arg[keylen:].strip()
            if not address:
                pass
            elif address[0] == '<' and address[-1] == '>' and address != '<>':
                # Addresses can be in the form <person@dom.com> but watch out
                # for null address, e.g. <>
                address = address[1:-1]
        return address

    def smtp_MAIL(self, arg):
        if not self.logged_in:
            self.push('503 Not authenticated.')
            self.close_when_done()
            return

        print >> smtpd.DEBUGSTREAM, '===> MAIL', arg
        address = self.__getaddr('FROM:', arg) if arg else None
        if not address:
            self.push('501 Syntax: MAIL FROM:<address>')
            return
        if self.__mailfrom:
            self.push('503 Error: nested MAIL command')
            return
        self.__mailfrom = address
        print >> smtpd.DEBUGSTREAM, 'sender:', self.__mailfrom
        self.push('250 Ok')

    def smtp_RCPT(self, arg):
        if not self.logged_in:
            self.push('503 Not authenticated.')
            self.close_when_done()
            return

        print >> smtpd.DEBUGSTREAM, '===> RCPT', arg
        if not self.__mailfrom:
            self.push('503 Error: need MAIL command')
            return
        address = self.__getaddr('TO:', arg) if arg else None
        if not address:
            self.push('501 Syntax: RCPT TO: <address>')
            return
        self.__rcpttos.append(address)
        print >> smtpd.DEBUGSTREAM, 'recips:', self.__rcpttos
        self.push('250 Ok')

    def smtp_RSET(self, arg):
        if not self.logged_in:
            self.push('503 Not authenticated.')
            self.close_when_done()
            return

        if arg:
            self.push('501 Syntax: RSET')
            return
        # Resets the sender, recipients, and data, but not the greeting
        self.__mailfrom = None
        self.__rcpttos = []
        self.__data = ''
        self.__state = self.COMMAND
        self.push('250 Ok')

    def smtp_DATA(self, arg):
        if not self.logged_in:
            self.push('503 Not authenticated.')
            self.close_when_done()
            return
        if not self.__rcpttos:
            self.push('503 Error: need RCPT command')
            return
        if arg:
            self.push('501 Syntax: DATA')
            return
        self.__state = self.DATA
        self.set_terminator('\r\n.\r\n')
        self.push('354 End data with <CR><LF>.<CR><LF>')


class bitmessageSMTPServer(smtpd.SMTPServer):
    def __init__(self):
        # TODO - move to separate file/class
        smtpport = shared.config.getint('bitmessagesettings', 'smtpport')

        self.ssl = shared.config.getboolean('bitmessagesettings', 'smtpssl')
        if self.ssl:
            self.keyfile = shared.config.get('bitmessagesettings', 'keyfile')
            self.certfile = shared.config.get('bitmessagesettings', 'certfile')

        smtpd.SMTPServer.__init__(self, ('127.0.0.1', smtpport), None)
        shared.printLock.acquire()
        print "SMTP server started"
        shared.printLock.release()

    def handle_accept(self):
        # Override SMTPServer's handle_accept so that we can start an SSL connection.
        sock, peer_address = self.accept()
        if self.ssl:
            sock = ssl.wrap_socket(sock, server_side=True, certfile=self.certfile, keyfile=self.keyfile, ssl_version=ssl.PROTOCOL_SSLv23)
            bitmessageSMTPChannel(self, sock, peer_address)

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


import sys
smtpd.DEBUGSTREAM = sys.stdout
