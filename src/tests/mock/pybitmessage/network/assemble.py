"""
Create bitmessage protocol command packets
"""
import struct

import addresses
from network.constants import MAX_ADDR_COUNT
from network.node import Peer
from protocol import CreatePacket, encodeHost


def assemble_addr(peerList):
    """Create address command"""
    if isinstance(peerList, Peer):
        peerList = [peerList]
    if not peerList:
        return bytes()
    retval = bytes()
    for i in range(0, len(peerList), MAX_ADDR_COUNT):
        payload = addresses.encodeVarint(len(peerList[i:i + MAX_ADDR_COUNT]))
        for stream, peer, timestamp in peerList[i:i + MAX_ADDR_COUNT]:
            payload += struct.pack(
                '>Q', int(timestamp))  # 64-bit time

            payload += struct.pack('>I', stream)
            # service bit flags offered by this node
            payload += struct.pack('>q', 1)
            payload += encodeHost(peer.host)
            # remote port
            payload += struct.pack('>H', peer.port)
        retval += CreatePacket('addr', payload)
    return retval
