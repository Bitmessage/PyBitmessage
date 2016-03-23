import socket
import sys
from binascii import hexlify, unhexlify

import shared

def convertIntToString(n):
    a = __builtins__.hex(n)
    if a[-1:] == 'L':
        a = a[:-1]
    if (len(a) % 2) == 0:
        return unhexlify(a[2:])
    else:
        return unhexlify('0' + a[2:])


def convertStringToInt(s):
    return int(hexlify(s), 16)


def signal_handler(signal, frame):
    if shared.safeConfigGetBoolean('bitmessagesettings', 'daemon'):
        shared.doCleanShutdown()
        sys.exit(0)
    else:
        print 'Unfortunately you cannot use Ctrl+C when running the UI because the UI captures the signal.'

def isHostInPrivateIPRange(host):
    if ":" in host: #IPv6
        hostAddr = socket.inet_pton(socket.AF_INET6, host)
        if hostAddr == ('\x00' * 15) + '\x01':
            return False
        if hostAddr[0] == '\xFE' and (ord(hostAddr[1]) & 0xc0) == 0x80:
            return False
        if (ord(hostAddr[0]) & 0xfe) == 0xfc:
            return False
        pass
    else:
        if host[:3] == '10.':
            return True
        if host[:4] == '172.':
            if host[6] == '.':
                if int(host[4:6]) >= 16 and int(host[4:6]) <= 31:
                    return True
        if host[:8] == '192.168.':
            return True
    return False

def addDataPadding(data, desiredMsgLength = 12, paddingChar = '\x00'):
    return data + paddingChar * (desiredMsgLength - len(data))
