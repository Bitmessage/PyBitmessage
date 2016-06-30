from email.mime.text import MIMEText
import smtplib
import sys
import threading
import urlparse

from debug import logger
from helper_threading import *
import shared

SMTPDOMAIN = "bmaddr.lan"

class smtpDeliver(threading.Thread, StoppableThread):
    _instance = None

    def __init__(self, parent=None):
        threading.Thread.__init__(self, name="smtpDeliver")
        self.initStop()
        
    def stopThread(self):
        try:
            shared.UISignallerQueue.put(("stopThread", "data"))
        except:
            pass
        super(smtpDeliver, self).stopThread()

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = UISignaler()
        return cls._instance

    def run(self):
        while shared.shutdown == 0:
            command, data = shared.UISignalQueue.get()
            if command == 'writeNewAddressToTable':
                label, address, streamNumber = data
                pass
            elif command == 'updateStatusBar':
                pass
            elif command == 'updateSentItemStatusByToAddress':
                toAddress, message = data
                pass
            elif command == 'updateSentItemStatusByAckdata':
                ackData, message = data
                pass
            elif command == 'displayNewInboxMessage':
                inventoryHash, toAddress, fromAddress, subject, body = data
                dest = shared.config.get("bitmessagesettings", "smtpdeliver", None)
                if not dest:
                    continue
                try:
                    u = urlparse.urlparse(dest)
                    to = urlparse.parse_qs(u.query)['to']
                    client = smtplib.SMTP(u.hostname, u.port)
                    msg = MIMEText(body, 'plain', 'utf-8')
                    msg['Subject'] = subject
                    msg['From'] = fromAddress + '@' + SMTPDOMAIN
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
                pass
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
                pass
            elif command == 'stopThread':
                break
            else:
                sys.stderr.write(
                    'Command sent to smtpDeliver not recognized: %s\n' % command)
