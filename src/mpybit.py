from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from os import environ

# environ['BITMESSAGE_HOME'] = '~/home/cis/Desktop/pybit'
# environ['HOME'] = '~/home/cis/Desktop/pybit'

from bmconfigparser import BMConfigParser
from helper_ackPayload import genAckPayload
from addresses import decodeAddress, addBMIfNotPresent
from class_sqlThread import sqlThread
from helper_sql import sqlQuery, sqlExecute, sqlExecuteChunked, sqlStoredProcedure
import time
import queues
import state
import threading
import shutdown
from inventory import Inventory
statusIconColor = 'red'


class Login_Screen(BoxLayout):


    def send(self):
        # print(len(Inventory()), "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
        # print(len(Inventory().unexpired_hashes_by_stream(1)), "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDdd")
        queues.apiAddressGeneratorReturnQueue.queue.clear()
        streamNumberForAddress = 1
        label = "CisDevelper"
        eighteenByteRipe = False
        nonceTrialsPerByte = 1000
        payloadLengthExtraBytes = 1000
        print("BREAK POINT STARTING @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        queues.addressGeneratorQueue.put( (
            'createRandomAddress', 4, streamNumberForAddress, label, 1, "", eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes )
        )
        print(BMConfigParser().sections(), "BMConfigParser().sections()")
        fromAddress = queues.apiAddressGeneratorReturnQueue.get()
        print("BREAK POINT ENDING //////////////////////////////////////////////////////////////////")
        # toAddress = "BM-NBqmcWH5XJMmXCVxD4HVTNPe3naGgHgE"
        toAddress = "BM-2cWyUfBdY2FbgyuCb7abFZ49JYxSzUhNFe"
        message = self.ids.user_input.text
        subject = 'Test'
        encoding = 3
        print("message: ", self.ids.user_input.text)
        sendMessageToPeople = True
        if sendMessageToPeople:
            if toAddress != '':
                status, addressVersionNumber, streamNumber, ripe = decodeAddress(toAddress)
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
                    t = ()
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
                    toLabel = ''
                    # queryreturn = sqlQuery('''select status from sent''')
                    # if queryreturn != []:
                    #     for row in queryreturn:
                    #         print(row, "YZYZYZYZYZYZYZYZYZYZYZYZYZYZYZYZYZYZYZYZYZYZZYZYZYZYZYZYZYZYZY")
                    #         toLabel, = row
                    queues.workerQueue.put(('sendmessage', toAddress))
                    print("sqlExecute successfully #####    ##################")
                    
                    # App.get_running_app().stop()
                    # Window.close()
                    # shutdown.doCleanShutdown()
                    for i in threading.enumerate(): 
                        print (i.name)
                    # from threading import Timer
                    # t = Timer(300.0, connectedHostsList())
                    # t.start()
                    # print(connectedHostsList())
                    print("calling connectios")
                    return None

    def say_exit(self):
        print ("**************************EXITING FROM APPLICATION*****************************")
        shutdown.doCleanShutdown()
        Window.close()

class MainApp(App):


    def build(self):
        return Login_Screen()
