"""
Create bitmessage protocol command packets
"""
import struct

from pybitmessage import addresses
from pybitmessage.network.constants import MAX_ADDR_COUNT
from pybitmessage.network.node import Peer
from pybitmessage.protocol import CreatePacket, encodeHost


def assemble_addr(peerList):
    """Create address command"""
    if isinstance(peerList, Peer):
        peerList = [peerList]
    if not peerList:
        return b''
    retval = b''
    for i in range(0, len(peerList), MAX_ADDR_COUNT):
        payload = addresses.encodeVarint(len(peerList[i:i + MAX_ADDR_COUNT]))
        for stream, peer, timestamp in peerList[i:i + MAX_ADDR_COUNT]:
            # 64-bit time
            payload += struct.pack('>Q', timestamp)
            payload += struct.pack('>I', stream)
            # service bit flags offered by this node
            payload += struct.pack('>q', 1)
            payload += encodeHost(peer.host)
            # remote port
            payload += struct.pack('>H', peer.port)
        retval += CreatePacket('addr', payload)
    return retval
