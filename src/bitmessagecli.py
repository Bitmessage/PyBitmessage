#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines,global-statement,too-many-branches,too-many-statements,inconsistent-return-statements
# pylint: disable=too-many-nested-blocks,too-many-locals,protected-access,too-many-arguments,too-many-function-args
# pylint: disable=no-member
"""
Created by Adam Melton (.dok) referenceing https://bitmessage.org/wiki/API_Reference for API documentation
Distributed under the MIT/X11 software license. See http://www.opensource.org/licenses/mit-license.php.

This is an example of a daemon client for PyBitmessage 0.6.2, original by .dok (Version 0.3.1)
Modified by .pt (Version 0.4.0), for PyBitmessage 0.6.3

TODO: fix the following (currently ignored) violations:

"""

import argparse
import ConfigParser
import imghdr
import ntpath
import json
import sys
import os

import base64
import ssl
import socket

# python3 maybe
try:
    import httplib
    import xmlrpclib
    from urlparse import urlparse
    from urllib import unquote
except ImportError:
    import http.client as httplib
    import xmlrpc.client as xmlrpclib
    from urllib.parse import urlparse, unquote

import traceback

import time
import datetime
import inspect
import re
import subprocess

from collections import OrderedDict

usrPrompt = 0  # 0 = First Start, 1 = prompt, 2 = no prompt if the program is starting up
api = ''
knownAddresses = dict({'addresses': []})
cmdStr = 'getLabel'.lower()
# menu by this order
cmdTbl = OrderedDict()
cmdTbl['Command'] = 'Description'
cmdTbl['s1'] = '-'
cmdTbl['help'] = 'This help'
cmdTbl['daemon'] = 'Try to start PyBitmessage daemon locally'
cmdTbl['apiTest'] = 'Daemon API connection tests'
cmdTbl['status'] = 'Get the summary of running daemon'
cmdTbl['addInfo'] = 'Request detailed info to a address'
cmdTbl['bmSettings'] = 'PyBitmessage settings "keys.dat"'
cmdTbl['exit'] = 'Use anytime to return to main menu'
cmdTbl['quit'] = 'Quit this CLI'
cmdTbl['shutdown'] = 'Shutdown the connectable daemon via. API'
cmdTbl['s2'] = '-'
cmdTbl['listAddresses'] = 'List user\'s addresse(s) (Senders)'
cmdTbl['newAddress'] = 'Generate a new sender address'
cmdTbl['getAddress'] = 'Get determinist address from passphrase'
cmdTbl['s3'] = '-'
cmdTbl['listAddressBK'] = 'List the "Address Book" entry (Contacts)'
cmdTbl['addAddressBK'] = 'Add a address to the "Address Book"'
cmdTbl['delAddressBK'] = 'Delete a address from the "Address Book"'
cmdTbl['s4'] = '-'
cmdTbl['listsubscrips'] = 'List subscriped addresses'
cmdTbl['subscribe'] = 'Subscribes to an address'
cmdTbl['unsubscribe'] = 'Unsubscribe from an address'
cmdTbl['s5'] = '-'
cmdTbl['create'] = 'Create a channel'
cmdTbl['join'] = 'Join to a channel'
cmdTbl['leave'] = 'Leave from a channel'
cmdTbl['s6'] = '-'
cmdTbl['getLabel'] = 'Retrieve addresse(s) label for message heads'
cmdTbl['s7'] = '-'
cmdTbl['inbox'] = 'List all inbox message heads'
cmdTbl['outbox'] = 'List all outbox message heads heads'
cmdTbl['news'] = 'List all "unread" inbox message heads'
cmdTbl['send'] = 'Send out new message or broadcast'
cmdTbl['s8'] = '-'
cmdTbl['read'] = 'Read a message from in(out)box'
cmdTbl['readAll'] = 'Mard "read" for all inbox message(s)'
cmdTbl['unreadAll'] = 'Mark "unread" for all inbox message(s)'
cmdTbl['s9'] = '-'
cmdTbl['save'] = 'Save(Dump) a in(out)box message to disk'
cmdTbl['delete'] = 'Delete a(ll) in(out)box messages from remote'
cmdShorts = dict()

retStrings = dict({
    'none': '',
    'usercancel': '\n     User canceled.\n',
    'invalidinput': '\n     Invalid input.\n',
    'invalidindex': '\n     Invalid message index.\n',
    'invalidaddr': '\n     Invalid address.\n',
    'indexoutofbound': '\n     Reach end of index.\n',
    'bmsnotallow': '\n     Daemon configure command not allowed.\n',
    'nomain': '\n     Cannot locate "bitmessagemain.py", daemon start failed.\n',
    })
inputShorts = dict({
    'yes': ['y', 'yes'],
    'no': ['n', 'no'],
    'exit': ['e', 'ex', 'exit'],
    'deterministic': ['d', 'dt'],
    'random': ['r', 'rd', 'random'],
    'message': ['m', 'msg', 'message'],
    'broadcast': ['b', 'br', 'brd', 'broadcast'],
    'inbox': ['i', 'in', 'ib', 'inbox'],
    'outbox': ['o', 'ou', 'out', 'ob', 'outbox'],
    'dump': ['d', 'dp', 'dump'],
    'save': ['s', 'sa', 'save'],
    'reply': ['r', 'rp', 'reply'],
    'forward': ['f', 'fw', 'forward'],
    'delete': ['d', 'del', 'delete'],
    'all': ['a', 'all'],
    })
inputs = dict()


def duplicated(out):

    global cmdShorts

    seen = dict()
    dups = list()
    dcmds = dict()
    for x in out:
        if x not in seen:
            seen[x] = 1
        else:
            if seen[x] == 1:
                dups.append(x)
            seen[x] += 1
    for x in dups:
        for cmd in cmdShorts:
            if x in cmdShorts[cmd]:
                dcmds[cmd] = cmdShorts[cmd]
    return dcmds


def cmdGuess():

    global cmdTbl, cmdShorts

    fullWords = [
        'api', 'test', 'info', 'settings', 'quit', 'exit', 'set', 'list',
        'add', 'addresses', 'subscrips', 'label', 'all', 'delete', 'join',
        'scribe', 'build', 'in', 'out', 'box', 'new', 'create', 'end', 'shut',
        'read', 'down', 'get',  'del', 'address',
        'ubs', 'un', 'addressb', 'tatus', 'ave'
        ]
    halfWords = [
        'rate', 'lete', 'oin', 'lea', 'ead', 'eave', 'tatus', 'bke', 'un', 've',
        'fo', 'dress', 'boo', 'lete', 'reate', 'dae', 'mon', 'reate', 'sa',
        'inbox', 'outbox', 'send', 'in', 'add', 'news', 'all',
        ]
    fullWords.sort(key=lambda item: (-len(item), item))
    halfWords.sort(key=lambda item: (-len(item), item))

    out = list()
    # shorten
    wordscounter = 0
    for guessWords in [fullWords, halfWords]:
        wordscounter += 1
        for cmd in cmdTbl:
            lcmd = cmd.lower()
            if not any(cmdShorts.get(cmd, [])):  # keep full command name
                cmdShorts[cmd] = [lcmd]
            for words in guessWords:
                lwords = words.lower()
                lcmd = lcmd.replace(lwords, lwords[0], 1)
            if lcmd == lwords:
                break
            counter = len(cmdShorts[cmd])
            if lcmd not in cmdShorts[cmd]:
                if counter > 1 and len(lcmd) < len(cmdShorts[cmd][1]):
                    cmdShorts[cmd].insert(1, lcmd)
                else:
                    cmdShorts[cmd].append(lcmd)
                out.append(lcmd)

        dcmds = duplicated(out)
        if any(dcmds):
            print '\n     cmdGuess() Fail!'
            print '     duplicated =', dcmds
            print '     Change your "guessWords" list(%d).\n' % wordscounter
            return False

    cmdShorts['Command'] = ''
    cmdShorts['exit'] = ''
    cmdShorts['help'] = list(['help', 'h', '?'])
    return True


def showCmdTbl():

    global cmdTbl, cmdShorts

    url = 'https://github.com/BitMessage/PyBitmessage'
    print
    print ''.join([5 * ' ', 73 * '-'])
    print ''.join([5 * ' ', '|', url[:int(len(url)/2)].rjust(35), url[int(len(url)/2):].ljust(36), '|'])
    print ''.join([5 * ' ', 73 * '-'])
    for cmd in cmdTbl:
        lcmd = ('' if len(cmd) > 18 else cmd + ' ') + str(cmdShorts[cmd][1:])
        if len(lcmd) > 23:
            lcmd = lcmd[:20] + '...'
        des = cmdTbl[cmd]
        if len(des) > 45:
            des = des[:42] + '...'
        if des == '-':
            print '|'.join([5 * ' ', 24 * '-', 46 * '-', ''])
        else:
            print '| '.join([5 * ' ', lcmd.ljust(23), des.ljust(45), ''])
    print ''.join([5 * ' ', 73 * '-'])


class Config(object):
    def __init__(self, argv):
        self.version = "0.4.0"
        self.argv = argv
        self.action = None
        self.config_file = "client.dat"  # for initial default value
        self.conn = 'HTTP://127.0.0.1:8445/'  # default API uri
        self.createParser()
        self.createArguments()

    def createParser(self):
        # Create parser
        self.parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.parser.register('type', 'bool', self.strToBool)
        self.subparsers = self.parser.add_subparsers(title="Actions", dest="action")

    def __str__(self):
        return str(self.arguments).replace("Namespace", "Config")  # Using argparse str output

    def strToBool(self, v):
        return v.lower() in ("yes", "true", "t", "1")

    # Create command line arguments
    def createArguments(self):
        # this_file = os.path.abspath(__file__).replace("\\", "/").rstrip("cd")
        # if this_file.endswith("/src/bitmessagecli.py"):

        # main
        action = self.subparsers.add_parser("main", help='Start this CLI (default)')
        action = self.parser
        self.parser.add_argument('--version', action='version', version='BitMessageCLI %s' % (self.version))
        self.parser.add_argument('--start_daemon', help='Start BMs API daemon locally', default=None, metavar='BMs_host_uri')

        # api settings
        # action = self.subparsers.add_parser('api', help='Set API settings.')
        action.add_argument('--api_username', help='BMs API basic auth user name.', default=None, metavar='username')
        action.add_argument('--api_password', help='BMs API basic auth password.', default=None, metavar='password')
        action.add_argument('--api_path', help='BMs API host address.', default='127.0.0.1:8445', metavar='ip:port')
        action.add_argument('--api_type', help='BMs API hosts type.', default='HTTP', choices=["HTTP", "HTTPS"])

        # proxy settings
        # action = self.subparsers.add_parser('proxy', help='Use proxy for connections.')
        action.add_argument('--proxy_username', help='Username to authenticate to the proxy server.', default=None, metavar='username')
        action.add_argument('--proxy_password', help='Password to authenticate to the proxy server.', default=None, metavar='password')
        action.add_argument('--proxy_path', help='Address of the proxy server.', default='127.0.0.1:1080', metavar='ip:port')
        action.add_argument('--proxy_type', help='Proxy type.', default='none', choices=['none', 'SOCKS4', 'SOCKS5', 'HTTP'])
        action.add_argument('--proxy_remotedns', help='Send DNS request to remote(socks proxied).', type='bool', choices=[True, False], default=True)
        action.add_argument('--proxy_timeout', help='Network connection timeout.', default=30, type=int, metavar='seconds')

        self.parser.add_argument('--config_file', help='Path of config file.', default=self.config_file, metavar='path')
        self.parser.add_argument('--end', help='Stop multi value argument parsing(inner_use).', action='store_true')

        return self.parser

    # Find arguments specified for current action
    def getActionArguments(self):
        back = {}
        arguments = self.parser._subparsers._group_actions[0].choices[self.action]._actions[0:]  # First is --version
        # for argument in arguments:
        #    if argument.dest != 'help':
        #        back[argument.dest] = getattr(self, argument.dest)
        return back

    # Try to find action from argv
    def getAction(self, argv):
        actions = [action.choices.keys() for action in self.parser._actions if action.dest == "action"][0]  # Valid actions
        found_action = False
        for action in actions:  # See if any in argv
            if action in argv:
                found_action = action
                break
        return found_action

    # Move unknown parameters to end of argument list
    def moveUnknownToEnd(self, argv, default_action):
        valid_actions = sum([action.option_strings for action in self.parser._actions], [])
        valid_parameters = []
        unkown_parameters = []
        unkown = False
        for arg in argv:
            if arg.startswith("--"):
                if arg not in valid_actions:
                    unkown = True
                else:
                    unkown = False
            elif arg == default_action:
                unkown = False

            if unkown:
                unkown_parameters.append(arg)
            else:
                valid_parameters.append(arg)
        return valid_parameters + unkown_parameters

    # Parse arguments from config file and command line
    def parse(self, parse_config=True):
        argv = self.argv[:]  # Copy command line arguments
        self.parseCommandline(argv)  # Parse argv
        self.setAttributes()
        if parse_config:
            argv = self.parseConfig(argv)  # Add arguments from config file

        self.parseCommandline(argv)  # Parse argv
        self.setAttributes()

    # Parse command line arguments
    def parseCommandline(self, argv):
        # Find out if action is specificed on start
        action = self.getAction(argv)
        if not action:
            argv.append("--end")
            argv.append("main")

        action = "main"
        argv = self.moveUnknownToEnd(argv, action)
        self.arguments = self.parser.parse_args(argv[1:])

    # Parse config file
    def parseConfig(self, argv):
        # Find config file path from parameters
        if "--config_file" in argv:
            self.config_file = argv[argv.index("--config_file") + 1]
        print '- Configuration loading . (%s)' % os.path.realpath(self.config_file)
        if os.path.isfile(self.config_file):
            config = ConfigParser.ConfigParser(allow_no_value=True)
            config.read(self.config_file)
            for section in config.sections():
                for key, val in config.items(section):
                    if section != "global":  # If not global prefix key with section
                        key = section + "_" + key

                    to_end = key == "start_daemon"  # Prefer config value over argument
                    argv_extend = ["--%s" % key]
                    if val:
                        argv_extend.append(val)

                    if to_end:
                        argv = argv[:-1] + argv_extend + argv[-1:]
                    else:
                        argv = argv[:1] + argv_extend + argv[1:]
        return argv

    # Expose arguments as class attributes
    def setAttributes(self):
        # Set attributes from arguments
        if self.arguments:
            args = vars(self.arguments)
            for key, val in args.items():
                if type(val) is list:
                    val = val[:]
                setattr(self, key, val)

    def saveValue(self, key, value):
        if not os.path.isfile(self.config_file):
            content = ""
        else:
            content = open(self.config_file).read()
        lines = content.splitlines()

        global_line_i = None
        key_line_i = None
        i = 0
        for line in lines:
            if line.strip() == "[global]":
                global_line_i = i
            if line.startswith(key + " ="):
                key_line_i = i
            i += 1

        if key_line_i and len(lines) > key_line_i + 1:
            while True:  # Delete previous multiline values
                is_value_line = lines[key_line_i + 1].startswith(" ") or lines[key_line_i + 1].startswith("\t")
                if not is_value_line:
                    break
                del lines[key_line_i + 1]

        if value is None:  # Delete line
            if key_line_i:
                del lines[key_line_i]

        else:  # Add / update
            if type(value) is list:
                value_lines = [""] + [str(line).replace("\n", "").replace("\r", "") for line in value]
            else:
                value_lines = [str(value).replace("\n", "").replace("\r", "")]
            new_line = "%s = %s" % (key, "\n ".join(value_lines))
            if key_line_i:  # Already in the config, change the line
                lines[key_line_i] = new_line
            elif global_line_i is None:  # No global section yet, append to end of file
                lines.append("[global]")
                lines.append(new_line)
            else:  # Has global section, append the line after it
                lines.insert(global_line_i + 1, new_line)

        open(self.config_file, "w").write("\n".join(lines))


class Actions(object):
    def call(self, function_name, kwargs):
        print '- Original by .dok (Version 0.3.1) https://github.com/Dokument/PyBitmessage-Daemon'
        print '- Modified by .pt (Version 0.4.0) https://github.com/BitMessage/PyBitmessage'
        print '- Version: %s, Python %s' % (config.version, sys.version)

        func = getattr(self, function_name, None)
        back = func(**kwargs)
        if back:
            print back

    # Default action: Start CLI only
    def main(self, *argv):
        while True:
            try:
                CLI()
            except InputException as err:
                print retStrings.get(err.resKey, '\n     Not defined error raised: %s.\n' % err.resKey)

    def api(self, api_username, api_password, api_path, api_type):
        print 'action api: api_username:', api_username

    def proxy(self, proxy_username, proxy_password, proxy_path, proxy_type, proxy_timeout):
        print 'action proxy: proxy_username:', proxy_username


def start():
    ''' Call actions '''

    # action_kwargs = config.getActionArguments()
    actions.call(config.action, {})


# proxied start
# original https://github.com/benhengx/xmlrpclibex
# add basic auth support for top level host while none/HTTP proxied


class ProxyError(Exception): pass
class GeneralProxyError(ProxyError): pass
class Socks5AuthError(ProxyError): pass
class Socks5Error(ProxyError): pass
class Socks4Error(ProxyError): pass
class HTTPError(ProxyError): pass

def init_socks(proxy, timeout):
    '''init a socks proxy socket.'''
    import urllib

    map_to_type = {
        'SOCKS4':   socks.PROXY_TYPE_SOCKS4,
        'SOCKS5':   socks.PROXY_TYPE_SOCKS5,
        'HTTP': socks.PROXY_TYPE_HTTP
    }
    address_family = socket.AF_INET
    ssock = socks.socksocket(address_family, socket.SOCK_STREAM)
    ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # ssock.setsockopt()
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
    # ssock.connect(("www.google.com", 443))
    # urllib.urlopen("https://www.google.com/")
    return ssock


class SocksProxiedHTTPConnection(httplib.HTTPConnection):
    '''Proxy the http connection through a socks proxy.'''

    def init_socks(self, proxy):
        self.ssock = init_socks(proxy, self.timeout)

    def connect(self):
        self.ssock.connect((self.host, self.port))
        self.sock = self.ssock


class SocksProxiedHTTPSConnection(httplib.HTTPSConnection):
    '''Proxy the https connection through a socks proxy.'''

    def init_socks(self, proxy):
        self.ssock = init_socks(proxy, self.timeout)

    def connect(self):
        self.ssock.connect((self.host, self.port))
        self.sock = ssl.wrap_socket(self.ssock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_TLSv1)

    def close(self):
        httplib.HTTPSConnection.close(self)

        if self.ssock:
            self.ssock.close()
            self.ssock = None


class TransportWithTo(xmlrpclib.Transport):
    '''Transport support timeout'''

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
    '''Transport supports timeout and http proxy'''

    def __init__(self, proxy, use_datetime=0, timeout=None, api_cred=None):
        TransportWithTo.__init__(self, use_datetime, False, timeout)
        self.api_cred = api_cred
        self.proxy_path = proxy['proxy_path']
        if proxy['proxy_username'] and proxy['proxy_password']:
            self.proxy_cred = base64.encodestring('%s:%s' % (unquote(proxy['proxy_username']), unquote(proxy['proxy_password']))).strip()
        else:
            self.proxy_cred = None

    def request(self, host, handler, request_body, verbose=False):
        realhandler = 'HTTP://%s%s' % (host, handler)
        return TransportWithTo.request(self, host, realhandler, request_body, verbose)

    def make_connection(self, host):
        return TransportWithTo.make_connection(self, self.proxy_path)

    def send_content(self, connection, request_body):
        if self.proxy_cred:
            connection.putheader('Proxy-Authorization', 'Basic ' + self.proxy_cred)
        if self.api_cred:
            connection.putheader('Authorization', 'Basic ' + self.api_cred)
        return TransportWithTo.send_content(self, connection, request_body)


class SocksProxiedTransportWithTo(TransportWithTo):
    '''Transport supports timeout and socks SOCKS4/SOCKS5 and http connect tunnel'''

    cls_http_conn = SocksProxiedHTTPConnection
    cls_https_conn = SocksProxiedHTTPSConnection

    def __init__(self, proxy, use_datetime=0, is_https=False, timeout=None):
        TransportWithTo.__init__(self, use_datetime, is_https, timeout)
        self.proxy = proxy

    def make_connection(self, host):
        conn = TransportWithTo.make_connection(self, host)
        conn.init_socks(self.proxy)
        return conn


class Proxiedxmlrpclib(xmlrpclib.ServerProxy):
    """New added keyword arguments
    timeout: seconds waiting for the socket
    proxy: a dict specify the proxy settings, it supports the following fields:
        proxy_path: the address of the proxy server. default: 127.0.0.1:1080
        proxy_username: username to authenticate to the server. default None
        proxy_password: password to authenticate to the server, only relevant when
                  username is set. default None
        proxy_type: string, 'SOCKS4', 'SOCKS5', 'HTTP' (HTTP connect tunnel), only
                    relevant when is_socks is True. default 'SOCKS5'
    """

    def __init__(self, uri, transport=None, encoding=None, verbose=0,
                 allow_none=0, use_datetime=0, timeout=None, proxy=None):

        scheme, netloc, path, x, xx, xxx = urlparse(uri)
        api_username = urlparse(uri).username
        api_password = urlparse(uri).password
        api_cred = None
        self.uri = uri
        if api_username and api_password:
            api_cred = base64.encodestring('%s:%s' % (unquote(api_username), unquote(api_password))).strip()
            netloc = netloc.split('@')[1]

        if transport is None and (timeout or proxy):
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
                    transport = ProxiedTransportWithTo(proxy, use_datetime, timeout, api_cred)
                else:  # http connect and socksx
                    transport = SocksProxiedTransportWithTo(proxy, use_datetime, is_https, timeout)

        xmlrpclib.ServerProxy.__init__(self, self.uri, transport, encoding, verbose, allow_none, use_datetime)
# proxied end


class BMAPIWrapper(object):

    def set_proxy(self, proxy=None):
        self.proxy = proxy
        self.__init__(self.conn, self.proxy)

    def __init__(self, uri=None, proxy=None):
        self.proxy = proxy
        self.conn = uri

        proxied = 'non-proxied'
        if proxy:
            proxied = proxy['proxy_type'] + ' | ' + proxy['proxy_path']

        try:
            self.xmlrpc = Proxiedxmlrpclib(uri, verbose=False, allow_none=True, use_datetime=True, timeout=30, proxy=self.proxy)
            print '\n     XML-RPC initialed on: "%s" (%s)' % (self.conn, proxied)

        except Exception as err:  # IOError, unsupported XML-RPC protocol/
            self.xmlrpc = None
            print '\n     XML-RPC initial failed on: "%s" - {%s}\n' % (self.conn, err)
            # traceback.print_exc()

    def __getattr__(self, apiname):
        attr = getattr(self.xmlrpc, apiname, None)

        def wrapper(*args, **kwargs):
            error = 0
            result = ''
            errormsg = ''
            try:
                if attr is None:
                    error = 1
                    errormsg = '     Not prepared for calling API methods. (%s)' % apiname
                    return {'error': error, 'result': result, 'errormsg': errormsg}

                response = attr(*args, **kwargs)
                if type(response) is str and ("API Error" in response or 'RPC ' in response):  # API Error, Authorization Error, Proxy Error
                        error = 2
                        if "API Error" in response:
                            error = getAPIErrorCode(response)
                            if error in [20, 21]:  # programing error, Invalid method/Unexpected API Failure
                                print '\n     Maybe no such API method:', apiname
                                print '     Try helping:', self.xmlrpc.system.listMethods() if error == 20 else self.xmlrpc.system.methodHelp(apiname)
                        errormsg = '\n     ' + response + '\n'
                        return {'error': error, 'result': result, 'errormsg': errormsg}

                if apiname in [
                        'add',
                        'helloWorld',
                        'statusBar',
                        ]:
                    result = response
                else:  # pre-checking for API returns
                    try:
                        if apiname in [
                                'getAllInboxMessageIDs',
                                'getAllInboxMessageIds',
                                ]:
                            result = json.loads(response)['inboxMessageIds']
                        elif apiname in [
                                'getInboxMessageByID',
                                'getInboxMessageById',
                                ]:
                            result = json.loads(response)['inboxMessage']
                        elif apiname in [
                                'GetAllInboxMessages',
                                'getInboxMessagesByReceiver',
                                'getInboxMessagesByAddress',
                                ]:
                            result = json.loads(response)['inboxMessages']
                        elif apiname in [
                                'getAllSentMessageIDs',
                                'getAllSentMessageIds',
                                ]:
                            result = json.loads(response)['sentMessageIds']
                        elif apiname in [
                                'getAllSentMessages',
                                'getSentMessagesByAddress',
                                'getSentMessagesBySender',
                                'getSentMessageByAckData',
                                ]:
                            result = json.loads(response)['sentMessages']
                        elif apiname in [
                                'getSentMessageByID',
                                'getSentMessageById',
                                ]:
                            result = json.loads(response)['sentMessage']
                        elif apiname in [
                                'listAddressBookEntries',
                                'listAddressbook',
                                'listAddresses',
                                'listAddressbook',
                                'createDeterministicAddresses',
                                ]:
                            result = json.loads(response)['addresses']
                        elif apiname in [
                                'listSubscriptions',
                                ]:
                            result = json.loads(response)['subscriptions']
                        elif apiname in [
                                'decodeAddress',
                                'clientStatus',
                                'getMessageDataByDestinationHash',
                                'getMessageDataByDestinationTag',
                                ]:
                            result = json.loads(response)
                        elif apiname in [
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
                            result = response
                        else:
                            error = 99
                            errormsg = '\n     BMAPIWrapper error: unexpected api. <%s>\n' % apiname
                    except ValueError as err:  # json.loads error
                        error = 3
                        result = response
                        errormsg = '\n     Server returns unexpected data, maybe a network problem there? (%s)\n' % err

            except TypeError as err:  # unsupported XML-RPC protocol
                error = -1
                errormsg = '\n     XML-RPC not initialed correctly: %s.\n' % str(err)
                # traceback.print_exc()
            except (ProxyError, GeneralProxyError, Socks5AuthError, Socks5Error, Socks4Error, HTTPError, socket.error, xmlrpclib.ProtocolError, xmlrpclib.Fault) as err:  # (xmlrpclib.Error, ConnectionError, socks.GeneralProxyError)
                error = -2
                errormsg = '\n     Connection error: %s.\n' % str(err)
                # traceback.print_exc()
            except Exception:  # /httplib.BadStatusLine: connection close immediatly
                error = -99
                errormsg = '\n     Unexpected error: %s.\n' % sys.exc_info()[0]
                # traceback.print_exc()

            # print json.dumps({'error': error, 'result': result, 'errormsg': errormsg})
            return {'error': error, 'result': result, 'errormsg': errormsg}

        return wrapper


class InputException(Exception):
    def __init__(self, resKey):
        Exception.__init__(self, resKey)
        self.resKey = resKey

    def __str__(self):
        return self.resKey


def inputAddress(prompt='What is the address?'):

    global retStrings

    src = retStrings['invalidaddr']
    while True:
        address = userInput(prompt + '\nTry again or')
        if not validAddress(address):
            print src
            continue
        else:
            break

    return address

    def set_proxy(self, proxy=None):
        self.proxy = proxy
        self.__init__(self.conn, self.proxy)

def inputIndex(prompt='Input a index: ', maximum=-1, alter=[]):

    global retStrings

    while True:
        cinput = userInput(prompt + '\nTry again, (c) or').lower()
        try:
            if cinput == "c":
                cinput = '-1'
                raise InputException('usercancel')

            elif cinput in alter:
                break

            elif int(cinput) < 0 or (maximum >= 0 and int(cinput) > maximum):
                src = retStrings['invalidindex']
                print src

            else:
                break

        except (InputException, KeyboardInterrupt) as err:
            raise

        except ValueError:
            src = retStrings['invalidinput']
            print src

    return cinput


def userInput(message):
    """Checks input for exit or quit. Also formats for input, etc"""

    global cmdStr, retStrings

    stack = list(inspect.stack())
    where = ''.join([
        str(stack[3][2]),
        stack[3][3],
        str(stack[2][2]),
        stack[1][3],
        str(stack[1][2]),
        stack[3][3],
        cmdStr
        ])
    print ('\n%s (exit) to cancel.\nPress Enter to input default [%s]: ' % (message, inputs.get(where, '')))
    uInput = raw_input('>')

    if uInput.lower() == 'exit':  # Returns the user to the main menu
        raise InputException('usercancel')

    elif uInput == '':  # Return last value.
        return inputs.get(where, '')

    else:
        inputs[where] = uInput

    return uInput


def apiTest():
    """Tests the API connection to bitmessage. Returns true if it is connected."""

    response = api.add(2, 3)
    return response['result'] == 5 if response['error'] == 0 else False


def validAddress(address):
    """Predicate to test address validity"""

    print '     Validating...', address
    response = api.decodeAddress(address)
    if response['error'] != 0:
        print response['errormsg']
        return False

    return 'success' in response['result']['status'].lower()


def getAddress(passphrase, vNumber, sNumber):
    """Get a deterministic address"""

    passPhrase = passphrase.encode('base64')  # passphrase must be encoded
    print '     Getting address:', passphrase
    response = api.getDeterministicAddress(passPhrase, vNumber, sNumber)
    if response['error'] != 0:
        return response['errormsg']

    print '     Address:', response['result']


def subscribe(address, label):
    """Subscribe to an address"""

    label = label.encode('base64')
    print '     Subscribing address:', label
    response = api.addSubscription(address, label)
    if response['error'] != 0:
        return response['errormsg']

    return '\n    ' + response['result']


def unsubscribe(address):
    """Unsusbcribe from an address"""

    print '     unSubscribing address:', address
    response = api.deleteSubscription(address)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def listSubscriptions():
    """List subscriptions"""

    print '     Subscribed list retrieving...'
    response = api.listSubscriptions()
    if response['error'] != 0:
        return response['errormsg']

    jsonAddresses = response['result']
    numAddresses = len(jsonAddresses)
    print
    print '     ------------------------------------------------------------------------'
    print '     | #  |       Label        |               Address              |Enabled|'
    print '     |----|--------------------|------------------------------------|-------|'
    for addNum in range(0, numAddresses):  # processes all of the addresses and lists them out
        label = (jsonAddresses[addNum]['label'].decode('base64')).encode(
            'utf-8')              # may still misdiplay in some consoles
        address = str(jsonAddresses[addNum]['address'])
        enabled = str(jsonAddresses[addNum]['enabled'])

        if len(label) > 19:
            label = label[:16] + '...'

        print '| '.join(['     ', str(addNum).ljust(3), label.ljust(19), address.ljust(35), enabled.ljust(6), '', ])

    print ''.join(['     ', 72 * '-', '\n', ])

    return ''


def createChan(password):
    """Create a channel"""

    base64 = password.encode('base64')
    print '     Channel creating...', password
    response = api.createChan(base64)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def joinChan():
    """Join a channel"""

    uInput = ''
    address = inputAddress('Enter channel address')
    while uInput == '':
        uInput = userInput('Enter channel name[1~]')
    password = uInput.encode('base64')

    print '     Channel joining...', uInput
    response = api.joinChan(password, address)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def leaveChan():
    """Leave a channel"""

    address = inputAddress("Enter channel address")
    print '     Channel leaving...', 'address'
    response = api.leaveChan(address)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def listAdd():
    """List all of the addresses and their info"""

    print '     Retrieving...', 'Senders'
    response = api.listAddresses()
    if response['error'] != 0:
        return response['errormsg']

    jsonAddresses = response['result']
    numAddresses = len(jsonAddresses)  # Number of addresses
    # print '\nAddress Index,Label,Address,Stream,Enabled\n'
    print
    print '     ------------------------------------------------------------------------------'
    print '     | #  |       Label        |               Address                |S# |Enabled|'
    print '     |----|--------------------|--------------------------------------|---|-------|'
    for addNum in range(0, numAddresses):  # processes all of the addresses and lists them out
        label = jsonAddresses[addNum]['label'].encode(
            'utf-8')              # may still misdiplay in some consoles
        address = str(jsonAddresses[addNum]['address'])
        stream = str(jsonAddresses[addNum]['stream'])
        enabled = str(jsonAddresses[addNum]['enabled'])

        if len(label) > 19:
            label = label[:16] + '...'

        print '| '.join(['     ', str(addNum).ljust(3), label.ljust(19), address.ljust(37), stream.ljust(2), enabled.ljust(6), '', ])

    print ''.join(['     ', 78 * '-', '\n', ])

    return ''


def genAdd(lbl, deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe):
    """Generate address"""

    if deterministic is False:  # Generates a new address with the user defined label. non-deterministic
        addressLabel = lbl.encode('base64')
        print '     Address requesting...', lbl
        response = api.createRandomAddress(addressLabel)
        if response['error'] != 0:
            return response['errormsg']

    else:  # Generates a new deterministic address with the user inputs.
        passPhrase = passphrase.encode('base64')
        print '     Address deterministic...', passphrase
        response = api.createDeterministicAddresses(passPhrase, numOfAdd, addVNum, streamNum, ripe)
        if response['error'] != 0:
            return response['errormsg']

    return '\n     Address:', response['result']


def getBase64Len(x=''):

    strip = len(x) if len(x) < 4 else 2 if x[-2:] == '==' else 1 if x[-1] == '=' else 0
    return int(len(x) * 3 /4) - strip


def dump2File(fileName, fileData, deCoded):
    """Allows attachments and messages/broadcats to be saved"""

    global inputShorts

    # This section finds all invalid characters and replaces them with ~
    for s in ' /\\:*?"<>|':
        fileName = fileName.replace(s, '~')

    directory = os.path.abspath('attachments')

    if not os.path.exists(directory):
        try:
            os.makedirs(directory)

        except OSError as err:
            return '\n     %s.\n' % str(err)
            # return '\n     Failed creating ' + directory + '\n'
        except Exception:
            return '\n     Unexpected error: %s.\n' % sys.exc_info()[0]

    filePath = os.path.join(directory, fileName)

    if not deCoded:
        x = filter(lambda z: not re.match(r'^\s*$', z), fileData)
        trydecode = False
        if len(x) % 4 == 0:  # check by length before decode.
            trydecode = True
        else:
            print '\n'.join([
                '     -----------------------------------',
                '     Contents seems not "BASE64" encoded. (base on length check)',
                '     Start[%s] ~ Ends[%s].' % (x[:3], x[-3:]),
                '     About: %d(bytes).' % getBase64Len(x),
                '     FileName: "%s"' % fileName,
                ])
            uInput = userInput('Try to decode it anyway, (n)o or (Y)es?')
            if uInput not in inputShorts['no']:
                trydecode = True

        if trydecode is True:
            try:
                y = x.decode('base64', 'strict')
                if x == y.encode('base64').replace('\n', ''):  # double check decoded string.
                    fileData = y
                else:
                    print '\n     Failed on "BASE64" re-encode checking.\n'

            except ValueError:
                return '\n     Failed on "BASE64" decoding.\n'
        else:
            print '\n     Not "BASE64" contents, dump to file directly.'

    try:
        with open(filePath, 'wb+') as path_to_file:
                path_to_file.write(fileData)

    except IOError as err:
        return '\n     %s.\n' % str(err)
        # return '\n     Failed on operating: "' + filePath + '"\n'
    except Exception:
        return '\n     Unexpected error: %s.\n' % sys.exc_info()[0]

    return '     Successfully saved to: "' + filePath + '"'


def attachment():
    """Allows users to attach a file to their message or broadcast"""

    theAttachmentS = ''

    global inputShorts

    for counter in range(1, 3):  # maximum 3 of attachments
        isImage = False
        theAttachment = ''

        while True:  # loops until valid path is entered
            filePath = userInput(
                '\nPlease enter the path to the attachment or just the attachment name if in this folder[Max:180MB], %d/3 allowed.' % counter)

            try:
                with open(filePath):
                    break
            except IOError:
                print '\n     Failed open file on: ', filePath + '\n'

        # print filesize, and encoding estimate with confirmation if file is over X size (1mb?)
        invSize = os.path.getsize(filePath)
        invSize = (invSize / 1024)  # Converts to kilobytes
        round(invSize, 2)  # Rounds to two decimal places

        if invSize > 500.0:  # If over 500KB
            print '\n     WARNING:The file that you are trying to attach is %d(KB) and will take considerable time to send.\n' % invSize
            uInput = userInput('Are you sure you still want to attach it, (y)es or (N)o?').lower()

            if uInput not in inputShorts['yes']:
                return '\n     Attachment discarded.'

        elif invSize > 184320.0:  # If larger than 180MB, discard.
            return '\n     Attachment too big, maximum allowed size:180MB\n'

        pathLen = len(str(ntpath.basename(filePath)))  # Gets the length of the filepath excluding the filename
        fileName = filePath[(len(str(filePath)) - pathLen):]  # reads the filename

        filetype = imghdr.what(filePath)  # Tests if it is an image file
        if filetype is not None:
            print
            print '     ---------------------------------------------------'
            print '     Attachment detected as an Image.'
            print '     <img> tags will automatically be included,'
            print '     allowing the recipient to view the image'
            print '     using the "View HTML code..." option in Bitmessage.'
            print '     ---------------------------------------------------\n'
            isImage = True
            time.sleep(2)

        # Alert the user that the encoding process may take some time.
        print '     Encoding Attachment, Please Wait ...'

        with open(filePath, 'rb') as f:  # Begin the actual encoding
            data = f.read(188743680)  # Reads files up to 180MB, the maximum size for Bitmessage.
            data = data.encode("base64")

        if isImage:  # If it is an image, include image tags in the message
            theAttachment = """
<!-- Note: Image attachment below. Please use the right click "View HTML code ..." option to view it. -->
<!-- Sent using Bitmessage Daemon. https://github.com/BitMessage/PyBitmessage -->

Filename: %s
Filesize: %sKB
Encoding: base64

<center>
    <div id="image">
        <img alt="%s" src="data:image/%s;base64, %s"/>
    </div>
</center>""" % (fileName, invSize, fileName, filetype, data)
        else:  # Else it is not an image so do not include the embedded image code.
            theAttachment = """
<!-- Note: File attachment below. Please use a base64 decoder, or Daemon, to save it. -->
<!-- Sent using Bitmessage Daemon. https://github.com/BitMessage/PyBitmessage -->

Filename:%s
Filesize:%sKB
Encoding:base64

<attachment alt="%s" src="data:file/%s;base64, %s"/>""" % (fileName, invSize, fileName, fileName, data)

        uInput = userInput('Would you like to add another attachment, (y)es or (N)o?').lower()

        if uInput in inputShorts['yes']:  # Allows multiple attachments to be added to one message
            theAttachmentS = str(theAttachmentS) + str(theAttachment) + '\n\n'
        else:
            break

    theAttachmentS = theAttachmentS + theAttachment
    return theAttachmentS


def sendMsg(toAddress, fromAddress, subject=None, message=None):
    """
    With no arguments sent, sendMsg fills in the blanks.
    subject and message must be encoded before they are passed.
    """

    global retStrings, inputShorts

    if validAddress(toAddress) is False:
        toAddress = inputAddress("What is the To Address indeed?")

    if validAddress(fromAddress) is False:
        print '     Sender retrieving...', fromAddress
        response = api.listAddresses()
        if response['error'] != 0:
            return response['errormsg']

        jsonAddresses = response['result']
        numAddresses = len(jsonAddresses)  # Number of addresses

        if numAddresses > 1:  # Ask what address to send from if multiple addresses
            found = False
            while True:
                fromAddress = userInput('Enter an Address or Address Label to send from.')

                for addNum in range(0, numAddresses):  # processes all of the addresses
                    label = jsonAddresses[addNum]['label']
                    address = jsonAddresses[addNum]['address']
                    if fromAddress == label:  # address entered was a label and is found
                        fromAddress = address
                        found = True
                        break

                if found is False:
                    if validAddress(fromAddress) is False:
                        print '\n     Invalid Address. Please try again.\n'

                    else:
                        for addNum in range(0, numAddresses):  # processes all of the addresses
                            address = jsonAddresses[addNum]['address']
                            if fromAddress == address:  # address entered was a found in our addressbook.
                                found = True
                                break

                        if found is False:
                            print '\n     The address entered is not one of yours. Please try again.\n'

                if found:
                    break  # Address was found

        else:  # Only one address in address book
            print '\n     Using the only address in the addressbook to send from.\n'
            fromAddress = jsonAddresses[0]['address']

    if subject is None:
        subject = userInput('Enter your Subject.')
        subject = subject.encode('base64')

    if message is None:
        while True:
            try:
                message += '\n' + raw_input('Continue enter your message line by line, end with <CTL-D>.\n>')
            except EOFError:
                break

        uInput = userInput('Would you like to add an attachment, (y)es or (N)o?').lower()
        if uInput in inputShorts['yes']:
            message = message + '\n\n' + attachment()

        message = message.encode('base64')

    while True:
        print '     Message sending...', subject.decode('base64')
        ackData = api.sendMessage(toAddress, fromAddress, subject, message)
        if ackData['error'] == 1:
            return ackData['errormsg']
        elif ackData['error'] != 0:
            print ackData['errormsg']
            uInput = userInput('Would you like to try again, (n)o or (Y)es?').lower()
            if uInput in inputShorts['no']:
                break
        else:
            break

    if ackData['error'] == 0:
        print '     Fetching send status...'
        status = api.getStatus(ackData['result'])
        if status['error'] == 1:
            return status['errormsg']
        elif status['error'] != 0:
            print status['errormsg']
        else:
            return '     Message Status:' + status['result']

    return ''


def sendBrd(fromAddress=None, subject=None, message=None):
    """Send a broadcast"""

    global inputShorts
    if fromAddress is None:
        print '     Retrieving...', 'Senders'
        response = api.listAddresses()
        if response['error'] != 0:
            return response['errormsg']

        jsonAddresses = response['result']
        numAddresses = len(jsonAddresses)  # Number of addresses

        if numAddresses > 1:  # Ask what address to send from if multiple addresses
            found = False
            while True:
                fromAddress = userInput('Enter an Address or Address Label to send from.')

                for addNum in range(0, numAddresses):  # processes all of the addresses
                    label = jsonAddresses[addNum]['label']
                    address = jsonAddresses[addNum]['address']
                    if fromAddress == label:  # address entered was a label and is found
                        fromAddress = address
                        found = True
                        break

                if found is False:
                    if validAddress(fromAddress) is False:
                        print '\n     Invalid Address. Please try again.\n'

                    else:
                        for addNum in range(0, numAddresses):  # processes all of the addresses
                            address = jsonAddresses[addNum]['address']
                            if fromAddress == address:  # address entered was a found in our addressbook.
                                found = True
                                break

                        if found is False:
                            print '\n     The address entered is not one of yours. Please try again.\n'

                if found:
                    break  # Address was found

        else:  # Only one address in address book
            print '     Using the only address in the addressbook to send from.\n'
            fromAddress = jsonAddresses[0]['address']

    if subject is None:
        subject = userInput('Enter your Subject.')
    subject = subject.encode('base64')
    if message is None:
        while True:
            try:
                message += '\n' + raw_input('Continue enter your message line by line, end with <CTL-D>.\n>')
            except EOFError:
                break

        uInput = userInput('Would you like to add an attachment, (y)es or (N)o?').lower()
        if uInput in inputShorts['yes']:
            message = message + '\n\n' + attachment()

        message = message.encode('base64')

    while True:
        print '     Broadcast message sending...'
        ackData = api.sendBroadcast(fromAddress, subject, message)
        if ackData['error'] == 1:
            return ackData['errormsg']
        elif status['error'] != 0:
            print '\n     %s.\n' % str(err)
            uInput = userInput('Would you like to try again, no or (Y)es?').lower()
            if uInput in inputShorts['no']:
                break
        else:
            break

    if ackData['error'] == 0:
        print '     Fetching send status...'
        status = api.getStatus(ackData['result'])
        if status['error'] == 1:
            return status['errormsg']
        elif status['error'] != 0:
            print status['errormsg']
        else:
            return '     Message Status:' + status['result']

    return ''


def inbox(unreadOnly=False, pageNum=20):
    """Lists the messages by: message index, To Address Label, From Address Label, Subject, Received Time)"""

    print '     Inbox index fetching...'
    response = api.getAllInboxMessageIDs()
    if response['error'] != 0:
        return response['errormsg']

    messageIds = response['result']
    numMessages = len(messageIds)
    messagesPrinted = 0
    messagesUnread = 0
    for msgNum in range(numMessages - 1, -1, -1):  # processes all of the messages in the inbox
        messageID = messageIds[msgNum]['msgid']
        print '     -----------------------------------'
        print '     Inbox message retrieving...', messageID
        response = api.getInboxMessageByID(messageID)
        if response['error'] == 1:
            return response['errormsg']
        elif response['error'] != 0:
            print '\n     Retrieve failed on:', msgNum, messageID
            print response['errormsg']
        else:
            message = response['result'][0]
            # if we are displaying all messages or if this message is unread then display it
            if not unreadOnly or not message['read']:
                print '     -----------------------------------'
                print '     Inbox index: %d/%d' % (msgNum, numMessages - 1)  # message index
                print '     Message ID:', message['msgid']
                print '     Read:', message['read']
                print '     To:', getLabelForAddress(message['toAddress'])  # Get the to address
                print '     From:', getLabelForAddress(message['fromAddress'])  # Get the from address
                print '     Subject:', message['subject'].decode('base64')  # Get the subject
                print '     Received:', datetime.datetime.fromtimestamp(float(message['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')
                print '     Size: %d(bytes)' % getBase64Len(message['message'])
                messagesPrinted += 1
                if not message['read']:
                    messagesUnread += 1

                if messagesPrinted % pageNum == 0 and messagesPrinted != 0:
                    try:
                        uInput = userInput('Paused on %d/%d, next [%d],' % (msgNum, numMessages - 1, msgNum - pageNum if msgNum > pageNum else 0))

                    except InputException as err:
                        raise InputException(str(err))

    print '     -----------------------------------'
    print '     There are %d unread messages of %d messages in the inbox.' % (messagesUnread, numMessages)
    print '     -----------------------------------'

    return ''


def outbox(pageNum=20):
    """TBC"""

    print '     All outbox messages downloading...'
    response = api.getAllSentMessages()
    if response['error'] != 0:
        return response['errormsg']

    outboxMessages = response['result']
    numMessages = len(outboxMessages)
    for msgNum in range(numMessages - 1, -1, -1):  # processes all of the messages in the outbox
        message = outboxMessages[msgNum]
        print '     -----------------------------------'
        print '     Outbox index: %d/%d' % (msgNum, numMessages - 1)  # message index
        print '     Message ID:', message['msgid']
        print '     To:', getLabelForAddress(message['toAddress'])  # Get the to address
        # Get the from address
        print '     From:', getLabelForAddress(message['fromAddress'])
        print '     Subject:', message['subject'].decode('base64')  # Get the subject
        print '     Status:', message['status']  # Get the status
        print '     Ack:', message['ackData']  # Get the ackData
        print '     Last Action Time:', datetime.datetime.fromtimestamp(float(message['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S')
        print '     Size: %d(bytes)' % getBase64Len(message['message'])

        if msgNum % pageNum == 0 and msgNum != 0:
            uInput = userInput('Paused on %d/%d, next [%d],' % (msgNum, numMessages - 1, msgNum - pageNum if msgNum > pageNum else 0))

    print '     -----------------------------------'
    print '     There are ', numMessages, ' messages in the outbox.'
    print '     -----------------------------------\n'

    return ''


def attDetect(content=None, textmsg=None, attPrefix=None, askSave=True):

    global inputShorts

    attPos = msgPos = 0
    counter = 0
    prefixRe = re.compile(r'<(\w*)\s*[^<>]*src="[^"]*;base64,$')
    suffixRe = re.compile(r'("\s*/?>)')
    fnRe1 = re.compile(r'alt="([^"]*)"*\s*[^<>]*;base64,$')  # alt= preferred for attachment filename
    fnRe2 = re.compile(r'src="([^"]*)"*\s*[^<>]*;base64,$')
    # Hard way search attachments
    while counter < 4:  # Allows maximum 3 of attachments to be downloaded/saved
        try:
            attEndPos = attPos = content.index(';base64,', attPos) + len(';base64,')  # Finds the attachment position
            hasEnd = suffixRe.search(content[attPos:])
            if hasEnd:
                attEndPos = attPos + hasEnd.start() + len(hasEnd.group(1))
            else:
                raise ValueError

            attPre = attPos - len(';base64,') - 1  # back forward searching based on ;base64
            attOffset = attPos - msgPos
            # try remove prefix <xxxx | <xxxxxxxxxxx
            prefix_max = attOffset if attOffset <= 180 else 180  # define max forward searching for base64 embedded codes '<xxxx
            prefixStr = content[attPos - prefix_max:attPos]
            iscomplete = prefixRe.search(prefixStr)
            if iscomplete and hasEnd.start() >= 4:  # too small not attachments, leave as is
                havefn = fnRe1.search(prefixStr)
                if not havefn:
                    havefn = fnRe2.search(prefixStr)
                fn = '%s_%d_%s_%s' % (attPrefix, attPos, iscomplete.group(1), havefn.group(1) if havefn else 'notdetected')
                attPre = attPos - prefix_max + iscomplete.start()

            this_attachment = content[attPos:attPos + hasEnd.start()]
            x = filter(lambda z: not re.match(r'^\s*$', z), this_attachment)
            # x = x.replace('\n', '').strip()
            trydecode = False
            counter += 1
            if len(x) % 4 == 0:  # check by length before decode.
                trydecode = True
            else:
                print '\n'.join([
                    '     -----------------------------------',
                    '     Embeded mesaage seems not "BASE64" encoded. (base on length check)',
                    '     Offset: %d, about: %d(bytes).' % (attPre, getBase64Len(x)),
                    '     Start[%s] ~ Ends[%s].' % (x[:3], x[-3:]),
                    '     FileName: "%s"' % fn,
                ])
                uInput = userInput('Try to decode anyway, (n)o or (Y)es?')
                if uInput not in inputShorts['no']:
                    trydecode = True
            if trydecode is True:
                try:
                    y = x.decode('base64', 'strict')
                    if x == y.encode('base64').replace('\n', ''):  # double check decoded string.
                        if askSave is True:
                            uInput = userInput('Download the "decoded" attachment, (y)es or (No)?\nNames[%d]: %s,' % (counter, fn)).lower()
                            if uInput in inputShorts['yes']:
                                src = dump2File(fn, y, True)
                            else:
                                src = '     Attachment skiped[%d] "%s".' % (counter, fn)
                        else:
                            src = dump2File(fn, y, True)

                        print src
                        attmsg = '\n'.join([
                            '     -----------------------------------',
                            '     Attachment[%d]: "%s"' % (counter, fn),
                            '     Size: %d(bytes)' % getBase64Len(x),
                            '     -----------------------------------',
                            ])
                        # remove base64 and '<att' prefix and suffix '/>' stuff
                        textmsg = textmsg + content[msgPos:attPre] + attmsg
                        msgPos = attEndPos
                    else:
                        print '\n     Failed on decode this embeded "BASE64" like message on re-encode check.\n'

                except ValueError:
                    print '\n     Failed on decode this emdeded "BASE64" encoded like message.\n'
                except InputException:
                    raise
                except Exception:
                    print '\n     Unexpected error: %s.\n' % sys.exc_info()[0]

            else:
                print '\n    Skiped a embeded "BASE64" encoded like message.'

            if attEndPos != msgPos:
                textmsg = textmsg + content[msgPos:attEndPos]
                msgPos = attEndPos

        except ValueError:
            textmsg = textmsg + content[msgPos:]
            break
        except InputException:
            raise
        except Exception:
            traceback.print_exc()
            print '\n     Unexpected error: %s.\n' % sys.exc_info()[0]

    return textmsg


def readSentMsg(cmd='read', msgNum=-1, messageID=None, trunck=380, withAtta=False):
    """Opens a sent message for reading"""

    print '     All outbox messages downloading...', str(msgNum), messageID
    if not messageID:
        response = api.getAllSentMessages()
        if response['error'] != 0:
            return response['errormsg']

        message = response['result'][msgNum]
    else:
        response = api.getSentMessageByID(messageID)
        if response['error'] != 0:
            return response['errormsg']

        message = response['result'][0]

    subject = message['subject'].decode('base64')
    content = message['message'].decode('base64')
    full = len(content)
    textmsg = ''
    textmsg = content if withAtta else attDetect(content, textmsg, 'outbox_' + subject, cmd != 'save')

    print '    ', 74 * '-'
    print '     Message index:', str(msgNum)  # message outdex
    print '     Message ID:', message['msgid']
    print '     To:', getLabelForAddress(message['toAddress'])  # Get the to address
    # Get the from address
    print '     From:', getLabelForAddress(message['fromAddress'])
    print '     Subject:', subject  # Get the subject
    print '     Status:', message['status']  # Get the status
    print '     Ack:', message['ackData']  # Get the ackData

    print '     Last Action Time:', datetime.datetime.fromtimestamp(float(message['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S')
    print '     Length: %d/%d' % (trunck if trunck <= full else full, full)
    print '     Message:\n'
    print textmsg if trunck < 0 or len(textmsg) <= trunck else textmsg[:trunck] + '\n\n     ~< MESSAGE TOO LONG TRUNCKED TO SHOW >~'
    print '    ', 74 * '-'

    if cmd == 'save':
        ret = dump2File('outbox_' + subject, textmsg, True)
        print ret

    return ''


def readMsg(cmd='read', msgNum=-1, messageID=None, trunck=380, withAtta=False):
    """Open a message for reading"""

    print '     Inbox message reading...', str(msgNum)
    response = api.getInboxMessageByID(messageID, True)
    if response['error'] != 0:
        return response['errormsg']

    message = response['result'][0]
    subject = message['subject'].decode('base64')
    content = message['message'].decode('base64')  # Message that you are replying too.
    full = len(content)
    textmsg = ''
    textmsg = content if withAtta else attDetect(content, textmsg, 'inbox_' + subject, cmd != 'save')

    print '    ', 74 * '-'
    print '     Inbox index :', msgNum  # message index
    print '     Message ID:', message['msgid']
    print '     Read:', message['read']
    print '     To:', getLabelForAddress(message['toAddress'])  # Get the to address
    # Get the from address
    print '     From:', getLabelForAddress(message['fromAddress'])
    print '     Subject:', subject  # Get the subject
    print '     Received:', datetime.datetime.fromtimestamp(float(message['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')
    print '     Length: %d/%d' % (trunck if trunck <= full else full, full)
    print '     Message:\n'
    print textmsg if trunck < 0 or len(textmsg) <= trunck else textmsg[:trunck] + '\n\n     ~< MESSAGE TOO LONG TRUNCKED TO SHOW >~'
    print '    ', 74 * '-'

    if cmd == 'save':
        ret = dump2File('inbox_' + subject + str(full), textmsg, True)
        print ret

    return ''

def replyMsg(msgNum=-1, messageID=None, forwardORreply=None):
    """Allows you to reply to the message you are currently on. Saves typing in the addresses and subject."""

    global inputShorts, retStrings

    forwardORreply = forwardORreply.lower()  # makes it lowercase
    print '     Inbox message %s... %d' % (forwardORreply, msgNum)
    response = api.getInboxMessageByID(messageID, True)
    if response['error'] != 0:
        return response['errormsg']

    message = response['result'][0]
    subject = message['subject'].decode('base64')
    content = message['message'].decode('base64')  # Message that you are replying too.
    full = len(content)
    textmsg = ''
    textmsg = attDetect(content, textmsg, subject, True)

    if forwardORreply == 'forward':
        attachMessage = '\n'.join([
            '> To: ', fwdFrom,
            '> From: ', fromAdd,
            '> Subject: ', subject,
            '> Received: ', recvTime,
            '> Message:',
            ])
    else:
        attachMessage = ''
    for line in textmsg.splitlines():
        attachMessage = attachMessage + '> ' + line + '\n'

    fromAdd = message['toAddress']  # Address it was sent To, now the From address
    fwdFrom = message['fromAddress']  # Address it was sent To, will attached to fwd
    recvTime = datetime.datetime.fromtimestamp(float(message['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')

    if forwardORreply == 'reply':
        toAdd = message['fromAddress']  # Address it was From, now the To address
        subject = "Re: " + re.sub('^Re: *', '', subject)

    elif forwardORreply == 'forward':
        subject = "Fwd: " + re.sub('^Fwd: *', '', subject)
        toAdd = inputAddress("What is the To Address?")

    else:
        return '\n     Invalid Selection. Reply or Forward only'

    subject = subject.encode('base64')

    message = ''
    while True:
        try:
            print '\n'.join([
                '     Drafting:',
                message,
                '     -----------------------------------',
                ])
            message += '\n' + raw_input('Continue enter your message line by line, end with <CTL-D>.\n>')
        except EOFError:
            break

    src = retStrings['usercancel']
    uInput = userInput('Would you like to add an attachment, (y)es or (N)o?').lower()
    if uInput in inputShorts['yes']:
        message = message + '\n\n' + attachment()

    message = message + '\n\n------------------------------------------------------\n'
    message = message + attachMessage
    message = message.encode('base64')

    print message
    uInput = userInput('Realy want to send upper message, (n)o or (Y)es?').lower()
    if uInput not in inputShorts['no']:
        src = sendMsg(toAdd, fromAdd, subject, message)

    return src


def delMsg(msgNum=-1, messageID=None):
    """Deletes a specified message from the inbox"""

    print '     Inbox message deleting...', messageID
    response = api.trashMessage(messageID)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def delSentMsg(msgNum=-1, messageID=None):
    """Deletes a specified message from the outbox"""

    if not messageID:
        print '     All outbox messages downloading...', str(msgNum)
        response = api.getAllSentMessages()
        if response['error'] != 0:
            return response['errormsg']

        outboxMessages = response['result']
        # gets the message ackData via the message index number
        ackData = outboxMessages[msgNum]['ackData']
        print '     Outbox message deleting...', ackData
        response = api.trashSentMessageByAckData(ackData)
        if response['error'] != 0:
            return response['errormsg']
    else:
        print '     Outbox message deleting...', messageID
        response = api.trashSentMessage(messageID)
        if response['error'] != 0:
            return response['errormsg']

    return '\n     ' + response['result']


def toReadInbox(cmd='read', trunck=380, withAtta=False):

    global inputShorts, retStrings

    numMessages = 0
    print '     Inbox index fetching...'
    response = api.getAllInboxMessageIDs()
    if response['error'] != 0:
        return response['errormsg']

    messageIds = response['result']
    numMessages = len(messageIds)
    if numMessages < 1:
        return '     Zero message found.\n'

    src = retStrings['usercancel']
    if cmd != 'delete':
        msgNum = int(inputIndex('Input the index of the message to %s [0-%d]: ' % (cmd, numMessages - 1), numMessages - 1))

        nextNum = msgNum
        ret = ''
        while msgNum >= 0:  # save, read
            nextNum += 1
            messageID = messageIds[msgNum]['msgid']
            if cmd == 'save':
                ret = readMsg(cmd, msgNum, messageID, trunck, withAtta)
                return ret

            else:
                ret = readMsg(cmd, msgNum, messageID)
            print ret

            uInput = userInput('Would you like to set this message to unread, (y)es or (N)o?').lower()
            if uInput in inputShorts['yes']:
                ret = markMessageReadbit(msgNum, messageID, False)

            else:
                uInput = userInput('Would you like to (f)orward, (r)eply, (s)ave, (d)ump or Delete this message?').lower()

                if uInput in inputShorts['reply']:
                    ret = replyMsg(msgNum, messageID, 'reply')

                elif uInput in inputShorts['forward']:
                    ret = replyMsg(msgNum, messageID, 'forward')

                elif uInput in inputShorts['save']:
                    ret = readMsg('save', msgNum, messageID, withAtta=False)

                elif uInput in inputShorts['dump']:
                    ret = readMsg('save', msgNum, messageID, withAtta=True)

                else:
                    uInput = userInput('Are you sure to delete, (y)es or (N)o?').lower()  # Prevent accidental deletion
                    if uInput in inputShorts['yes']:
                        # nextNum -= 1
                        # numMessages -= 1
                        ret = delMsg(msgNum, messageID)

            print ret
            if nextNum < numMessages:
                uInput = userInput('Next message, (n)o or (Y)es?').lower()  # Prevent
                msgNum = nextNum if uInput not in inputShorts['no'] else -1

            else:
                msgNum = -1
                src = retStrings['indexoutofbound']

    else:
        uInput = inputIndex('Input the index of the message you wish to delete or (A)ll to empty the inbox [0-%d]: ' % (numMessages - 1), numMessages - 1, inputShorts['all'][0]).lower()

        if uInput in inputShorts['all']:
            ret = inbox(False)
            print ret
            uInput = userInput('Are you sure to delete all this %d message(s), (y)es or (N)o?' % numMessages).lower()  # Prevent accidental deletion
            if uInput in inputShorts['yes']:
                for msgNum in range(0, numMessages):  # processes all of the messages in the outbox
                    ret = delMsg(msgNum, messageIds[msgNum]['msgid'])
                    print ret
                src = ''

        else:
            nextNum = msgNum = int(uInput)
            while msgNum >= 0:  # save, read
                nextNum += 1
                messageID = messageIds[msgNum]['msgid']
                ret = readMsg(cmd, msgNum, messageID)
                print ret

                uInput = userInput('Are you sure to delete, (y)es or (N)o?').lower()  # Prevent accidental deletion
                if uInput in inputShorts['yes']:
                    # nextNum -= 1
                    # numMessages -= 1
                    ret = delMsg(msgNum, messageID)
                    print ret

                if nextNum < numMessages:
                    uInput = userInput('Next message, (n)o or (Y)es?').lower()  # Prevent
                    msgNum = nextNum if uInput not in inputShorts['no'] else -1

                else:
                    msgNum = -1
                    src = retStrings['indexoutofbound']

    return src


def toReadOutbox(cmd='read', trunck=380, withAtta=False):

    global inputShorts, retStrings

    print '     Outbox index fetching...'
    response = api.getAllSentMessageIDs()
    if response['error'] != 0:
        return response['errormsg']

    messageIds = response['result']
    numMessages = len(messageIds)
    if numMessages < 1:
        return '     Zero message found.\n'

    src = retStrings['usercancel']
    if cmd != 'delete':
        msgNum = int(inputIndex('Input the index of the message open [0-%d]: ' % (numMessages - 1), numMessages - 1))

        nextNum = msgNum
        ret = ''
        while msgNum >= 0:  # save, read
            nextNum += 1
            messageID = messageIds[msgNum]['msgid']
            if cmd == 'save':
                ret = readSentMsg(cmd, msgNum, messageID, trunck, withAtta)
                return ret

            else:
                ret = readSentMsg(cmd, msgNum, messageID)

            print ret
            # Gives the user the option to delete the message
            uInput = userInput('Would you like to (s)ave, (d)ump or Delete this message directly?').lower()

            if uInput in inputShorts['save']:
                ret = readSentMsg('save', msgNum, messageID, withAtta=False)

            elif uInput in inputShorts['dump']:
                ret = readSentMsg('save', msgNum, messageID, withAtta=True)

            else:
                uInput = userInput('Are you sure to delete, (y)es or (N)o?').lower()  # Prevent accidental deletion
                if uInput in inputShorts['yes']:
                    nextNum -= 1
                    numMessages -= 1
                    ret = delSentMsg(msgNum, messageID)

            print ret
            if nextNum < numMessages:
                uInput = userInput('Next message, (n)o or (Y)es?').lower()  # Prevent
                msgNum = nextNum if uInput not in inputShorts['no'] else -1

            else:
                msgNum = -1
                src = retStrings['indexoutofbound']

    else:
        uInput = inputIndex('Input the index of the message you wish to delete or (A)ll to empty the outbox [0-%d]: ' % (numMessages - 1), numMessages - 1, inputShorts['all'][0]).lower()

        if uInput in inputShorts['all']:
            ret = outbox()
            print ret
            uInput = userInput('Are you sure to delete all this %d message(s), (y)es or (N)o?' % numMessages).lower()  # Prevent accidental deletion
            if uInput in inputShorts['yes']:
                for msgNum in range(0, numMessages):  # processes all of the messages in the outbox
                    ret = delSentMsg(msgNum, messageIds[msgNum]['msgid'])
                    print ret
                src = ''

        else:
            nextNum = msgNum = int(uInput)
            while msgNum >= 0:  # save, read
                nextNum += 1

                messageID = messageIds[msgNum]['msgid']
                ret = readSentMsg(cmd, msgNum, messageID)
                print ret

                uInput = userInput('Are you sure to delete this message, (y)es or (N)o?').lower()  # Prevent accidental deletion
                if uInput in inputShorts['yes']:
                    nextNum -= 1
                    numMessages -= 1
                    ret = delSentMsg(msgNum, messageID)
                    print ret

                if nextNum < numMessages:
                    uInput = userInput('Next message, (n)o or (Y)es?').lower()  # Prevent
                    msgNum = nextNum if uInput not in inputShorts['no'] else -1

                else:
                    msgNum = -1
                    src = retStrings['indexoutofbound']

    return src


def getLabelForAddress(address):
    """Get label for an address"""

    for entry in knownAddresses['addresses']:
        if entry['address'] == address:
            return "%s (%s)" % (entry['label'], entry['address'])

    return address


def getLabel():
    """Build known addresses"""

    # add from address book
    errors = ''
    newentry = []
    print '     Retrieving...', 'Contacts'
    addresses = api.listAddressBookEntries()
    if addresses['error'] != 0:
        print addresses['errormsg']
    else:
        for entry in addresses['result']:
            isnew = True
            for old in knownAddresses['addresses']:
                if entry['address'] == old['address']:
                    isnew = False
                    break
            if isnew is True:
                newentry.append({'label': entry['label'].decode('base64').encode('utf-8'), 'address': entry['address']})
        if any(newentry):
            for new in newentry:
                knownAddresses['addresses'].append(new)

    newentry = []
    print '     Retrieving...', 'Senders'
    addresses = api.listAddresses()
    if addresses['error'] != 0:
        print addresses['errormsg']
    else:
        for entry in addresses['result']:
            isnew = True
            for old in knownAddresses['addresses']:
                if entry['address'] == old['address']:
                    isnew = False
                    break
            if isnew is True:
                newentry.append({'label': entry['label'].encode('utf-8'), 'address': entry['address']})
        if any(newentry):
            for new in newentry:
                knownAddresses['addresses'].append(new)

    return ''


def listAddressBK(printKnown=False):
    """List addressbook entries"""

    if not printKnown:
        print '     Retrieving...', 'Contacts'
        response = api.listAddressBookEntries()
        if response['error'] != 0:
            return response['errormsg']
        addressBook = response['result']
    else:
        addressBook = knownAddresses['addresses']

    numAddresses = len(addressBook)
    print
    print '     ------------------------------------------------------------------'
    print '     | #  |       Label        |               Address                |'
    print '     |----|--------------------|--------------------------------------|'
    for addNum in range(0, numAddresses):  # processes all of the addresses and lists them out
        entry = addressBook[addNum]
        label = entry['label'].decode('base64').encode('utf-8') if not printKnown else entry['label']
        address = entry['address']
        if len(label) > 19:
            label = label[:16] + '...'
        print '| '.join(['     ', str(addNum).ljust(3), label.ljust(19), address.ljust(37), '', ])
    print ''.join(['     ', 66 * '-', '\n', ])

    return ''


def addAddressToAddressBook(address, label):
    """Add an address to an addressbook"""

    print '     Adding...', label
    response = api.addAddressBK(address, label.encode('base64'))
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def deleteAddressFromAddressBook(address):
    """Delete an address from an addressbook"""

    print '     Deleting...', address
    response = api.delAddressBK(address)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def getAPIErrorCode(response):
    """Get API error code"""

    if "API Error" in response:
        # if we got an API error return the number by getting the number
        # after the second space and removing the trailing colon
        return int(response.split()[2][:-1])


def markMessageReadbit(msgNum=-1, messageID=None, read=False):
    """Mark a mesasge as unread/read"""

    print '     Marking...', str(msgNum),
    response = api.getInboxMessageByID(messageID, read)
    if response['error'] != 0:
        print 'Failed.'
        return response['errormsg']

    print 'OK.'
    return ''


def markAllMessagesReadbit(read=False):
    """Mark all messages as unread/read"""

    print '     Inbox index fetching...', 'mark'
    response = api.getAllInboxMessageIDs()
    if response['error'] != 0:
        return response['errormsg']

    messageIds = response['result']
    numMessages = len(messageIds)
    if numMessages < 1:
        return '     Zero message found.\n'

    for msgNum in range(0, numMessages):  # processes all of the messages in the inbox
        src = markMessageReadbit(msgNum, messageIds[msgNum]['msgid'], read)
        print src

    return ''


def addInfo(address):

    print '     Address decoding...', address
    response = api.decodeAddress(address)
    if response['error'] != 0:
        return response['errormsg']

    addinfo = response['result']
    print '     ------------------------------'
    if 'success' in addinfo['status'].lower():
        print '     Valid Address'
        print '     Address Version: %s' % str(addinfo['addressVersion'])
        print '     Stream Number: %s\n' % str(addinfo['streamNumber'])
    else:
        print '\n     Invalid Address !\n'

    return ''


def clientStatus():
    """Print the client status"""

    print '     Client status fetching...'
    print '     ------------------------------'

    response = api.clientStatus()
    if response['error'] == 0:
        client_status = response['result']
        for key in client_status.keys():
            print '    ', key, ':', str(client_status[key])
    else:
        print response['errormsg']

    response = api.getAllInboxMessageIDs()
    if response['error'] == 0:
        inboxMessageIds = response['result']
        inumMessages = len(inboxMessageIds)
        print '     InboxMessages:', str(inumMessages)
    else:
        print response['errormsg']

    response = api.getAllSentMessageIDs()
    if response['error'] == 0:
        outboxMessageIds = response['result']
        onumMessages = len(outboxMessageIds)
        print '     OutboxMessages:', str(onumMessages)
    else:
        print response['errormsg']
    # print '     Message.dat:', str(boxSize)
    # print '     knownNodes.dat:', str(knownNodes)
    # print '     debug.log:', str(debugSize)

    print '     ------------------------------'

    return ''


def shutdown():
    """Shutdown the API"""

    print '     Shutdown command sending...'
    response = api.shutdown()
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def start_daemon(uri=''):

    start_dir = os.path.dirname(os.path.abspath(__file__))
    mainfile = os.path.join(start_dir, 'bitmessagemain.py')
    print "     Try to start daemon: %s..." % uri
    if os.path.isfile(mainfile):
        cmd = ' '.join([sys.executable, mainfile, '--daemon'])
        print '\n     Exec:', cmd, uri
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        result = out.split('\n')
        for line in result:
            print '     ' + line
    else:
        print '     ' + retStrings['nomain']


def UI(cmdInput=None):
    """Main user menu"""

    global usrPrompt, inputShorts, cmdShorts, retStrings, bms_allow

    src = 'MUST WRONG'
    uInput = ''

    if not any(cmdShorts):
        if not cmdGuess():
            raise SystemExit('\n     Bye\n')

    if cmdInput in cmdShorts['help']:
        src = showCmdTbl()

    elif cmdInput in cmdShorts['daemon']:
        src = start_daemon(getattr(config, 'start_daemon', ''))

    elif cmdInput in cmdShorts['apiTest']:  # tests the API Connection.
        print '     API connection test has:',
        print 'PASSED' if apiTest() else 'FAILED\n'
        src = ''

    elif cmdInput in cmdShorts['addInfo']:
        while uInput == '':
            uInput = userInput('Input the Bitmessage Address.')
        src = addInfo(uInput)

    elif cmdInput in cmdShorts['bmSettings']:  # tests the API Connection.
        if bms_allow is True:
            if hasattr(conninit, 'main') and hasattr(conninit, 'bmSettings'):
                src = conninit.bmSettings()
            else:
                src = '\n     Depends moudle changed, calling dismissed.'
        else:
            src = '     ' + retStrings['bmsnotallow']

    elif cmdInput in cmdShorts['quit']:  # Quits the application
        raise SystemExit('\n     Bye\n')

    elif cmdInput in cmdShorts['listAddresses']:  # Lists all of the identities in the addressbook
        src = listAdd()

    elif cmdInput in cmdShorts['newAddress']:  # Generates a new address
        uInput = userInput('Would you like to create a (d)eterministic or (R)andom address?').lower()

        if uInput in inputShorts['deterministic']:  # Creates a deterministic address
            deterministic = True

            lbl = ''
            passphrase = userInput('Input the Passphrase.')  # .encode('base64')
            numOfAdd = int(userInput('How many addresses would you like to generate?'))
            addVNum = 3
            streamNum = 1
            isRipe = userInput('Shorten the address, (Y)es or no?').lower()

            if isRipe in inputShorts['yes']:
                ripe = True
                src = genAdd(lbl, deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe)

            else:
                ripe = False
                src = genAdd(lbl, deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe)

        else:  # Creates a random address with user-defined label
            deterministic = False
            lbl = null = None
            while lbl is None:
                lbl = userInput('Input the label for the new address.')
            src = genAdd(lbl, deterministic, null, null, null, null, null)

    elif cmdInput in cmdShorts['getAddress']:  # Gets the address for/from a passphrase
        while len(uInput) < 6:
            uInput = userInput('Input a strong address passphrase.[6-]')
        src = getAddress(uInput, 4, 1)

    elif cmdInput in cmdShorts['subscribe']:  # Subsribe to an address
        address = inputAddress('What address would you like to subscribe?')
        while uInput == '':
            uInput = userInput('Enter a label for this address.')
        src = subscribe(address, uInput)

    elif cmdInput in cmdShorts['unsubscribe']:  # Unsubscribe from an address
        address = inputAddress("What address would you like to unsubscribe from?")
        uInput = userInput('Are you sure to unsubscribe: [%s]?' % address)
        if uInput in inputShorts['yes']:
            src = unsubscribe(address)

    elif cmdInput in cmdShorts['listsubscrips']:  # Unsubscribe from an address
        src = listSubscriptions()

    elif cmdInput in cmdShorts['create']:
        while uInput == '':
            uInput = userInput('Enter channel name')
        src = createChan(uInput)

    elif cmdInput in cmdShorts['join']:
        src = joinChan()

    elif cmdInput in cmdShorts['leave']:
        src = leaveChan()

    elif cmdInput in cmdShorts['getLabel']:  # Retrieve all of the addressbooks
        src = getLabel()
        print src,
        src = listAddressBK(True)

    elif cmdInput in cmdShorts['inbox']:
        src = inbox(False)

    elif cmdInput in cmdShorts['news']:
        src = inbox(True)

    elif cmdInput in cmdShorts['outbox']:
        src = outbox()

    elif cmdInput in cmdShorts['send']:  # Sends a message or broadcast
        uInput = userInput('Would you like to send a (b)roadcast or (M)essage?').lower()
        null = None
        if uInput in inputShorts['broadcast']:
            src = sendBrd(null, null, null)
        else:
            src = sendMsg(null, null, null, null)

    elif cmdInput in cmdShorts['delete']:
        withAtta = True
        uInput = userInput('Would you like to delete message(s) from the (i)nbox or (O)utbox?').lower()

        if uInput in inputShorts['inbox']:
            src = toReadInbox(cmd='delete', withAtta=withAtta)

        else:
            src = toReadOutbox(cmd='delete', withAtta=withAtta)

    elif cmdInput in cmdShorts['read']:  # Opens a message from the inbox for viewing.
        withAtta = False
        uInput = userInput('Would you like to read a message from the (i)nbox or (O)utbox?').lower()

        if uInput in inputShorts['inbox']:
            src = toReadInbox(cmd='read', withAtta=withAtta)

        else:
            src = toReadOutbox(cmd='read', withAtta=withAtta)

    elif cmdInput in cmdShorts['save']:
        uInput = userInput('Would you like to save a message from the (i)nbox or (O)utbox?').lower()

        if uInput in inputShorts['inbox']:
            withAtta = True
            uInput = userInput('Would you like to decode and (s)ave or (D)ump directly?').lower()
            if uInput in inputShorts['save']:
                withAtta = False
            src = toReadInbox(cmd='save', trunck=-1, withAtta=withAtta)

        else:
            withAtta = True
            uInput = userInput('Would you like to decode and (s)ave or (D)ump directly?').lower()
            if uInput in inputShorts['save']:
                withAtta = False

            src = toReadOutbox(cmd='save', trunck=-1, withAtta=withAtta)

    elif cmdInput in cmdShorts['quit']:
        src = '\n     You are already at the main menu. Use "quit" to quit.\n'

    elif cmdInput in cmdShorts['listAddressBK']:
        src = listAddressBK()

    elif cmdInput in cmdShorts['addAddressBK']:
        label = ''
        while uInput == '':
            uInput = userInput('Enter address to add.')
        while label == '':
            label = userInput('Enter label')
        src = addAddressToAddressBook(uInput, label)

    elif cmdInput in cmdShorts['delAddressBK']:
        while uInput == '':
            uInput = userInput('Enter address to delete.')
        src = deleteAddressFromAddressBook(uInput)

    elif cmdInput in cmdShorts['readAll']:
        src = markAllMessagesReadbit(True)

    elif cmdInput in cmdShorts['unreadAll']:
        src = markAllMessagesReadbit(False)

    elif cmdInput in cmdShorts['status']:
        src = clientStatus()

    elif cmdInput in cmdShorts['shutdown']:
        src = shutdown()

    else:
        src = '\n     "' + cmdInput + '" is not a command.\n'

    if src is None or src == '':
        src = retStrings['none']
        usrPrompt = 1
    elif 'Connection' in src or 'ProtocolError' in src:
        usrPrompt = 0
    else:
        usrPrompt = 1

    print src


def CLI():
    """Entrypoint for the CLI app"""

    global usrPrompt, config, api, cmdStr

    if usrPrompt == 0:
        if config.conn:
            api = BMAPIWrapper(config.conn, config.proxy)
            # api.set_proxy(config.proxy)
            if apiTest() is False:
                print
                print '     ****************************************************************'
                print '        WARNING: You are not connected to the Bitmessage API service.'
                print '     Either Bitmessage is not running or your settings are incorrect.'
                print '     Use the command "apiTest" or "bmSettings" to resolve this issue.'
                print '     ****************************************************************\n'

            print '\nType (H)elp for a list of commands.\nPress Enter for default cmd [%s]: ' % cmdStr  # Startup message
            usrPrompt = 2
        else:
            print
            print '     *****************************************************'
            print '        WARNING: API not functionable till you finish the'
            print '     configuration.'
            print '     *****************************************************\n'
            print '\nType (H)elp for a list of commands.\nPress Enter for default cmd [%s]: ' % cmdStr  # Startup message
            usrPrompt = 0

    elif usrPrompt == 1:
        print '\nType (H)elp for a list of commands.\nPress Enter for default cmd [%s]: ' % cmdStr  # Startup message
        usrPrompt = 2

    try:
        cmdInput = raw_input('>').lower().replace(" ", "")
        if cmdInput != '':
            cmdStr = cmdInput  # save as last cmd for replay
        UI(cmdStr)

    except EOFError:
        UI("quit")


if __name__ == "__main__":
    config = Config(sys.argv)
    config.parse()
    bms_allow = False
    socks_allow = False
    if not config.arguments:  # Config parse failed, show the help screen and exit
        config.parse()

    if config.action == 'main':
        try:
            print '- Try to get API connect uri from BMs setting file "keys.dat"...'
            import bmsettings as conninit
            bms_allow = True
            if hasattr(conninit, 'apiData'):
                config.conn = conninit.apiData()
                print '     BMs host uri:', config.conn, '\n'
        except Exception as err:
            print '     Depends check failed, command "bmSettings" disabled. (%s)' % err
            pass

        try:
            print '- Try to get socks module for proxied...'
            from socks import ProxyError, GeneralProxyError, Socks5AuthError, Socks5Error, Socks4Error, HTTPError
            import socks
            if hasattr(socks, 'setdefaultproxy'):
                socks_allow = True
            else:
                print '     Not the correct "socks" module imported.'
        except ImportError as err:
            print '     Depends check failed, "SOCKS" type proxy disabled. (%s)' % err

    if getattr(config, 'start_daemon'):
        start_daemon(getattr(config, 'start_daemon'))

    socks_type = getattr(config, 'proxy_type', 'none')
    proxy = dict()
    if socks_type != 'none':
        if socks_allow is False and 'SOCKS' in socks_type:
            print '     Socks type proxy disabled.'
        else:
            for key in ['proxy_type', 'proxy_path', 'proxy_username', 'proxy_password', 'proxy_remotedns', 'proxy_timeout']:
                proxy[key] = getattr(config, key)
    config.proxy = proxy
    if getattr(config, 'api_path', None):
        if getattr(config, 'api_username', None) and getattr(config, 'api_password', None):
            config.conn = '%s://%s:%s@%s/' % (config.api_type, config.api_username, config.api_password, config.api_path)
        else:
            config.conn = '%s://%s/' % (config.api_type, config.api_path)

    actions = Actions()
    start()
    print 'bye'
    sys.exit()
