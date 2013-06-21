import threading
import shared
import socket

from class_sendDataThread import *
from class_receiveDataThread import *

# Only one singleListener thread will ever exist. It creates the
# receiveDataThread and sendDataThread for each incoming connection. Note
# that it cannot set the stream number because it is not known yet- the
# other node will have to tell us its stream number in a version message.
# If we don't care about their stream, we will close the connection
# (within the recversion function of the recieveData thread)


class singleListener(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # We don't want to accept incoming connections if the user is using a
        # SOCKS proxy. If they eventually select proxy 'none' then this will
        # start listening for connections.
        while shared.config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
            time.sleep(300)

        shared.printLock.acquire()
        print 'Listening for incoming connections.'
        shared.printLock.release()
        HOST = ''  # Symbolic name meaning all available interfaces
        PORT = shared.config.getint('bitmessagesettings', 'port')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # This option apparently avoids the TIME_WAIT state so that we can
        # rebind faster
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(2)

        while True:
            # We don't want to accept incoming connections if the user is using
            # a SOCKS proxy. If the user eventually select proxy 'none' then
            # this will start listening for connections.
            while shared.config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
                time.sleep(10)
            while len(shared.connectedHostsList) > 220:
                shared.printLock.acquire()
                print 'We are connected to too many people. Not accepting further incoming connections for ten seconds.'
                shared.printLock.release()
                time.sleep(10)
            a, (HOST, PORT) = sock.accept()

            # The following code will, unfortunately, block an incoming
            # connection if someone else on the same LAN is already connected
            # because the two computers will share the same external IP. This
            # is here to prevent connection flooding.
            while HOST in shared.connectedHostsList:
                shared.printLock.acquire()
                print 'We are already connected to', HOST + '. Ignoring connection.'
                shared.printLock.release()
                a.close()
                a, (HOST, PORT) = sock.accept()
            objectsOfWhichThisRemoteNodeIsAlreadyAware = {}
            a.settimeout(20)

            sd = sendDataThread()
            sd.setup(
                a, HOST, PORT, -1, objectsOfWhichThisRemoteNodeIsAlreadyAware)
            sd.start()

            rd = receiveDataThread()
            rd.daemon = True  # close the main program even if there are threads left
            rd.setup(
                a, HOST, PORT, -1, objectsOfWhichThisRemoteNodeIsAlreadyAware)
            rd.start()

            shared.printLock.acquire()
            print self, 'connected to', HOST, 'during INCOMING request.'
            shared.printLock.release()
