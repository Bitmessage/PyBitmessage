"""
src/class_smtpDeliver.py
========================
"""
# pylint: disable=unused-variable

import smtplib
import sys
import threading
import urlparse
from email.header import Header
from email.mime.text import MIMEText

import queues
import state
from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread

SMTPDOMAIN = "bmaddr.lan"


class smtpDeliver(threading.Thread, StoppableThread):
    """SMTP client thread for delivery"""
    _instance = None

    def __init__(self):
        threading.Thread.__init__(self, name="smtpDeliver")
        self.initStop()

    def stopThread(self):
        try:
            queues.UISignallerQueue.put(("stopThread", "data"))  # pylint: disable=no-member
        except:
            pass
        super(smtpDeliver, self).stopThread()

    @classmethod
    def get(cls):
        """(probably) Singleton functionality"""
        if not cls._instance:
            cls._instance = smtpDeliver()
        return cls._instance

    def run(self):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        while state.shutdown == 0:
            command, data = queues.UISignalQueue.get()
            if command == 'writeNewAddressToTable':
                label, address, streamNumber = data
            elif command == 'updateStatusBar':
                pass
            elif command == 'updateSentItemStatusByToAddress':
                toAddress, message = data
            elif command == 'updateSentItemStatusByAckdata':
                ackData, message = data
            elif command == 'displayNewInboxMessage':
                inventoryHash, toAddress, fromAddress, subject, body = data
                dest = BMConfigParser().safeGet("bitmessagesettings", "smtpdeliver", '')
                if dest == '':
                    continue
                try:
                    u = urlparse.urlparse(dest)
                    to = urlparse.parse_qs(u.query)['to']
                    client = smtplib.SMTP(u.hostname, u.port)
                    msg = MIMEText(body, 'plain', 'utf-8')
                    msg['Subject'] = Header(subject, 'utf-8')
                    msg['From'] = fromAddress + '@' + SMTPDOMAIN
                    toLabel = map(  # pylint: disable=deprecated-lambda
                        lambda y: BMConfigParser().safeGet(y, "label"),
                        filter(  # pylint: disable=deprecated-lambda
                            lambda x: x == toAddress, BMConfigParser().addresses())
                    )
                    if toLabel:
                        msg['To'] = "\"%s\" <%s>" % (Header(toLabel[0], 'utf-8'), toAddress + '@' + SMTPDOMAIN)
                    else:
                        msg['To'] = toAddress + '@' + SMTPDOMAIN
                    client.ehlo()
                    client.starttls()
                    client.ehlo()
                    client.sendmail(msg['From'], [to], msg.as_string())
                    logger.info("Delivered via SMTP to %s through %s:%i ...", to, u.hostname, u.port)
                    client.quit()
                except:
                    logger.error("smtp delivery error", exc_info=True)
            elif command == 'displayNewSentMessage':
                toAddress, fromLabel, fromAddress, subject, message, ackdata = data
            elif command == 'updateNetworkStatusTab':
                pass
            elif command == 'updateNumberOfMessagesProcessed':
                pass
            elif command == 'updateNumberOfPubkeysProcessed':
                pass
            elif command == 'updateNumberOfBroadcastsProcessed':
                pass
            elif command == 'setStatusIcon':
                pass
            elif command == 'changedInboxUnread':
                pass
            elif command == 'rerenderMessagelistFromLabels':
                pass
            elif command == 'rerenderMessagelistToLabels':
                pass
            elif command == 'rerenderAddressBook':
                pass
            elif command == 'rerenderSubscriptions':
                pass
            elif command == 'rerenderBlackWhiteList':
                pass
            elif command == 'removeInboxRowByMsgid':
                pass
            elif command == 'newVersionAvailable':
                pass
            elif command == 'alert':
                title, text, exitAfterUserClicksOk = data
            elif command == 'stopThread':
                break
            else:
                sys.stderr.write(
                    'Command sent to smtpDeliver not recognized: %s\n' % command)
