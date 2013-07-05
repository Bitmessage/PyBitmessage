# Copyright (C) 2013 by Daniel Kraft <d@domob.eu>
# This file is part of the Bitmessage project.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import base64
import json
import socket

# Error thrown when the RPC call returns an error.
class RPCError (Exception):
    error = None

    def __init__ (self, data):
        self.error = data

# This class handles the Namecoin identity integration.
class namecoinConnection (object):
    user = None
    password = None
    host = None
    port = None
    bufsize = 4096
    queryid = 1

    def __init__ (self):
        self.user = "daniel"
        self.password = "password"
        self.host = "localhost"
        self.port = "8336"

    # Query for the bitmessage address corresponding to the given identity
    # string.  If it doesn't contain a slash, id/ is prepended.  We return
    # the result as (Error, Address) pair, where the Error is an error
    # message to display or None in case of success.
    def query (self, string):
        slashPos = string.find ("/")
        if slashPos < 0:
            string = "id/" + string

        try:
            res = self.callRPC ("name_show", [string])
        except RPCError as exc:
            if exc.error["code"] == -4:
                return ("The name '%s' was not found." % string, None)
            else:
                return ("The namecoin query failed (%s)" % exc.error["message"],
                        None)
        except Exception as exc:
            print "Namecoin query exception: %s" % str (exc)
            return ("The namecoin query failed.", None)

        try:
            val = json.loads (res["value"])
        except:
            return ("The name '%s' has no valid JSON data." % string, None)

        if "bitmessage" in val:
            return (None, val["bitmessage"])

        return ("The name '%s' has no associated Bitmessage address." % string,
                None)

    # Helper routine that actually performs an JSON RPC call.
    def callRPC (self, method, params):
        data = {"method": method, "params": params, "id": self.queryid}
        resp = self.queryHTTP (json.dumps (data))
        val = json.loads (resp)

        if val["id"] != self.queryid:
            raise Exception ("ID mismatch in JSON RPC answer.")
        self.queryid = self.queryid + 1

        if val["error"] is not None:
            raise RPCError (val["error"])

        return val["result"]

    # Query the server via HTTP.
    def queryHTTP (self, data):
        header = "POST / HTTP/1.1\n"
        header += "User-Agent: bitmessage\n"
        header += "Host: %s\n" % self.host
        header += "Content-Type: application/json\n"
        header += "Content-Length: %d\n" % len (data)
        header += "Accept: application/json\n"
        authstr = "%s:%s" % (self.user, self.password)
        header += "Authorization: Basic %s\n" % base64.b64encode (authstr)

        resp = self.queryServer ("%s\n%s" % (header, data))
        lines = resp.split ("\r\n")
        result = None
        body = False
        for line in lines:
            if line == "" and not body:
                body = True
            elif body:
                if result is not None:
                    raise Exception ("Expected a single line in HTTP response.")
                result = line

        return result

    # Helper routine sending data to the RPC server and returning the result.
    def queryServer (self, data):
        try:
            s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect ((self.host, int (self.port)))
            s.sendall (data)
            result = ""

            while True:
                tmp = s.recv (self.bufsize)
                if not tmp:
                  break
                result += tmp

            s.close ()

            return result

        except socket.error as exc:
            raise Exception ("Socket error in RPC connection: %s" % str (exc))
