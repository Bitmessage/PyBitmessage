# Copyright (c) 2012-2014 Jonathan Warren
# Copyright (c) 2012-2014 The Bitmessage developers

comment= """
This is not what you run to run the Bitmessage API. Instead, enable the API
( https://bitmessage.org/wiki/API ) and optionally enable daemon mode
( https://bitmessage.org/wiki/Daemon ) then run bitmessagemain.py. 
"""

if __name__ == "__main__":
    print comment
    import sys
    sys.exit(0)

from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import json
import re

import shared
import time

import hashlib

from helper_api import _handle_request
from addresses import decodeAddress,addBMIfNotPresent,decodeVarint,calculateInventoryHash,varintDecodeError
from pyelliptic.openssl import OpenSSL
from struct import pack

# Classes
from debug import logger

class APIError(Exception):
    def __init__(self, error_number, error_message):
        super(APIError, self).__init__()
        self.error_number = error_number
        self.error_message = error_message
    def __str__(self):
        return "API Error %04i: %s" % (self.error_number, self.error_message)

# This is one of several classes that constitute the API
# This class was written by Vaibhav Bhatia. Modified by Jonathan Warren (Atheros).
# http://code.activestate.com/recipes/501148-xmlrpc-serverclient-which-does-cookie-handling-and/
class MySimpleXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):

    def do_POST(self):
        # Handles the HTTP POST request.
        # Attempts to interpret all HTTP POST requests as XML-RPC calls,
        # which are forwarded to the server's _dispatch method for handling.

        # Note: this method is the same as in SimpleXMLRPCRequestHandler,
        # just hacked to handle cookies

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
                L.append(self.rfile.read(chunk_size))
                size_remaining -= len(L[-1])
            data = ''.join(L)

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.

            response = self.server._marshaled_dispatch(
                data, getattr(self, '_dispatch', None)
            )
        except:  # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "application/json")
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

    def APIAuthenticateClient(self):
        if 'Authorization' in self.headers:
            # handle Basic authentication
            (enctype, encstr) = self.headers.get('Authorization').split()
            (emailid, password) = encstr.decode('base64').split(':')
            if emailid == shared.config.get('bitmessagesettings', 'apiusername') and password == shared.config.get('bitmessagesettings', 'apipassword'):
                return True
            else:
                return False
        else:
            logger.warn('Authentication failed because header lacks Authentication field')
            time.sleep(2)
            return False

        return False

    def _decode(self, text, decode_type):
        try:
            return text.decode(decode_type)
        except Exception as e:
            raise APIError(22, "Decode error - " + str(e) + ". Had trouble while decoding string: " + repr(text))

    def _verifyAddress(self, address):
        status, addressVersionNumber, streamNumber, ripe = decodeAddress(address)
        if status != 'success':
            logger.warn('API Error 0007: Could not decode address %s. Status: %s.', address, status)

            if status == 'checksumfailed':
                raise APIError(8, 'Checksum failed for address: ' + address)
            if status == 'invalidcharacters':
                raise APIError(9, 'Invalid characters in address: ' + address)
            if status == 'versiontoohigh':
                raise APIError(10, 'Address version number too high (or zero) in address: ' + address)
            if status == 'varintmalformed':
                raise APIError(26, 'Malformed varint in address: ' + address)
            raise APIError(7, 'Could not decode address: ' + address + ' : ' + status)
        if addressVersionNumber < 2 or addressVersionNumber > 4:
            raise APIError(11, 'The address version number currently must be 2, 3 or 4. Others aren\'t supported. Check the address.')
        if streamNumber != 1:
            raise APIError(12, 'The stream number must be 1. Others aren\'t supported. Check the address.')

        return (status, addressVersionNumber, streamNumber, ripe)

    def _dispatch( self, method, params ):
        self.cookies = []

        validuser = self.APIAuthenticateClient()
        if not validuser:
            time.sleep(2)
            return "RPC Username or password incorrect or HTTP header lacks authentication at all."

        self.apiDir = _handle_request

        if method in dir( self.apiDir ):
            logger.warn( 'Found "{}" in API'.format( method ) )
            try:
                statusCode, data = object.__getattribute__( _handle_request, method )( self, *params )
            except Exception as e:
                logger.exception(e)
                statusCode = 500
                data = "500"
        else:
            statusCode = 404
            data = "Method not found"

        if statusCode != 200:
            data = { 'error': data }

        response = {
            'data': data,
            'status': statusCode,
            'method': method
        }
        return json.dumps( response )
