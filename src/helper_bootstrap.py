import shared
import socket
import defaultKnownNodes
import pickle
import time
import logging
logger = logging.getLogger('helper_bootstrap')

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
                    host, (port, time) = node_tuple
                    peer = shared.Peer(host, port)
                except:
                    peer, time = node_tuple
                shared.knownNodes[stream][peer] = time
    except:
        shared.knownNodes = defaultKnownNodes.createDefaultKnownNodes(shared.appdata)
    if shared.config.getint('bitmessagesettings', 'settingsversion') > 7:
        logger.info('Bitmessage cannot read future versions of the keys file (keys.dat). Run the newer version of Bitmessage.')
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
                logger.debug('Adding %s to knownNodes based on DNS boostrap method'%item[4][0])
                shared.knownNodes[1][shared.Peer(item[4][0], 8080)] = int(time.time())
        except:
            logger.info('bootstrap8080.bitmessage.org DNS bootstrapping failed.')
        try:
            for item in socket.getaddrinfo('bootstrap8444.bitmessage.org', 80):
                logger.debug('Adding %s to knownNodes based on DNS boostrap method'%item[4][0])
                shared.knownNodes[1][shared.Peer(item[4][0], 8444)] = int(time.time())
        except:
            logger.info('bootstrap8444.bitmessage.org DNS bootstrapping failed.')
    else:
        logger.info('DNS bootstrap skipped because SOCKS is used.')

