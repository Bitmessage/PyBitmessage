import threading
import shared
import socket
from class_sendDataThread import *
from class_receiveDataThread import *
import helper_bootstrap

# Only one singleListener thread will ever exist. It creates the
# receiveDataThread and sendDataThread for each incoming connection. Note
# that it cannot set the stream number because it is not known yet- the
# other node will have to tell us its stream number in a version message.
# If we don't care about their stream, we will close the connection
# (within the recversion function of the recieveData thread)


class singleListener(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def setup(self, selfInitiatedConnections):
        self.selfInitiatedConnections = selfInitiatedConnections

    def run(self):
        while shared.safeConfigGetBoolean('bitmessagesettings', 'dontconnect'):
            time.sleep(1)
        helper_bootstrap.dns()
        # We typically don't want to accept incoming connections if the user is using a
        # SOCKS proxy, unless they have configured otherwise. If they eventually select
        # proxy 'none' or configure SOCKS listening then this will start listening for
        # connections.
        while shared.config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS' and not shared.config.getboolean('bitmessagesettings', 'sockslisten'):
            time.sleep(5)

        with shared.printLock:
            print 'Listening for incoming connections.'

        HOST = ''  # Symbolic name meaning all available interfaces
        PORT = shared.config.getint('bitmessagesettings', 'port')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # This option apparently avoids the TIME_WAIT state so that we can
        # rebind faster
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(2)

        while True:
            # We typically don't want to accept incoming connections if the user is using a
            # SOCKS proxy, unless they have configured otherwise. If they eventually select
            # proxy 'none' or configure SOCKS listening then this will start listening for
            # connections.
            while shared.config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS' and not shared.config.getboolean('bitmessagesettings', 'sockslisten'):
                time.sleep(10)
            while len(shared.connectedHostsList) > 220:
                with shared.printLock:
                    print 'We are connected to too many people. Not accepting further incoming connections for ten seconds.'

                time.sleep(10)
            a, (HOST, PORT) = sock.accept()

            # The following code will, unfortunately, block an incoming
            # connection if someone else on the same LAN is already connected
            # because the two computers will share the same external IP. This
            # is here to prevent connection flooding.
            while HOST in shared.connectedHostsList:
                with shared.printLock:
                    print 'We are already connected to', HOST + '. Ignoring connection.'

                a.close()
                a, (HOST, PORT) = sock.accept()
            someObjectsOfWhichThisRemoteNodeIsAlreadyAware = {} # This is not necessairly a complete list; we clear it from time to time to save memory.
            sendDataThreadQueue = Queue.Queue() # Used to submit information to the send data thread for this connection.
            a.settimeout(20)

            sd = sendDataThread(sendDataThreadQueue)
            sd.setup(
                a, HOST, PORT, -1, someObjectsOfWhichThisRemoteNodeIsAlreadyAware)
            sd.start()

            rd = receiveDataThread()
            rd.daemon = True  # close the main program even if there are threads left
            rd.setup(
                a, HOST, PORT, -1, someObjectsOfWhichThisRemoteNodeIsAlreadyAware, self.selfInitiatedConnections, sendDataThreadQueue)
            rd.start()

            with shared.printLock:
                print self, 'connected to', HOST, 'during INCOMING request.'

