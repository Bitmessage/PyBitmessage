import time

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.gridlayout import GridLayout

from debug import logger

from addresses import addBMIfNotPresent, decodeAddress

from bmconfigparser import BMConfigParser

from helper_ackPayload import genAckPayload

from helper_sql import sqlExecute

import queues

import shutdown
statusIconColor = 'red'


class LoginScreen(BoxLayout):
    """This will use for sending message to recipents from mobile client."""

    def send(self):
        """It is used for sending message with subject and body."""
        queues.apiAddressGeneratorReturnQueue.queue.clear()
        streamNumberForAddress = 1
        label = "CisDevelper"
        eighteenByteRipe = False
        nonceTrialsPerByte = 1000
        payloadLengthExtraBytes = 1000
        queues.addressGeneratorQueue.put((
            'createRandomAddress', 4,
            streamNumberForAddress, label, 1,
            "", eighteenByteRipe, nonceTrialsPerByte,
            payloadLengthExtraBytes
        ))
        fromAddress = queues.apiAddressGeneratorReturnQueue.get()
        toAddress = "BM-2cWyUfBdY2FbgyuCb7abFZ49JYxSzUhNFe"
        message = self.ids.user_input.text
        subject = 'Test'
        encoding = 3
        sendMessageToPeople = True
        if sendMessageToPeople:
            if toAddress != '':
                status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                    toAddress)
                if status == 'success':
                    toAddress = addBMIfNotPresent(toAddress)

                    if addressVersionNumber > 4 or addressVersionNumber <= 1:
                        logger.info("addressVersionNumber > 4 or addressVersionNumber <= 1")
                    if streamNumber > 1 or streamNumber == 0:
                        logger.info("streamNumber > 1 or streamNumber == 0")
                    if statusIconColor == 'red':
                        logger.info("shared.statusIconColor == 'red'")
                    stealthLevel = BMConfigParser().safeGetInt(
                        'bitmessagesettings', 'ackstealthlevel')
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
                        int(time.time()),
                        int(time.time()),
                        0,
                        'msgqueued',
                        0,
                        'sent',
                        encoding,
                        BMConfigParser().getint('bitmessagesettings', 'ttl'))
                    queues.workerQueue.put(('sendmessage', toAddress))
                    return None

    def sayexit(self):
        """Method will exit the application screen."""
        shutdown.doCleanShutdown()
        Window.close()


class MainApp(App):
    """The App class is the base for creating Kivy applications
    Think of it as your main entry point into the Kivy run loop."""

    def build(self):
        """To initialize an app with a widget tree, we need to override the build().
        method in our app class and return the widget tree which we have constructed..
        """
        return LoginScreen()
