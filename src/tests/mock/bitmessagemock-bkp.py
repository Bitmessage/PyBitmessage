"""
Bitmessage mock
"""
from pybitmessage.class_addressGenerator import addressGenerator
from pybitmessage.class_singleWorker import singleWorker
from pybitmessage.class_objectProcessor import objectProcessor
from pybitmessage.inventory import Inventory
from pybitmessage.bmconfigparser import BMConfigParser
from pybitmessage.class_singleCleaner import singleCleaner
from pybitmessage import state
from pybitmessage.network.threads import StoppableThread

# from pybitmessage.network.connectionpool import BMConnectionPool
# from pybitmessage.network.networkthread import BMNetworkThread
# from pybitmessage.network.receivequeuethread import ReceiveQueueThread

# pylint: disable=too-few-public-methods,no-init,old-style-class
class MockMain:
    """Mock main function"""

    # pylint: disable=no-self-use
    def start(self):
        """Start main application"""
        # pylint: disable=too-many-statements,too-many-branches,too-many-locals, unused-variable
        config = BMConfigParser()
        daemon = config.safeGetBoolean('bitmessagesettings', 'daemon')

        # Start the address generation thread
        addressGeneratorThread = addressGenerator()
        # close the main program even if there are threads left
        addressGeneratorThread.daemon = True
        addressGeneratorThread.start()

        # Start the thread that calculates POWs
        singleWorkerThread = singleWorker()
        # close the main program even if there are threads left
        singleWorkerThread.daemon = True
        singleWorkerThread.start()

        # Start the thread that calculates POWs
        objectProcessorThread = objectProcessor()
        # DON'T close the main program even the thread remains.
        # This thread checks the shutdown variable after processing
        # each object.
        objectProcessorThread.daemon = False
        objectProcessorThread.start()

        Inventory()  # init

#         # Start the cleanerThread
        singleCleanerThread = singleCleaner()
#         # close the main program even if there are threads left
        singleCleanerThread.daemon = True
        singleCleanerThread.start()
        # Not needed if objproc disabled
        # if state.enableObjProc:
        #     shared.reloadMyAddressHashes()
        #     shared.reloadBroadcastSendersForWhichImWatching()
            # API is also objproc dependent
            # if config.safeGetBoolean('bitmessagesettings', 'apienabled'):
            #     # pylint: disable=relative-import
            #     from pybitmessage import api
            #     singleAPIThread = api.singleAPI()
            #     # close the main program even if there are threads left
            #     singleAPIThread.daemon = True
            #     singleAPIThread.start()

#         # start network components if networking is enabled
        # if state.enableNetwork:
        #     # start_proxyconfig()
        #     # BMConnectionPool().connectToStream(1)
        #     asyncoreThread = BMNetworkThread()
        #     asyncoreThread.daemon = True
        #     asyncoreThread.start()
            
        #     for i in range(config.safeGet('threads', 'receive')):
        #         receiveQueueThread = ReceiveQueueThread(i)
        #         receiveQueueThread.daemon = True
        #         receiveQueueThread.start()
            # announceThread = AnnounceThread()
            # announceThread.daemon = True
            # announceThread.start()
            # state.invThread = InvThread()
            # state.invThread.daemon = True
            # state.invThread.start()
            # state.addrThread = AddrThread()
            # state.addrThread.daemon = True
            # state.addrThread.start()
            # state.downloadThread = DownloadThread()
            # state.downloadThread.daemon = True
            # state.downloadThread.start()
            # state.uploadThread = UploadThread()
            # state.uploadThread.daemon = True
            # state.uploadThread.start()

#             if config.safeGetBoolean('bitmessagesettings', 'upnp'):
#                 import upnp
#                 upnpThread = upnp.uPnPThread()
#                 upnpThread.start()
#         else:
#             # Populate with hardcoded value (same as connectToStream above)
#             state.streamsInWhichIAmParticipating.append(1)
        # if not daemon and state.enableGUI:
        #     if state.curses:
        #         if not depends.check_curses():
        #             sys.exit()
        #         print('Running with curses')
        #         import bitmessagecurses
        #         bitmessagecurses.runwrapper()

            # config.remove_option('bitmessagesettings', 'dontconnect')
            # pylint: disable=no-member,import-error,no-name-in-module,relative-import
        from pybitmessage.mpybit import NavigateApp
        state.kivyapp = NavigateApp()
        print('NavigateApp() ----------------------')
        state.kivyapp.run()
        print('state.kivyapp.run() ----------------------')


        # else:
        #     config.remove_option('bitmessagesettings', 'dontconnect')

#         if daemon:
#             while state.shutdown == 0:
#                 time.sleep(1)
#                 if (
#                     state.testmode
#                     and time.time() - state.last_api_response >= 30
#                 ):
#                     self.stop()
#         elif not state.enableGUI:
#             state.enableGUI = True
#             # pylint: disable=relative-import
#             from tests import core as test_core
#             test_core_result = test_core.run()
#             state.enableGUI = True
#             self.stop()
#             test_core.cleanup()
#             sys.exit(
#                 'Core tests failed!'
#                 if test_core_result.errors or test_core_result.failures
#                 else 0
#             )

#     @staticmethod
#     def daemonize():
#         """Running as a daemon. Send signal in end."""
#         grandfatherPid = os.getpid()
#         parentPid = None
#         try:
#             if os.fork():
#                 # unlock
#                 state.thisapp.cleanup()
#                 # wait until grandchild ready
#                 while True:
#                     time.sleep(1)

#                 os._exit(0)  # pylint: disable=protected-access
#         except AttributeError:
#             # fork not implemented
#             pass
#         else:
#             parentPid = os.getpid()
#             state.thisapp.lock()  # relock

#         os.umask(0)
#         try:
#             os.setsid()
#         except AttributeError:
#             # setsid not implemented
#             pass
#         try:
#             if os.fork():
#                 # unlock
#                 state.thisapp.cleanup()
#                 # wait until child ready
#                 while True:
#                     time.sleep(1)
#                 os._exit(0)  # pylint: disable=protected-access
#         except AttributeError:
#             # fork not implemented
#             pass
#         else:
#             state.thisapp.lock()  # relock
#         state.thisapp.lockPid = None  # indicate we're the final child
#         sys.stdout.flush()
#         sys.stderr.flush()
#         if not sys.platform.startswith('win'):
#             si = file(os.devnull, 'r')
#             so = file(os.devnull, 'a+')
#             se = file(os.devnull, 'a+', 0)
#             os.dup2(si.fileno(), sys.stdin.fileno())
#             os.dup2(so.fileno(), sys.stdout.fileno())
#             os.dup2(se.fileno(), sys.stderr.fileno())
#         if parentPid:
#             # signal ready
#             os.kill(parentPid, signal.SIGTERM)
#             os.kill(grandfatherPid, signal.SIGTERM)

#     @staticmethod
#     def setSignalHandler():
#         """Setting the Signal Handler"""
#         signal.signal(signal.SIGINT, signal_handler)
#         signal.signal(signal.SIGTERM, signal_handler)
#         # signal.signal(signal.SIGINT, signal.SIG_DFL)

#     @staticmethod
#     def usage():
#         """Displaying the usages"""
#         print('Usage: ' + sys.argv[0] + ' [OPTIONS]')
#         print('''
# Options:
#   -h, --help            show this help message and exit
#   -c, --curses          use curses (text mode) interface
#   -d, --daemon          run in daemon (background) mode
#   -t, --test            dryrun, make testing

# All parameters are optional.
# ''')

#     @staticmethod
#     def stop():
#         """Stop main application"""
#         with printLock:
#             print('Stopping Bitmessage Deamon.')
#         shutdown.doCleanShutdown()

#     # .. todo:: nice function but no one is using this
#     @staticmethod
#     def getApiAddress():
#         """This function returns API address and port"""
#         if not BMConfigParser().safeGetBoolean(
#                 'bitmessagesettings', 'apienabled'):
#             return None
#         address = BMConfigParser().get('bitmessagesettings', 'apiinterface')
#         port = BMConfigParser().getint('bitmessagesettings', 'apiport')
#         return {'address': address, 'port': port}

# def start_proxyconfig():
#     """Check socksproxytype and start any proxy configuration plugin"""
#     if not get_plugin:
#         return
#     config = BMConfigParser()
#     proxy_type = config.safeGet('bitmessagesettings', 'socksproxytype')
#     if proxy_type and proxy_type not in ('none', 'SOCKS4a', 'SOCKS5'):
#         try:
#             proxyconfig_start = time.time()
#             if not get_plugin('proxyconfig', name=proxy_type)(config):
#                 raise TypeError()
#         except TypeError:
#             # cannot import shutdown here ):
#             logger.error(
#                 'Failed to run proxy config plugin %s',
#                 proxy_type, exc_info=True)
#             os._exit(0)  # pylint: disable=protected-access
#         else:
#             logger.info(
#                 'Started proxy config plugin %s in %s sec',
#                 proxy_type, time.time() - proxyconfig_start)



# class AnnounceThread(StoppableThread):
#     """A thread to manage regular announcing of this node"""
#     name = "Announcer"

#     def run(self):
#         lastSelfAnnounced = 0
#         while not self._stopped and state.shutdown == 0:
#             processed = 0
#             if lastSelfAnnounced < time.time() - UDPSocket.announceInterval:
#                 self.announceSelf()
#                 lastSelfAnnounced = time.time()
#             if processed == 0:
#                 self.stop.wait(10)

    # @staticmethod
    # def announceSelf():
    #     """Announce our presence"""
    #     for connection in [udpSockets for udpSockets in BMConnectionPool().udpSockets.values()]:
    #         if not connection.announcing:
    #             continue
    #         for stream in state.streamsInWhichIAmParticipating:
    #             addr = (
    #                 stream,
    #                 #     state.Peer('127.0.0.1',int( BMConfigParser().safeGet("bitmessagesettings", "port"))),
    #                 #     int(time.time()))
    #                 # connection.append_write_buf(BMProto.assembleAddr([addr]))
    #                 Peer(
    #                     '127.0.0.1',
    #                     BMConfigParser().safeGetInt(
    #                         'bitmessagesettings', 'port')),
    #                 time.time())
    #             connection.append_write_buf(assemble_addr([addr]))


def main():
    """Triggers main module"""
    mainprogram = MockMain()
    mainprogram.start()


if __name__ == "__main__":
    main()
