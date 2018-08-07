# XML-RPC Client with Pybitmessage.
# This module adapt the ``xmlrpc.client`` module of the standard library to
# work with Pybitmessage.

import sys
import base64

try:
    import httplib
    import xmlrpclib
    from urlparse import urlparse
    from urllib import unquote as unquote_to_bytes
    from urllib import quote
except ImportError:
    import http.client as httplib
    import xmlrpc.client as xmlrpclib
    from urllib.parse import urlparse, unquote_to_bytes, quote

import ssl
from socket import error as SOCKETError
import json
import logging

logger = logging.getLogger('default')
# logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
# logger.getEffectiveLevel()
# logger.setLevel(loggin.INFO)
try:
    logger.info('- Try to import "SocksiPy" module for proxied...')
    from bmsxmlrpc.socks import ProxyError, ProxyConnectionError, GeneralProxyError, SOCKS5AuthError, SOCKS5Error, SOCKS4Error, HTTPError
    import bmsxmlrpc.socks as socks
    if hasattr(socks, 'setdefaultproxy'):
        socks_allow = True
        logger.info('     "SocksiPy" module imported.')
    else:
        logger.warn('     Not the correct "SocksiPy" module imported.')

except ImportError as err:
    logger.warn('     Depends check failed, "SOCKS" type proxy disabled. {%s}' % str(err))


    class ProxyError(Exception):
        pass


    class ProxyConnectionError(ProxyError):
        pass


    class GeneralProxyError(ProxyError):
        pass


    class SOCKS5AuthError(ProxyError):
        pass


    class SOCKS5Error(ProxyError):
        pass


    class SOCKS4Error(ProxyError):
        pass


    class HTTPError(ProxyError):
        pass


__all__ = [
        'ServerProxy', 'MultiCall', 'safeBMAPI',
        # BMS API call returns.
        'APICallSafeRet'
        # Parse Error code from BMS API response.
        'getAPIErrorCode',
        # hexlify or base64 (de)encoding.
        'BMS_decode', 'BMS_encode', 'DecodeError',
        # error codes defines for APICallSafeRet
        'SAFEAPI_ERRORS',
        ]


SAFEAPI_ERRORS = {
    0: "Response ok.",
    1: "Not prepared for calling API methods.",
    2: "Authorization Error",
    3: "Server returns unexpected data.",
    97: "Unexpected type in MultiCall result.",
    98: "MultiCall error: unexpected MultiCall method.",
#    errono: "API Error",  # details see BMS API Error codes
#    faltCode: "xmlrpc Fault error",
    -1: "XML-RPC not initialed correctly(+ProtocolError/HTTP500).",
    -3: "Connection error(+xmlrpc lib error).",
    -99: "Unexpected error(+ConnectionRefusedError on python3)."
}


def __repr__(self):
    return '<%s.%s object at %s>' % (
        self.__class__.__module__,
        self.__class__.__name__,
        hex(id(self))
        )


class APICallSafeRet(object):
    # safeBMAPI return object

    def __init__(self, error=-100, result='INITIAL_RESULT', errormsg='INITIAL_ERRORMSG'):
        self.error = error
        self.result = result
        self.errormsg = errormsg


def getAPIErrorCode(response):
    # Get API error code

    if "API Error" in response:
        # if we got an API error return the number by getting the number
        # after the second space and removing the trailing colon
        return int(response.split()[2][:-1])


class DecodeError(Exception):
    # base64 or hexlify decode error

    def __init__(self, err):
        Exception.__init__(self, err)
        self.err = err

    def __str__(self):
        return str(self.err)


def BMS_decode(text, decode_type):
    # base64 or hexlify decode
    # decode_type: 'hex' or 'base64'

    try:
        if decode_type == 'hex':  # for messageId/ackData/payload
            return unhexlify(text)
        elif decode_type == 'base64':  # for label/passphrase/ripe/subject/message
            return base64.b64decode(text)
    except Exception as err:  # UnicodeEncodeError/
        raise DecodeError(err)


def BMS_encode(text, encode_type):
    # base64 or hexlify encode
    # decode_type: 'hex' or 'base64'

    if encode_type == 'hex':
        return hexlify(text)
    elif encode_type == 'base64':  # for label/passphrase/ripe/subject/message
        return base64.b64encode(text)


# proxied start
# original https://github.com/benhengx/xmlrpclibex
# add basic auth support for top level host while none/HTTP proxied


def init_socks(proxy, timeout):
    # init a `SocksiPy` socks proxy socket.

    map_to_type = {
        'SOCKS4':   socks.PROXY_TYPE_SOCKS4,
        'SOCKS5':   socks.PROXY_TYPE_SOCKS5,
        'HTTP': socks.PROXY_TYPE_HTTP
    }
    address_family = socket.AF_INET
    ssock = socks.socksocket(address_family, socket.SOCK_STREAM)
    ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if isinstance(timeout, (int, float)):
        ssock.settimeout(timeout)
    proxytype = map_to_type[proxy['proxy_type']]
    rdns = proxy['proxy_remotedns']
    addr, port = proxy['proxy_path'].split(':', 1)
    port = int(port)
    username = proxy['proxy_username']
    password = proxy['proxy_password']
    isauth = username and password
    if isauth is True:
        ssock.setproxy(proxytype, addr, port, username, password, rdns)
        socks.setdefaultproxy(proxytype, addr, port, username, password, rdns)
    else:
        ssock.setproxy(proxytype, addr, port, rdns)
        socks.setdefaultproxy(proxytype, addr, port, rdns)

    socket.socket = socks.socksocket
    return ssock


class SocksProxiedHTTPConnection(httplib.HTTPConnection):
    # Proxy the http connection through a socks proxy.

    def init_socks(self, proxy):
        self.ssock = init_socks(proxy, self.timeout)

    def connect(self):
        self.ssock.connect((self.host, self.port))
        self.sock = self.ssock


class SocksProxiedHTTPSConnection(httplib.HTTPSConnection):
    # Proxy the https connection through a socks proxy.

    def init_socks(self, proxy):
        self.ssock = init_socks(proxy, self.timeout)

    def connect(self):
        self.ssock.connect((self.host, self.port))
        self.sock = ssl.wrap_socket(self.ssock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_TLSv1)  # SSLv3

    def close(self):
        httplib.HTTPSConnection.close(self)

        if self.ssock:
            self.ssock.close()
            self.ssock = None


class TransportWithTo(xmlrpclib.Transport):
    # Transport support timeout

    cls_http_conn = httplib.HTTPConnection
    cls_https_conn = httplib.HTTPSConnection

    def __init__(self, use_datetime=0, is_https=False, timeout=None):
        xmlrpclib.Transport.__init__(self, use_datetime)

        self.is_https = is_https
        if timeout is None:
            timeout = socket._GLOBAL_DEFAULT_TIMEOUT
        self.timeout = timeout

    def make_connection(self, host):
        self.realhost = host
        if self._connection and host == self._connection[0]:
            return self._connection[1]

        # create a HTTP/HTTPS connection object from a host descriptor
        # host may be a string, or a (host, x509-dict) tuple
        # no basic auth head returns here
        chost, self._extra_headers, x509 = self.get_host_info(host)

        # store the host argument along with the connection object
        if self.is_https:  # xmlrpclib.SafeTransport + timeout
            self._connection = host, self.cls_https_conn(chost, None, timeout=self.timeout, **(x509 or {}))
        else:    # xmlrpclib.Transport + timeout
            self._connection = host, self.cls_http_conn(chost, timeout=self.timeout)
        return self._connection[1]

#    def send_request(self, connection, handler, request_body):
#        connection.putrequest('POST', '%s://%s' % (self.realhost, handler))

#    def send_host(self, connection, host):
#        connection.putheader('Host', self.realhost)

#    def send_user_agent(self, connection):
#        connection.putheader("User-Agent", self.send_user_agent)


class ProxiedTransportWithTo(TransportWithTo):
    # Transport supports timeout and http proxy

    def __init__(self, proxy, use_datetime=0, timeout=None, api_cred=None):
        TransportWithTo.__init__(self, use_datetime, False, timeout)

        self.api_cred = api_cred
        self.proxy_path = proxy['proxy_path']
        if proxy['proxy_username'] and proxy['proxy_password']:
            self.proxy_cred = '%s:%s' % (quote(proxy['proxy_username']), quote(proxy['proxy_password']))
        else:
            self.proxy_cred = None

    def basic_str(quote_auth):
        auth = unquote_to_bytes(quote_auth)
        auth = BMS_encode(auth, 'base64').decode("utf-8")
        auth = "".join(auth.split())  # get rid of whitespace
        return auth

    def request(self, host, handler, request_body, verbose=False):
        realhandler = 'HTTP://%s%s' % (host, handler)
        return TransportWithTo.request(self, host, realhandler, request_body, verbose)

    def make_connection(self, host):
        return TransportWithTo.make_connection(self, self.proxy_path)

    def send_content(self, connection, request_body):
        if self.proxy_cred:
            connection.putheader('Proxy-Authorization', 'Basic ' + self.basic_str(self.proxy_cred))
        if self.api_cred:
            connection.putheader('Authorization', 'Basic ' + self.basic_str(self.api_cred))
        return TransportWithTo.send_content(self, connection, request_body)


class SocksProxiedTransportWithTo(TransportWithTo):
    # Transport supports timeout and socks SOCKS4/SOCKS5 and http connect tunnel

    cls_http_conn = SocksProxiedHTTPConnection
    cls_https_conn = SocksProxiedHTTPSConnection

    def __init__(self, proxy, use_datetime=0, is_https=False, timeout=None):
        TransportWithTo.__init__(self, use_datetime, is_https, timeout)
        self.proxy = proxy

    def make_connection(self, host):
        conn = TransportWithTo.make_connection(self, host)
        conn.init_socks(self.proxy)
        return conn


class _Method(object):
    # copied from xmlrpclib
    # some magic to bind an XML-RPC method to an RPC server.
    # supports "nested" methods (e.g. examples.getStateName)

    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __getattr__(self, name):
        return _Method(self.__send, "%s.%s" % (self.__name, name))

    def __call__(self, *args):
        ret = self.__send(self.__name, args)
        return ret


class ServerProxy(xmlrpclib.ServerProxy):
    # ``xmlrpc.ServerProxy`` subclass for PyBitmessage
    # New added keyword arguments
    # timeout: seconds waiting for the socket
    # proxy: a dict specify the proxy settings, it supports the following fields:
    #    proxy_path: the address of the proxy server. default: 127.0.0.1:1080
    #    proxy_username: username to authenticate to the server. default None
    #    proxy_password: password to authenticate to the server, only relevant when
    #              username is set. default None
    #    proxy_type: string, 'SOCKS4', 'SOCKS5', 'HTTP' (HTTP connect tunnel), only
    #                relevant when is_socks is True. default 'SOCKS5'

    def __init__(self, uri, transport=None, encoding='utf-8', verbose=False,
                 allow_none=False, use_datetime=False, timeout=30, proxy=None):

        scheme, netloc, path = urlparse(uri)[:3]
        api_username = urlparse(uri).username
        api_password = urlparse(uri).password
        api_cred = None
        self.uri = uri
        if api_username and api_password:
            api_cred = '%s:%s' % (quote(api_username), quote(api_password))
            netloc = netloc.split('@')[1]

        if transport is None and proxy:
            is_https = scheme == 'https'

            if proxy.get('proxy_type', 'none') == 'none':
                transport = TransportWithTo(use_datetime, is_https, timeout)
            else:
                timeout = proxy.get('timeout', timeout)  # overide default timeout from proxy dict
                is_socks = 'SOCKS' in proxy['proxy_type']

                if is_https and not is_socks:  # set default HTTP type for https uri
                    # https must be tunnelled through http connect
                    is_socks = True
                    proxy['proxy_type'] = 'HTTP'

                if not is_socks:  # http proxy
                    self.uri = '%s://%s%s' % (scheme, netloc, path)
                    transport = ProxiedTransportWithTo(proxy,
                                                       use_datetime,
                                                       timeout,
                                                       api_cred)
                else:  # http connect and socksx
                    transport = SocksProxiedTransportWithTo(proxy,
                                                            use_datetime,
                                                            is_https,
                                                            timeout)

        xmlrpclib.ServerProxy.__init__(self, self.uri, transport=transport, encoding=encoding, verbose=verbose, allow_none=allow_none, use_datetime=use_datetime, context=None)

    def __request(self, methodname, params):
        # call a method on the remote server

        response = ''
        try:
            try:
                request = xmlrpclib.dumps(params, methodname, allow_none=self.__allow_none,  encoding=self.__encoding).encode(self.__encoding)

                response = self.__transport.request(
                    self.__host,
                    self.__handler,
                    request,
                    verbose=self.__verbose
                    )
                if len(response) == 1:
                    response = response[0]
            except Exception as err:
                raise RPCErrorWithRet(response, err)
        except RPCErrorWithRet as err:
            return APICallSafeRet(err.error, err.ret, err.errormsg)

        ret = APICallSafeRet()
        parse_singlecall_result(ret, methodname, response)
        return ret

    def __getattr__(self, name):
        return _Method(self.__request, name)
# proxied end


class RPCErrorWithRet(Exception):
    # Catching all exceptions on xmlrpc method calling.

    def __init__(self, ret, err):
        Exception.__init__(self, err)
        self.ret = ret
        self.err = err

        if isinstance(err, (TypeError, xmlrpclib.ProtocolError)):  # unsupported XML-RPC protocol/ not callable
            self.error = -1
            self.errormsg = '\n     XML-RPC not initialed correctly. {%s}\n' % str(self)
            logger.critical(self.errormsg, exc_info=True)
        elif isinstance(err, xmlrpclib.Fault):
            self.error = err.faultCode
            self.result = err.faultString
            self.errormsg = '\n     API method Fault error. {%s}\n' % str(self)
            logger.debug(self.errormsg)
        elif isinstance(err, (ProxyError, ProxyConnectionError, GeneralProxyError, SOCKS5AuthError, SOCKS5Error, SOCKS4Error, HTTPError, SOCKETError, xmlrpclib.Error)):
            self.error = -3
            self.errormsg = '\n     Connection error. {%s}\n' % str(self)
            logger.debug(self.errormsg, exc_info=True)
        else:  # /httplib.BadStatusLine/ConnectionRefusedError111/ConnectionError
            self.error = -99
            self.errormsg = '\n     Unexpected error: {%s}\n' % str(self)
            logger.exception(self.errormsg, exc_info=True)

    def __str__(self):
        return str(self.err)


class notForCalling(object):
    # A replacement return for remote api method calls on XML-RPC error

    def __request(self, methodname, params):
        ret = '     Not prepared for calling API methods. %s%s' % (methodname, str(params))
        response = APICallSafeRet(1, '', ret)
        return response

    def __getattr__(self, name):
        return _Method(self.__request, name)


def safeBMAPI(uri, verbose=False, allow_none=True, use_datetime=True, timeout=30, proxy=None):
    # pre-check XML-RPC errors for init `ServerProxy`

    proxied = 'non-proxied'
    ret = None
    if proxy:
        proxied = proxy['proxy_type'] + ' | ' + proxy['proxy_path']

    try:
        xmlrpc = ServerProxy(uri, verbose=verbose, allow_none=allow_none, use_datetime=use_datetime, timeout=timeout, proxy=proxy)
        logger.info('\n     XML-RPC initialed on: "%s" (%s)' % (uri, proxied))
        ret = xmlrpc
    except Exception as err:  # IOError, unsupported XML-RPC protocol/
        logger.exception('\n     XML-RPC initial failed on: "%s" - {%s}' % (uri, err), exc_info=True)
        ret = notForCalling()

    return ret


def parse_singlecall_result(ret, method_name, response):
    # pre-checking for PyBitmessage API returns

    ret.error = 0
    if isinstance(response, str) and ("API Error" in response or 'RPC ' in response):  # API Error, Authorization Error
        ret.error = 2
        if "API Error" in response:
            ret.error = getAPIErrorCode(response)
            if ret.error in [20, 21]:  # programing error, Invalid method/Unexpected API Failure
                logger.critical('\n     Update your API server for method. <%s>' % method_name)
        ret.errormsg = '     ' + response + '\n'
        return

    if method_name in [
            'add',
            'helloWorld',
            'statusBar',
            'addSubscription',
            'deleteSubscription',
            'createChan',
            'joinChan',
            'leaveChan',
            'sendMessage',
            'sendBroadcast',
            'getStatus',
            'trashMessage',
            'trashInboxMessage',
            'trashSentMessageByAckData',
            'trashSentMessage',
            'addAddressBK',
            'addAddressbook',
            'delAddressBK',
            'deleteAddressbook',
            'createRandomAddress',
            'getDeterministicAddress',
            'deleteAddress',
            'disseminatePreEncryptedMsg',
            'disseminatePubkey',
            'deleteAndVacuum',
            'shutdown',
            ]:
        ret.result = response
        return

    try:
        if method_name in [
                'getAllInboxMessageIds',
                'getAllInboxMessageIDs',
                ]:
            ret.result = json.loads(response)['inboxMessageIds']
        elif method_name in [
                'getInboxMessageById',
                'getInboxMessageByID',
                ]:
            ret.result = json.loads(response)['inboxMessage']
        elif method_name in [
                'GetAllInboxMessages',
                'getInboxMessagesByReceiver',
                'getInboxMessagesByAddress',
                ]:
            ret.result = json.loads(response)['inboxMessages']
        elif method_name in [
                'getAllSentMessageIds',
                'getAllSentMessageIDs',
                ]:
            ret.result = json.loads(response)['sentMessageIds']
        elif method_name in [
                'getAllSentMessages',
                'getSentMessagesByAddress',
                'getSentMessagesBySender',
                'getSentMessageByAckData',
                ]:
            ret.result = json.loads(response)['sentMessages']
        elif method_name in [
                'getSentMessageById',
                'getSentMessageByID',
                ]:
            ret.result = json.loads(response)['sentMessage']
        elif method_name in [
                'listAddressBookEntries',
                'listAddressbook',
                'listAddresses',
                'createDeterministicAddresses',
                ]:
            ret.result = json.loads(response)['addresses']
        elif method_name in [
                'listSubscriptions',
                ]:
            ret.result = json.loads(response)['subscriptions']
        elif method_name in [
                'decodeAddress',
                'clientStatus',
                'getMessageDataByDestinationHash',
                'getMessageDataByDestinationTag',
                ]:
            ret.result = json.loads(response)
        else:  # introspection_functions
            if isinstance(response, (list, str)):  # multicall results in list
                ret.result = response
            else:  # not used yet, maybe safe for `APIError` type?
                ret.result = json.loads(response)

    except (ValueError, KeyError, TypeError) as err:  # json.loads error
        ret.err = err
        ret.error = 3
        ret.result = json.loads(response) if isinstance(err, KeyError) else response
        ret.errormsg = '\n     Server returns unexpected data, maybe a network problem there? {%s}\n%s\n' % (str(err), ret.result)


def parse_multicall_result(ret, method_name, item):
    # parse signle api method return in multi call style
    # multicall methods limited to list

    ret.error = 0
    if isinstance(item, dict) and item.get('faultCode', None):  # Fault Error
        ret.error = item['faultCode']  # -2
        ret.errormsg = item['faultString']
        logger.warn('got Fault error in multicall results.')
        return

    if not isinstance(item, list):
        ret.error = 97
        ret.result = item
        ret.errormsg = "\n     unexpected type in multicall result.\n"
        return

    response = item[0]
    if method_name in [
            'trashInboxMessage',
            'getStatus',
            'add',
            ]:
        ret.result = response
        return

    try:
        if method_name in [
                'getInboxMessageById',
                ]:
            ret.result = json.loads(response)['inboxMessage']
        elif method_name in [
                'getAllSentMessageIds',  # alter get outbox msg length
                ]:
            result = json.loads(response)['sentMessageIds']
            ret.result = {'OutboxMessages': len(result)}
        elif method_name in [
                'getAllInboxMessageIds',  # alter get inbox msg length
                ]:
            result = json.loads(response)['inboxMessageIds']
            ret.result = {'InboxMessages': len(result)}
        elif method_name in [
                'listAddressBookEntries',
                'listAddresses',
                ]:
            results = json.loads(response)['addresses']
            ret.result = []
            for result in results:
                if method_name == 'listAddressBookEntries':
                    result['label'] = BMS_decode(result['label'], 'base64').decode(encoding='utf-8')
                ret.result.append(result)
        elif method_name in [
                'clientStatus',
                ]:
            ret.result = json.loads(response)
        else:
            ret.error = 98
            ret.result = response
            ret.errormsg = '\n     MultiCall error: unexpected multicall method. <%s>\n' % method_name
    except (ValueError, KeyError, TypeError) as err:  # json.loads error
        ret.err = err
        ret.error = 3
        ret.result = json.loads(response) if isinstance(err, KeyError) else response
        ret.errormsg = '\n     MultiCall returns unexpected data, maybe a network problem there? {%s}\n%s\n' % (str(err), ret.result)


class MultiCallIterator(object):
    # Iterates over the results of a multicall. Exceptions are
    # raised in response to xmlrpc faults.

    def __init__(self, call_list, results):
        self.call_list = call_list
        self.results = results

    def __getitem__(self, i):
        if not isinstance(self.results.result, list):  # force to multicall type safe returns on not type of multicall results
            if i > 0:
                raise StopIteration
            return self.results

        item = self.results.result[i]
        method_name = self.call_list[i]['methodName']
        _safe_ret = APICallSafeRet(0, '', '')
        parse_multicall_result(_safe_ret, method_name, item)
        return _safe_ret


class _MultiCallMethod(object):
    # some lesser magic to store calls made to a MultiCall object
    # for batch execution
    # multicall methods limited to the list

    def __init__(self, call_list, name):
        self.__call_list = call_list
        self.__name = name

    def __getattr__(self, name):
        return _MultiCallMethod(self.__call_list, "%s.%s" % (self.__name, name))

    def __call__(self, *args):
        if self.__name in [
                'trashInboxMessage',
                'getStatus',
                'add',
                'getInboxMessageById',
                'clientStatus',
                'listAddressBookEntries',
                'listAddresses',
                ]:
            self.__call_list.append((self.__name, args))
        elif self.__name in [
                'getAllSentMessageIds_alt',
                'getAllInboxMessageIds_alt',
                ]:
            self.__call_list.append((self.__name[:-4], args))
        else:
            logger.critical('\n     Skip an unexpected multicall method. <%s>' % self.__name)


class MultiCall(object):
    # overide xmlrpclib to parse multicall responses

    def __init__(self, server):
        self.__server = server
        self.__call_list = []

    def __repr__(self):
        return "<MultiCall at %x>" % id(self)

    __str__ = __repr__

    def __getattr__(self, name):
        return _MultiCallMethod(self.__call_list, name)

    def __call__(self):
        marshalled_list = []
        for name, args in self.__call_list:
            marshalled_list.append({'methodName': name, 'params': args})
        return MultiCallIterator(marshalled_list, self.__server.system.multicall(marshalled_list))

