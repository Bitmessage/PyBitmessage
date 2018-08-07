# Copyright (c) 2012-2016 Jonathan Warren
# Copyright (c) 2012-2018 The Bitmessage developers

# This is not what you run to run the Bitmessage API. Instead, enable the API
# ( https://bitmessage.org/wiki/API ) and optionally enable daemon mode
# ( https://bitmessage.org/wiki/Daemon ) then run bitmessagemain.py.


import time
import sys
# import errno
import threading

try:
    # import SocketServer
    from SocketServer import BaseServer
    from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer, SimpleXMLRPCDispatcher
    from thread import start_new_thread
except ImportError:
    from socketserver import BaseServer
    from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer, SimpleXMLRPCDispatcher
    from _thread import start_new_thread

import ssl
import socket

# from services import BMConfigParser, state, APIError, varintDecodeError, Services, logger
from services import *

DEFAULTKEYFILE = 'sslkeys/key.pem'
DEFAULTFILE = 'sslkeys/cert.pem'


def __repr__(self):
    return '<%s.%s object at %s>' % (
        self.__class__.__module__,
        self.__class__.__name__,
        hex(id(self))
        )


class CustomThreadingMixIn:
    """Mix-in class to handle each resquest in new thread."""
    # Decides how threads will act upon termination of the main process

    daemon_threads = True

    def process_request_thread(self, request, client_address):
        """Same as in BaseServer but as a thread.
        In addition, exception handling is done here.
        """
        try:
            self.finish_request(request, client_address)
            self.close_request(request)

        except socket.error as err:
            logger.warning('socket.error finishing request from "%s"; Error: %s' % (client_address, str(err)))
            self.close_request(request)
        except Exception:
            self.handle_error(request, client_address)
            self.close_request(request)

    def process_request(self, request, client_address):
        """Start a new thread to process the request."""
        t = threading.Thread(target=self.process_request_thread, args=(request, client_address))
        if self.daemon_threads:
            t.setDaemon(1)
        t.start()


class VerifyingRequestHandler(SimpleXMLRPCRequestHandler):
    cookies = []

    def setup(self):
        self.connection = self.request
        self.rfile = socket.socket.makefile(self.request, 'rb', self.rbufsize)
        self.wfile = socket.socket.makefile(self.request, 'wb', self.wbufsize)

    def address_string(self):
        """Getting 'FQDN' from host seems to stall on some ip address, so... just (quickly!) return raw host address"""
        host, port = self.client_address[:2]
        # return socket.getfqdn(host)
        return host

    def do_POST(self):
        """ Handles the HTTP(S) POST request.
        It was copied out from SimpleXMLRPCServer.py and modified to shutdown the socket cleanly and handle cookies.

        Attempts to interpret all HTTP POST requests as XML-RPC calls,
        which are forwarded to the server's _dispatch method for handling.
        """

        # Check that the path is legal
        if not self.is_rpc_path_valid():
            self.report_404()
            return

        try:
            # Get arguments by reading body of request.
            # We read this in chunks to avoid straining
            # socket.read(); around the 10 or 15Mb mark, some platforms
            # begin to have problems (bug #792570).
            max_chunk_size = 10 * 1024 * 1024
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                chunk = self.rfile.read(chunk_size)
                if not chunk:
                    break
                L.append(chunk)
                size_remaining -= len(L[-1])
            data = b''.join(L)

            # skip encoding checking
            # data = SimpleXMLRPCRequestHandler.decode_request_content(data)
            # if data is None:
            #     return  # response has been sent

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(
                data, getattr(self, '_dispatch', None), self.path
            )
        except Exception as err:  # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            logger.exception('do_POST Exception:')
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            # zip encoding request ignored //self.encode_threshold 1400(default)
            self.send_header("Content-length", str(len(response)))

            # HACK :start -> sends cookies here
            if self.cookies:
                for cookie in self.cookies:
                    self.send_header('Set-Cookie', cookie.output(header=''))
            # HACK :end

            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown(1)

        return

    def do_GET(self):
        if not self.is_rpc_path_valid():
            self.report_404()
            return

        response = self.server.generate_html_documentation()
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

        # shut down the connection
        self.wfile.flush()
        self.connection.shutdown(1)

        return

    def report_404 (self):
            # Report a 404 error
        self.send_response(404)
        response = b'No such page'
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        # shut down the connection
        self.wfile.flush()
        self.connection.shutdown(1)

    def parse_request(self):
        """Http version checking and connection close, force Basic Authentication"""

        import base64
        try:
            from urllib import unquote as unquote_to_bytes
        except ImportError:
            from urllib.parse import unquote_to_bytes

        isValid = False
        if SimpleXMLRPCRequestHandler.parse_request(self):
            enctype, encstr = self.headers.get('Authorization').split()
            encstr = base64.b64decode(encstr).decode("utf-8")
            emailid, password = encstr.split(':')
            emailid = unquote_to_bytes(emailid).decode("utf-8")
            password = unquote_to_bytes(password).decode("utf-8")
            isValid = emailid == BMConfigParser().get('bitmessagesettings', 'apiusername') and password == BMConfigParser().get('bitmessagesettings', 'apipassword')
        else:
            logger.warning(
                'Authentication failed because header lacks'
                ' Authentication field')
            time.sleep(2)

        if isValid is False:
            self.send_error(401, b'Authetication failed')

        return isValid


class StoppableXMLRPCServer(CustomThreadingMixIn, SimpleXMLRPCServer, VerifyingRequestHandler, Services):

    def serve_forever(self):
        while state.shutdown == 0:
            try:
                self.rCondition.acquire()
                start_new_thread(self.handle_request, ())  # we do this async, because handle_request blocks!
                while not self.requests:
                    self.rCondition.wait(timeout=3.0)
                if self.requests:
                    self.requests -= 1
                self.rCondition.release()
            except KeyboardInterrupt:
                logger.warning('quit signaled. i am done.')
                break

        logger.info('API service down.')
        self.server_close()
        return

    def get_request(self):
        request, client_address = self.socket.accept()
        self.rCondition.acquire()
        self.requests += 1
        self.rCondition.notifyAll()
        self.rCondition.release()
        return (request, client_address)

    def __init__(self,  addr, logRequests=True, allow_none=False, encoding=None, allow_dotted_names = False, bind_and_activate=True, keyFile=DEFAULTKEYFILE, certFile=DEFAULTFILE):
        self.logRequests = logRequests
        self.allow_none = allow_none
        self.encoding = encoding
        self.allow_dotted_names = allow_dotted_names

        # This is one of several classes that constitute the API
        # This class was written by Vaibhav Bhatia.
        # Modified by Jonathan Warren (Atheros).
        # http://code.activestate.com/recipes/501148-xmlrpc-serverclient-which-does-cookie-handling-and/

        SimpleXMLRPCDispatcher.__init__(self, self.allow_none, self.encoding)

        self.funcs = {}
        self.register_introspection_functions()
        self.register_multicall_functions()

        self.requests = 0
        self.rCondition = threading.Condition()

        BaseServer.__init__(self, addr, VerifyingRequestHandler)
        # SocketServer.TCPServer.__init__(self, addr, VerifyingRequestHandler, bind_and_activate)

        # [Bug #1222790] If possible, set close-on-exec flag; if a
        # method spawns a subprocess, the subprocess shouldn't have
        # the listening socket open.
    #        if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
    #            flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
    #            flags |= fcntl.FD_CLOEXEC
    #            fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)

        # ssl socket stuff
    #        ctx = ssl.Context(ssl.SSLv23_METHOD)
    #        ctx.use_privatekey_file(keyFile)
    #        ctx.use_certificate_file(certFile)
    #        self.socket = ssl.Connection(ctx, socket.socket(self.address_family, self.socket_type))
        self.allow_reuse_address = True
        self.socket = socket.socket(self.address_family, self.socket_type)
        self.server_bind()
        self.server_activate()

        self.register_function(self.HandleListAddresses, name='listAddresses')
        self.register_function(self.HandleListAddressBookEntries, name='listAddressBookEntries')
        self.register_function(self.HandleAddAddressBookEntry, name='addAddressBookEntry')
        self.register_function(self.HandleDeleteAddressBookEntry, name='deleteAddressBookEntry')
        self.register_function(self.HandleCreateRandomAddress, name='createRandomAddress')
        self.register_function(self.HandleCreateDeterministicAddresses, name='createDeterministicAddresses')
        self.register_function(self.HandleGetDeterministicAddress, name='getDeterministicAddress')
        self.register_function(self.HandleCreateChan, name='createChan')
        self.register_function(self.HandleJoinChan, name='joinChan')
        self.register_function(self.HandleLeaveChan, name='leaveChan')
        self.register_function(self.HandleDeleteAddress, name='deleteAddress')
        self.register_function(self.HandleGetAllInboxMessages, name='getAllInboxMessages')
        self.register_function(self.HandleGetAllInboxMessageIds, name='getAllInboxMessageIds')
        self.register_function(self.HandleGetInboxMessageById, name='getInboxMessageById')
        self.register_function(self.HandleGetAllSentMessages, name='getAllSentMessages')
        self.register_function(self.HandleGetAllSentMessageIds, name='getAllSentMessageIds')
        self.register_function(self.HandleInboxMessagesByReceiver, name='getInboxMessagesByReceiver')
        self.register_function(self.HandleGetSentMessageById, name='getSentMessageById')
        self.register_function(self.HandleGetSentMessagesBySender, name='getSentMessagesBySender')
        self.register_function(self.HandleGetSentMessagesByAckData, name='getSentMessageByAckData')
        self.register_function(self.HandleTrashMessage, name='trashMessage')
        self.register_function(self.HandleTrashInboxMessage, name='trashInboxMessage')
        self.register_function(self.HandleTrashSentMessage, name='trashSentMessage')
        self.register_function(self.HandleSendMessage, name='sendMessage')
        self.register_function(self.HandleSendBroadcast, name='sendBroadcast')
        self.register_function(self.HandleGetStatus, name='getStatus')
        self.register_function(self.HandleAddSubscription, name='addSubscription')
        self.register_function(self.HandleDeleteSubscription, name='deleteSubscription')
        self.register_function(self.HandleListSubscriptions, name='listSubscriptions')
        self.register_function(self.HandleDisseminatePreEncryptedMsg, name='disseminatePreEncryptedMsg')
        self.register_function(self.HandleTrashSentMessageByAckDAta, name='trashSentMessageByAckData')
        self.register_function(self.HandleDissimatePubKey, name='disseminatePubkey')
        self.register_function(self.HandleGetMessageDataByDestinationHash, name='getMessageDataByDestinationHash')
        self.register_function(self.HandleClientStatus, name='clientStatus')
        self.register_function(self.HandleDecodeAddress, name='decodeAddress')
        self.register_function(self.HandleHelloWorld, name='helloWorld')
        self.register_function(self.HandleAdd, name='add')
        self.register_function(self.HandleStatusBar, name='statusBar')
        self.register_function(self.HandleDeleteAndVacuum, name='deleteAndVacuum')
        self.register_function(self.HandleShutdown, name='shutdown')

        # should be removed eventually
        self.register_function(self.HandleListAddressBookEntries, name='listAddressbook')
        self.register_function(self.HandleAddAddressBookEntry, name='addAddressbook')
        self.register_function(self.HandleDeleteAddressBookEntry, name='deleteAddressbook')
        self.register_function(self.HandleGetAllInboxMessageIds, name='getAllInboxMessageIDs')
        self.register_function(self.HandleGetInboxMessageById, name='getInboxMessageByID')
        self.register_function(self.HandleGetAllSentMessageIds, name='getAllSentMessageIDs')
        self.register_function(self.HandleGetSentMessageById, name='getSentMessageByID')
        self.register_function(self.HandleGetSentMessagesBySender, name='getSentMessagesByAddress')
        self.register_function(self.HandleInboxMessagesByReceiver, name='getInboxMessagesByAddress')
        self.register_function(self.HandleGetMessageDataByDestinationHash, name='getMessageDataByDestinationTag')

    def _dispatch(self, method, params):

        try:
            # _dispatch method handle skiped
            func = self.funcs.get(method, None)
            if func is not None:
                if method[:7] == 'system.':
                    return func(*params)
                else:
                    return func(params)
            else:
                raise APIError(20, 'Invalid method: %s' % method)
        except APIError as e:
            pass
        except varintDecodeError as e:
            logger.error(e)
            e = APIError(26, "Data contains a malformed varint. Some details: %s" % e)
        except Exception as e:
            logger.exception(e)
            e = APIError(21, "Unexpected API Failure - %s" % e)

        return str(e)


# This thread, of which there is only one, runs the API.
class singleAPI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, name="singleAPI")
        self.port = BMConfigParser().safeGetInt('bitmessagesettings', 'apiport')
        self.interface = BMConfigParser().get('bitmessagesettings', 'apiinterface')
        self.serve = None
        self.initStop()

    def initStop(self):
        self.stop = threading.Event()
        self._stopped = False

    def stopThread(self):
        self._stopped = True
        self.stop.set()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.interface, self.port))
            s.shutdown(socket.SHUT_RDWR)
            s.close()
        except Exception as err:
            logger.exception(err)

    def run(self):
#        try:
#            from errno import WSAEADDRINUSE
#        except (ImportError, AttributeError):
#            errno.WSAEADDRINUSE = errno.EADDRINUSE
        try:
            se = StoppableXMLRPCServer((self.interface, self.port), True, True)
            sa = se.socket.getsockname()
            logger.warn('Serving API on %s, port %d' % (sa[0], sa[1]))
            self.serve = se
            se.serve_forever()
        except socket.error as err:
            #if e.errno in (errno.EADDRINUSE, errno.WSAEADDRINUSE):
            logger.exception('interface not useable: [%s:%d]' % (self.interface, self.port))
        except Exception as err:
            logger.exception(err)

    def test(self):
        try:
            import xmlrpclib
        except ImportError:
            import xmlrpc.client as xmlrpclib

        emailid = BMConfigParser().get('bitmessagesettings', 'apiusername')
        password = BMConfigParser().get('bitmessagesettings', 'apipassword')
        uri = 'http://%s:%s@%s:%d/' % (emailid, password, self.interface, self.port)

        ret = False
        try:
            api = xmlrpclib.ServerProxy(uri)
            print('api: %s' % api)
            response = api.system.listMethods()
            if response:
                print('Methods = %s' % response)
            print('MultiCall...')
            multi = xmlrpclib.MultiCall(api)
            multi.add(1, 2)
            multi.add(2, 3)
            for response in multi():
                print(response)
            ret = True
        except TypeError as err:  # unsupported XML-RPC protocol
            print('XML-RPC not initialed correctly. {%s}\n' % str(err))
        except xmlrpclib.Fault as err:
            print('API returns Fault error. {%s}\n' % str(err))
        except Exception as err:  # /httplib.BadStatusLine: connection close immediatly
            print('Unexpected error. {%s}\n' % sys.exc_info()[0])

        if ret is False:
            logger.exception(err)

        return ret


class TestAPIThread(object):

    def start(self):
        success = False
        print('XMLRPC API daemon...')
        singleAPIThread = singleAPI()
        singleAPIThread.daemon = True
        singleAPIThread.start()
        time.sleep(3)
        if singleAPIThread.serve:
            print('XMLRPC Testing...')
            success = singleAPIThread.test()
            singleAPIThread.stopThread()
        else:
            print('XMLRPC API daemon failed!')

        sys.exit(success is False)


def main():
    mainprogram = TestAPIThread()
    mainprogram.start()


if __name__ == "__main__":
    main()
