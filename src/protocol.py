import struct
import shared

def getBitfield(address):
    # bitfield of features supported by me (see the wiki).
    bitfield = 0
    # send ack
    if not shared.safeConfigGetBoolean(address, 'dontsendack'):
        bitfield |= shared.BITFIELD_DOESACK
    return struct.pack('>I', bitfield)

def checkBitfield(bitfieldBinary, flags):
    bitfield, = struct.unpack('>I', bitfieldBinary)
    return (bitfield & flags) == flags