import threading

import time


from addresses import addBMIfNotPresent, decodeAddress

from bmconfigparser import BMConfigParser

from helper_ackPayload import genAckPayload


from helper_sql import sqlExecute


from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout

import queues

import shutdown
statusIconColor = 'red'


class LoginScreen(BoxLayout):
    """This will use for sending message to recipents from mobile client."""

    def send(self):
        """Send used for sending message with title and body."""
        queues.apiAddressGeneratorReturnQueue.queue.clear()
        streamNumberForAddress = 1
        label = "CisDevelper"
        eighteenByteRipe = False
        nonceTrialsPerByte = 1000
        payloadLengthExtraBytes = 1000
        print("BREAK POINT STARTING")
        queues.addressGeneratorQueue.put(
                                        (
                                            'createRandomAddress', 4,
                                            streamNumberForAddress, label, 1,
                                            "", eighteenByteRipe, nonceTrialsPerByte,
                                            payloadLengthExtraBytes
                                        )
        )
        print(BMConfigParser().sections(), "BMConfigParser().sections()")
        fromAddress = queues.apiAddressGeneratorReturnQueue.get()
        print("BREAK POINT ENDING")
        toAddress = "BM-2cWyUfBdY2FbgyuCb7abFZ49JYxSzUhNFe"
        message = self.ids.user_input.text
        subject = 'Test'
        encoding = 3
        print("message: ", self.ids.user_input.text)
        sendMessageToPeople = True
        if sendMessageToPeople:
            if toAddress != '':
                status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                    toAddress)
                if status == 'success':
                    toAddress = addBMIfNotPresent(toAddress)

                    if addressVersionNumber > 4 or addressVersionNumber <= 1:
                        print("addressVersionNumber > 4 or addressVersionNumber <= 1")
                    if streamNumber > 1 or streamNumber == 0:
                        print("streamNumber > 1 or streamNumber == 0")
                    if statusIconColor == 'red':
                        print("shared.statusIconColor == 'red'")
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
                    print("sqlExecute successfully #####    ##################")
                    for i in threading.enumerate():
                        print(i.name)
                    return None

    def sayexit(self):
        print("**************************EXITING FROM APPLICATION*****************************")
        shutdown.doCleanShutdown()
        Window.close()


class MainApp(App):

    def build(self):
        return LoginScreen()
