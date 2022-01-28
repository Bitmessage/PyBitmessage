"""
SMTP client thread for delivering emails
"""
# pylint: disable=unused-variable

import smtplib
import urlparse
from email.header import Header
from email.mime.text import MIMEText

import queues
import state
from bmconfigparser import config
from network.threads import StoppableThread

SMTPDOMAIN = "bmaddr.lan"


class smtpDeliver(StoppableThread):
    """SMTP client thread for delivery"""
    name = "smtpDeliver"
    _instance = None

    def stopThread(self):
        # pylint: disable=no-member
        try:
            queues.UISignallerQueue.put(("stopThread", "data"))
        except:  # noqa:E722
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
        # pylint: disable=deprecated-lambda
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
                dest = config.safeGet("bitmessagesettings", "smtpdeliver", '')
                if dest == '':
                    continue
                try:
                    u = urlparse.urlparse(dest)
                    to = urlparse.parse_qs(u.query)['to']
                    client = smtplib.SMTP(u.hostname, u.port)
                    msg = MIMEText(body, 'plain', 'utf-8')
                    msg['Subject'] = Header(subject, 'utf-8')
                    msg['From'] = fromAddress + '@' + SMTPDOMAIN
                    toLabel = map(
                        lambda y: config.safeGet(y, "label"),
                        filter(
                            lambda x: x == toAddress, config.addresses())
                    )
                    if toLabel:
                        msg['To'] = "\"%s\" <%s>" % (Header(toLabel[0], 'utf-8'), toAddress + '@' + SMTPDOMAIN)
                    else:
                        msg['To'] = toAddress + '@' + SMTPDOMAIN
                    client.ehlo()
                    client.starttls()
                    client.ehlo()
                    client.sendmail(msg['From'], [to], msg.as_string())
                    self.logger.info(
                        'Delivered via SMTP to %s through %s:%i ...',
                        to, u.hostname, u.port)
                    client.quit()
                except:  # noqa:E722
                    self.logger.error('smtp delivery error', exc_info=True)
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
                self.logger.warning(
                    'Command sent to smtpDeliver not recognized: %s', command)
