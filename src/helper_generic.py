import shared
import sys

def convertIntToString(n):
    a = __builtins__.hex(n)
    if a[-1:] == 'L':
        a = a[:-1]
    if (len(a) % 2) == 0:
        return a[2:].decode('hex')
    else:
        return ('0' + a[2:]).decode('hex')


def convertStringToInt(s):
    return int(s.encode('hex'), 16)


def signal_handler(signal, frame):
    if shared.safeConfigGetBoolean('bitmessagesettings', 'daemon'):
        shared.doCleanShutdown()
        sys.exit(0)
    else:
        print 'Unfortunately you cannot use Ctrl+C when running the UI because the UI captures the signal.'

def isHostInPrivateIPRange(host):
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
