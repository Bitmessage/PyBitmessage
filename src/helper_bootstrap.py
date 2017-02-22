import socket
import defaultKnownNodes
import pickle
import time

from bmconfigparser import BMConfigParser
from debug import logger
import knownnodes
import socks
import state

def knownNodes():
    try:
        # We shouldn't have to use the knownnodes.knownNodesLock because this had
        # better be the only thread accessing knownNodes right now.
        pickleFile = open(state.appdata + 'knownnodes.dat', 'rb')
        loadedKnownNodes = pickle.load(pickleFile)
        pickleFile.close()
        # The old format of storing knownNodes was as a 'host: (port, time)'
        # mapping. The new format is as 'Peer: time' pairs. If we loaded
        # data in the old format, transform it to the new style.
        for stream, nodes in loadedKnownNodes.items():
            knownnodes.knownNodes[stream] = {}
            for node_tuple in nodes.items():
                try:
                    host, (port, lastseen) = node_tuple
                    peer = state.Peer(host, port)
                except:
                    peer, lastseen = node_tuple
                knownnodes.knownNodes[stream][peer] = lastseen
    except:
        knownnodes.knownNodes = defaultKnownNodes.createDefaultKnownNodes(state.appdata)
    # your own onion address, if setup
    if BMConfigParser().has_option('bitmessagesettings', 'onionhostname') and ".onion" in BMConfigParser().get('bitmessagesettings', 'onionhostname'):
        knownnodes.knownNodes[1][state.Peer(BMConfigParser().get('bitmessagesettings', 'onionhostname'), BMConfigParser().getint('bitmessagesettings', 'onionport'))] = int(time.time())
    if BMConfigParser().getint('bitmessagesettings', 'settingsversion') > 10:
        logger.error('Bitmessage cannot read future versions of the keys file (keys.dat). Run the newer version of Bitmessage.')
        raise SystemExit

def dns():
    # DNS bootstrap. This could be programmed to use the SOCKS proxy to do the
    # DNS lookup some day but for now we will just rely on the entries in
    # defaultKnownNodes.py. Hopefully either they are up to date or the user
    # has run Bitmessage recently without SOCKS turned on and received good
    # bootstrap nodes using that method.
    if BMConfigParser().get('bitmessagesettings', 'socksproxytype') == 'none':
        try:
            for item in socket.getaddrinfo('bootstrap8080.bitmessage.org', 80):
                logger.info('Adding ' + item[4][0] + ' to knownNodes based on DNS bootstrap method')
                knownnodes.knownNodes[1][state.Peer(item[4][0], 8080)] = int(time.time())
        except:
            logger.error('bootstrap8080.bitmessage.org DNS bootstrapping failed.')
        try:
            for item in socket.getaddrinfo('bootstrap8444.bitmessage.org', 80):
                logger.info ('Adding ' + item[4][0] + ' to knownNodes based on DNS bootstrap method')
                knownnodes.knownNodes[1][state.Peer(item[4][0], 8444)] = int(time.time())
        except:
            logger.error('bootstrap8444.bitmessage.org DNS bootstrapping failed.')
    elif BMConfigParser().get('bitmessagesettings', 'socksproxytype') == 'SOCKS5':
        knownnodes.knownNodes[1][state.Peer('quzwelsuziwqgpt2.onion', 8444)] = int(time.time())
        logger.debug("Adding quzwelsuziwqgpt2.onion:8444 to knownNodes.")
        for port in [8080, 8444]:
            logger.debug("Resolving %i through SOCKS...", port)
            address_family = socket.AF_INET
            sock = socks.socksocket(address_family, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(20)
            proxytype = socks.PROXY_TYPE_SOCKS5
            sockshostname = BMConfigParser().get(
                'bitmessagesettings', 'sockshostname')
            socksport = BMConfigParser().getint(
                'bitmessagesettings', 'socksport')
            rdns = True  # Do domain name lookups through the proxy; though this setting doesn't really matter since we won't be doing any domain name lookups anyway.
            if BMConfigParser().getboolean('bitmessagesettings', 'socksauthentication'):
                socksusername = BMConfigParser().get(
                    'bitmessagesettings', 'socksusername')
                sockspassword = BMConfigParser().get(
                    'bitmessagesettings', 'sockspassword')
                sock.setproxy(
                    proxytype, sockshostname, socksport, rdns, socksusername, sockspassword)
            else:
                sock.setproxy(
                    proxytype, sockshostname, socksport, rdns)
            try:
                ip = sock.resolve("bootstrap" + str(port) + ".bitmessage.org")
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except:
                logger.error("SOCKS DNS resolving failed", exc_info=True)
            else:
                if ip is not None:
                    logger.info ('Adding ' + ip + ' to knownNodes based on SOCKS DNS bootstrap method')
                    knownnodes.knownNodes[1][state.Peer(ip, port)] = time.time()
    else:
        logger.info('DNS bootstrap skipped because the proxy type does not support DNS resolution.')

