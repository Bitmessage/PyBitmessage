import shared
import socket
import defaultKnownNodes
import pickle
import time

from debug import logger
import socks

def knownNodes():
    try:
        # We shouldn't have to use the shared.knownNodesLock because this had
        # better be the only thread accessing knownNodes right now.
        pickleFile = open(shared.appdata + 'knownnodes.dat', 'rb')
        loadedKnownNodes = pickle.load(pickleFile)
        pickleFile.close()
        # The old format of storing knownNodes was as a 'host: (port, time)'
        # mapping. The new format is as 'Peer: time' pairs. If we loaded
        # data in the old format, transform it to the new style.
        for stream, nodes in loadedKnownNodes.items():
            shared.knownNodes[stream] = {}
            for node_tuple in nodes.items():
                try:
                    host, (port, lastseen) = node_tuple
                    peer = shared.Peer(host, port)
                except:
                    peer, lastseen = node_tuple
                shared.knownNodes[stream][peer] = lastseen
    except:
        shared.knownNodes = defaultKnownNodes.createDefaultKnownNodes(shared.appdata)
    # your own onion address, if setup
    if shared.config.has_option('bitmessagesettings', 'onionhostname') and ".onion" in shared.config.get('bitmessagesettings', 'onionhostname'):
        shared.knownNodes[1][shared.Peer(shared.config.get('bitmessagesettings', 'onionhostname'), shared.config.getint('bitmessagesettings', 'onionport'))] = int(time.time())
    if shared.config.getint('bitmessagesettings', 'settingsversion') > 10:
        logger.error('Bitmessage cannot read future versions of the keys file (keys.dat). Run the newer version of Bitmessage.')
        raise SystemExit

def dns():
    # DNS bootstrap. This could be programmed to use the SOCKS proxy to do the
    # DNS lookup some day but for now we will just rely on the entries in
    # defaultKnownNodes.py. Hopefully either they are up to date or the user
    # has run Bitmessage recently without SOCKS turned on and received good
    # bootstrap nodes using that method.
    if shared.config.get('bitmessagesettings', 'socksproxytype') == 'none':
        try:
            for item in socket.getaddrinfo('bootstrap8080.bitmessage.org', 80):
                logger.info('Adding ' + item[4][0] + ' to knownNodes based on DNS bootstrap method')
                shared.knownNodes[1][shared.Peer(item[4][0], 8080)] = int(time.time())
        except:
            logger.error('bootstrap8080.bitmessage.org DNS bootstrapping failed.')
        try:
            for item in socket.getaddrinfo('bootstrap8444.bitmessage.org', 80):
                logger.info ('Adding ' + item[4][0] + ' to knownNodes based on DNS bootstrap method')
                shared.knownNodes[1][shared.Peer(item[4][0], 8444)] = int(time.time())
        except:
            logger.error('bootstrap8444.bitmessage.org DNS bootstrapping failed.')
    elif shared.config.get('bitmessagesettings', 'socksproxytype') == 'SOCKS5':
        shared.knownNodes[1][shared.Peer('quzwelsuziwqgpt2.onion', 8444)] = int(time.time())
        logger.debug("Adding quzwelsuziwqgpt2.onion:8444 to knownNodes.")
        for port in [8080, 8444]:
            logger.debug("Resolving %i through SOCKS...", port)
            address_family = socket.AF_INET
            sock = socks.socksocket(address_family, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(20)
            proxytype = socks.PROXY_TYPE_SOCKS5
            sockshostname = shared.config.get(
                'bitmessagesettings', 'sockshostname')
            socksport = shared.config.getint(
                'bitmessagesettings', 'socksport')
            rdns = True  # Do domain name lookups through the proxy; though this setting doesn't really matter since we won't be doing any domain name lookups anyway.
            if shared.config.getboolean('bitmessagesettings', 'socksauthentication'):
                socksusername = shared.config.get(
                    'bitmessagesettings', 'socksusername')
                sockspassword = shared.config.get(
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
            if ip is not None:
                logger.info ('Adding ' + ip + ' to knownNodes based on SOCKS DNS bootstrap method')
                shared.knownNodes[1][shared.Peer(ip, port)] = time.time()
    else:
        logger.info('DNS bootstrap skipped because the proxy type does not support DNS resolution.')

