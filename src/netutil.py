import os
import sys
import socket
import select
import contextlib

from debug import logger
from socks import socksocket

class IPv6NotSupportedError(Exception): pass

def packNetworkAddress(address):
    # Works on most modern posix distros.
    if hasattr(socket, 'inet_pton'):
        try:
            # Matches IPV4-style address.
            # TODO(fiatflux): this matching is kinda clunky.
            if ':' not in address and address.count('.') == 3:
                return socket.inet_pton(socket.AF_INET6, '::ffff:' + address)
            # IPV4-mapped IPV6 and plain IPV6.
            else:
                return socket.inet_pton(socket.AF_INET6, address)
        except Exception as err:
            logger.error('Failed to pack address "%s". Err: %s' % (address, err))
            raise

    # For some systems, we need to avoid socket.inet_pton()
    else:
        try:
            # Matches IPV4-style address.
            if ':' not in address and address.count('.') == 3:
                # Already in IPv6 format; no address curtailing needed.
                pass
            elif address.lower().startswith('::ffff:'):
                # Chop off the IPv4-mapped IPv6 prefix from the standard-form address.
                address = address[7:]
            else:
                raise IPv6NotSupportedError(
                        'IPv6 not supported by packNetworkAddress on your system')
            # Pack the standard-form IPv4 address and add prefix to make packed IPv4-mapped IPv6.
            return '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
                    socket.inet_aton(address)
        except Exception as err:
            logger.error('Failed to pack address "%s". Err: %s' % (address, err))
            raise

# Take packed IPv6 address and return unpacked IPv6 string
# in standard notation (e.g. ::ffff:127.0.0.1).
def unpackNetworkAddress(packedAddress):
    # Works on most modern posix distros.
    if hasattr(socket, 'inet_ntop'):
        try:
            return socket.inet_ntop(socket.AF_INET6, packedAddress)
        except:
            logger.debug('Failed to unpack address %s.' % repr(packedAddress))
            raise

    # For some systems, we need to avoid socket.inet_ntop()
    else:
        try:
            if not packedAddress.startswith('\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF'):
                raise IPv6NotSupportedError(
                        'IPv6 not supported by {,un}packNetworkAddress on your system')
        except:
            logger.debug('Failed to unpack address %s.' % repr(packedAddress))
            raise
        return '::ffff:' + socket.inet_ntoa(packedAddress[12:])
