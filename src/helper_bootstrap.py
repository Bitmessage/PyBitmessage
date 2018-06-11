import socket

import knownnodes
import socks
import state
from bmconfigparser import BMConfigParser
from debug import logger


def dns():
    """
    DNS bootstrap. This could be programmed to use the SOCKS proxy to do the
    DNS lookup some day but for now we will just rely on the entries in
    defaultKnownNodes.py. Hopefully either they are up to date or the user
    has run Bitmessage recently without SOCKS turned on and received good
    bootstrap nodes using that method.
    """

    def try_add_known_node(stream, addr, port, method=''):
        try:
            socket.inet_aton(addr)
        except (TypeError, socket.error):
            return
        logger.info(
            'Adding %s to knownNodes based on %s DNS bootstrap method',
            addr, method)
        knownnodes.addKnownNode(stream, state.Peer(addr, port))

    proxy_type = BMConfigParser().get('bitmessagesettings', 'socksproxytype')

    if proxy_type == 'none':
        for port in [8080, 8444]:
            try:
                for item in socket.getaddrinfo(
                        'bootstrap%s.bitmessage.org' % port, 80):
                    try_add_known_node(1, item[4][0], port)
            except:
                logger.error(
                    'bootstrap%s.bitmessage.org DNS bootstrapping failed.',
                    port, exc_info=True
                )
    elif proxy_type == 'SOCKS5':
        knownnodes.addKnownNode(1, state.Peer('quzwelsuziwqgpt2.onion', 8444))
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
            # Do domain name lookups through the proxy;
            # though this setting doesn't really matter since we won't
            # be doing any domain name lookups anyway.
            rdns = True
            if BMConfigParser().getboolean(
                    'bitmessagesettings', 'socksauthentication'):
                socksusername = BMConfigParser().get(
                    'bitmessagesettings', 'socksusername')
                sockspassword = BMConfigParser().get(
                    'bitmessagesettings', 'sockspassword')
                sock.setproxy(
                    proxytype, sockshostname, socksport, rdns,
                    socksusername, sockspassword)
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
                try_add_known_node(1, ip, port, 'SOCKS')
    else:
        logger.info(
            'DNS bootstrap skipped because the proxy type does not support'
            ' DNS resolution.'
        )
