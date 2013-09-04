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
import sys
import os

import shared
import tr # translate

configSection = "bitmessagesettings"

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
    nmctype = None
    bufsize = 4096
    queryid = 1

    # Initialise.  If options are given, take the connection settings from
    # them instead of loading from the configs.  This can be used to test
    # currently entered connection settings in the config dialog without
    # actually changing the values (yet).
    def __init__ (self, options = None):
        if options is None:
          self.nmctype = shared.config.get (configSection, "namecoinrpctype")
          self.host = shared.config.get (configSection, "namecoinrpchost")
          self.port = shared.config.get (configSection, "namecoinrpcport")
          self.user = shared.config.get (configSection, "namecoinrpcuser")
          self.password = shared.config.get (configSection,
                                             "namecoinrpcpassword")
        else:
          self.nmctype = options["type"]
          self.host = options["host"]
          self.port = options["port"]
          self.user = options["user"]
          self.password = options["password"]

        assert self.nmctype == "namecoind" or self.nmctype == "nmcontrol"

    # Query for the bitmessage address corresponding to the given identity
    # string.  If it doesn't contain a slash, id/ is prepended.  We return
    # the result as (Error, Address) pair, where the Error is an error
    # message to display or None in case of success.
    def query (self, string):
        slashPos = string.find ("/")
        if slashPos < 0:
            string = "id/" + string

        try:
            if self.nmctype == "namecoind":
                res = self.callRPC ("name_show", [string])
                res = res["value"]
            elif self.nmctype == "nmcontrol":
                res = self.callRPC ("data", ["getValue", string])
                res = res["reply"]
                if res == False:
                    raise RPCError ({"code": -4})
            else:
                assert False
        except RPCError as exc:
            if exc.error["code"] == -4:
                return (tr.translateText("MainWindow",'The name %1 was not found.').arg(unicode(string)), None)
            else:
                return (tr.translateText("MainWindow",'The namecoin query failed (%1)').arg(unicode(exc.error["message"])), None)
        except Exception as exc:
            print "Namecoin query exception: %s" % str (exc)
            return (tr.translateText("MainWindow",'The namecoin query failed.'), None)

        try:
            val = json.loads (res)
        except:
            return (tr.translateText("MainWindow",'The name %1 has no valid JSON data.').arg(unicode(string)), None)            

        if "bitmessage" in val:
            return (None, val["bitmessage"])
        return (tr.translateText("MainWindow",'The name %1 has no associated Bitmessage address.').arg(unicode(string)), None) 

    # Test the connection settings.  This routine tries to query a "getinfo"
    # command, and builds either an error message or a success message with
    # some info from it.
    def test (self):
        try:
            if self.nmctype == "namecoind":
                res = self.callRPC ("getinfo", [])
                vers = res["version"]
                
                v3 = vers % 100
                vers = vers / 100
                v2 = vers % 100
                vers = vers / 100
                v1 = vers
                if v3 == 0:
                  versStr = "0.%d.%d" % (v1, v2)
                else:
                  versStr = "0.%d.%d.%d" % (v1, v2, v3)
                return ('success',  tr.translateText("MainWindow",'Success!  Namecoind version %1 running.').arg(unicode(versStr)) )

            elif self.nmctype == "nmcontrol":
                res = self.callRPC ("data", ["status"])
                prefix = "Plugin data running"
                if ("reply" in res) and res["reply"][:len(prefix)] == prefix:
                    return ('success', tr.translateText("MainWindow",'Success!  NMControll is up and running.'))

                print "Unexpected nmcontrol reply: %s" % res
                return ('failed',  tr.translateText("MainWindow",'Couldn\'t understand NMControl.'))

            else:
                assert False

        except Exception as exc:
            print "Namecoin connection test: %s" % str (exc)
            return ('failed', "The connection to namecoin failed.")

    # Helper routine that actually performs an JSON RPC call.
    def callRPC (self, method, params):
        data = {"method": method, "params": params, "id": self.queryid}
        if self.nmctype == "namecoind":
          resp = self.queryHTTP (json.dumps (data))
        elif self.nmctype == "nmcontrol":
          resp = self.queryServer (json.dumps (data))
        else:
          assert False
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
            s.settimeout(3) 
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

# Look up the namecoin data folder.
# FIXME: Check whether this works on other platforms as well!
def lookupNamecoinFolder ():
    app = "namecoin"
    from os import path, environ
    if sys.platform == "darwin":
        if "HOME" in environ:
            dataFolder = path.join (os.environ["HOME"],
                                    "Library/Application Support/", app) + '/'
        else:
            print ("Could not find home folder, please report this message"
                    + " and your OS X version to the BitMessage Github.")
            sys.exit()

    elif "win32" in sys.platform or "win64" in sys.platform:
        dataFolder = path.join(environ["APPDATA"], app) + "\\"
    else:
        dataFolder = path.join(environ["HOME"], ".%s" % app) + "/"

    return dataFolder

# Ensure all namecoin options are set, by setting those to default values
# that aren't there.
def ensureNamecoinOptions ():
    if not shared.config.has_option (configSection, "namecoinrpctype"):
        shared.config.set (configSection, "namecoinrpctype", "namecoind")
    if not shared.config.has_option (configSection, "namecoinrpchost"):
        shared.config.set (configSection, "namecoinrpchost", "localhost")

    hasUser = shared.config.has_option (configSection, "namecoinrpcuser")
    hasPass = shared.config.has_option (configSection, "namecoinrpcpassword")
    hasPort = shared.config.has_option (configSection, "namecoinrpcport")

    # Try to read user/password from .namecoin configuration file.
    defaultUser = ""
    defaultPass = ""
    try:
        nmcFolder = lookupNamecoinFolder ()
        nmcConfig = nmcFolder + "namecoin.conf"
        nmc = open (nmcConfig, "r")

        while True:
            line = nmc.readline ()
            if line == "":
                break
            parts = line.split ("=")
            if len (parts) == 2:
                key = parts[0]
                val = parts[1].rstrip ()

                if key == "rpcuser" and not hasUser:
                    defaultUser = val
                if key == "rpcpassword" and not hasPass:
                    defaultPass = val
                if key == "rpcport":
                    shared.namecoinDefaultRpcPort = val
                
        nmc.close ()

    except Exception as exc:
        print "Could not read the Namecoin config file probably because you don't have Namecoin installed. That's ok; we don't really need it. Detailed error message: %s" % str (exc)

    # If still nothing found, set empty at least.
    if (not hasUser):
        shared.config.set (configSection, "namecoinrpcuser", defaultUser)
    if (not hasPass):
        shared.config.set (configSection, "namecoinrpcpassword", defaultPass)

    # Set default port now, possibly to found value.
    if (not hasPort):
        shared.config.set (configSection, "namecoinrpcport",
                           shared.namecoinDefaultRpcPort)
