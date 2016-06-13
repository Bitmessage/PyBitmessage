import struct
import shared


def getBitfield(address):
    # Bitfield of features supported by me (see the wiki).
    bitfield = 0
    # Send ack
    if not shared.safeConfigGetBoolean(address, 'dontsendack'):
        bitfield |= shared.BITFIELD_DOESACK
    return struct.pack('>I', bitfield)


def checkBitfield(bitfieldBinary, flags):
    bitfield, = struct.unpack('>I', bitfieldBinary)
    return (bitfield & flags) == flags
