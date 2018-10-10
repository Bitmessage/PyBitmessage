"""
src/class_smtpServer.py
=======================

"""
# pylint: disable=attribute-defined-outside-init,unused-argument

import asyncore
import base64
import email
import re
import signal
import smtpd
import threading
import time
from email.header import decode_header
from email.parser import Parser

from version import softwareVersion

import queues
from addresses import decodeAddress
from bmconfigparser import BMConfigParser
from debug import logger
from helper_ackPayload import genAckPayload
from helper_sql import sqlExecute
from helper_threading import StoppableThread

SMTPDOMAIN = "bmaddr.lan"
LISTENPORT = 8425


class smtpServerChannel(smtpd.SMTPChannel):
    """Asyncore channel for SMTP protocol (server)"""
    def smtp_EHLO(self, arg):
        """Process an EHLO"""
        if not arg:
            self.push('501 Syntax: HELO hostname')
            return
        self.push('250-PyBitmessage %s' % softwareVersion)
        self.push('250 AUTH PLAIN')

    def smtp_AUTH(self, arg):
        """Process AUTH"""
        if not arg or arg[0:5] not in ["PLAIN"]:
            self.push('501 Syntax: AUTH PLAIN')
            return
        authstring = arg[6:]
        try:
            decoded = base64.b64decode(authstring)
            correctauth = "\x00" + BMConfigParser().safeGet("bitmessagesettings", "smtpdusername", "") + \
                "\x00" + BMConfigParser().safeGet("bitmessagesettings", "smtpdpassword", "")
            logger.debug("authstring: %s / %s", correctauth, decoded)
            if correctauth == decoded:
                self.auth = True
                self.push('235 2.7.0 Authentication successful')
            else:
                raise Exception("Auth fail")
        except BaseException:
            self.push('501 Authentication fail')

    def smtp_DATA(self, arg):
        """Process DATA"""
        if not hasattr(self, "auth") or not self.auth:
            self.push("530 Authentication required")
            return
        smtpd.SMTPChannel.smtp_DATA(self, arg)


class smtpServerPyBitmessage(smtpd.SMTPServer):
    """Asyncore SMTP server class"""
    def handle_accept(self):
        """Accept a connection"""
        pair = self.accept()
        if pair is not None:
            conn, addr = pair
            self.channel = smtpServerChannel(self, conn, addr)

    def send(self, fromAddress, toAddress, subject, message):  # pylint: disable=arguments-differ
        """Send a bitmessage"""
        status, addressVersionNumber, streamNumber, ripe = decodeAddress(toAddress)  # pylint: disable=unused-variable
        stealthLevel = BMConfigParser().safeGetInt('bitmessagesettings', 'ackstealthlevel')
        ackdata = genAckPayload(streamNumber, stealthLevel)
        sqlExecute(
            '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            '',
            toAddress,
            ripe,
            fromAddress,
            subject,
            message,
            ackdata,
            int(time.time()),  # sentTime (this will never change)
            int(time.time()),  # lastActionTime
            0,  # sleepTill time. This will get set when the POW gets done.
            'msgqueued',
            0,  # retryNumber
            'sent',  # folder
            2,  # encodingtype
            # not necessary to have a TTL higher than 2 days
            min(BMConfigParser().getint('bitmessagesettings', 'ttl'), 86400 * 2)
        )

        queues.workerQueue.put(('sendmessage', toAddress))

    def decode_header(self, hdr):
        """Email header decoding"""
        ret = []
        for h in decode_header(self.msg_headers[hdr]):
            if h[1]:
                ret.append(unicode(h[0], h[1]))
            else:
                ret.append(h[0].decode("utf-8", errors='replace'))

        return ret

    def process_message(self, peer, mailfrom, rcpttos, data):
        """Process an email"""
        # pylint: disable=too-many-locals,too-many-branches
        p = re.compile(".*<([^>]+)>")
        if not hasattr(self.channel, "auth") or not self.channel.auth:
            logger.error("Missing or invalid auth")
            return
        try:
            self.msg_headers = Parser().parsestr(data)
        except BaseException:
            logger.error("Invalid headers")
            return

        try:
            sender, domain = p.sub(r'\1', mailfrom).split("@")
            if domain != SMTPDOMAIN:
                raise Exception("Bad domain %s" % domain)
            if sender not in BMConfigParser().addresses():
                raise Exception("Nonexisting user %s" % sender)
        except Exception as err:
            logger.debug("Bad envelope from %s: %s", mailfrom, repr(err))
            msg_from = self.decode_header("from")
            try:
                msg_from = p.sub(r'\1', self.decode_header("from")[0])
                sender, domain = msg_from.split("@")
                if domain != SMTPDOMAIN:
                    raise Exception("Bad domain %s" % domain)
                if sender not in BMConfigParser().addresses():
                    raise Exception("Nonexisting user %s" % sender)
            except Exception as err:
                logger.error("Bad headers from %s: %s", msg_from, repr(err))
                return

        try:
            msg_subject = self.decode_header('subject')[0]
        except BaseException:
            msg_subject = "Subject missing..."

        msg_tmp = email.message_from_string(data)
        body = u''
        for part in msg_tmp.walk():
            if part and part.get_content_type() == "text/plain":
                body += part.get_payload(decode=1).decode(part.get_content_charset('utf-8'), errors='replace')

        for to in rcpttos:
            try:
                rcpt, domain = p.sub(r'\1', to).split("@")
                if domain != SMTPDOMAIN:
                    raise Exception("Bad domain %s" % domain)
                logger.debug("Sending %s to %s about %s", sender, rcpt, msg_subject)
                self.send(sender, rcpt, msg_subject, body)
                logger.info("Relayed %s to %s", sender, rcpt)
            except Exception as err:
                logger.error("Bad to %s: %s", to, repr(err))
                continue
        return


class smtpServer(threading.Thread, StoppableThread):
    """SMTP server thread"""
    def __init__(self, parent=None):
        threading.Thread.__init__(self, name="smtpServerThread")
        self.initStop()
        self.server = smtpServerPyBitmessage(('127.0.0.1', LISTENPORT), None)

    def stopThread(self):
        super(smtpServer, self).stopThread()
        self.server.close()
        return

    def run(self):
        asyncore.loop(1)


def signals(sig, frame):
    """Signal handler"""
    print "Got signal, terminating"
    for thread in threading.enumerate():
        if thread.isAlive() and isinstance(thread, StoppableThread):
            thread.stopThread()


def runServer():
    """Run SMTP server as a standalone python process"""
    print "Running SMTPd thread"
    smtpThread = smtpServer()
    smtpThread.start()
    signal.signal(signal.SIGINT, signals)
    signal.signal(signal.SIGTERM, signals)
    print "Processing"
    smtpThread.join()
    print "The end"


if __name__ == "__main__":
    runServer()
