import os
import socket
import sys
from binascii import hexlify, unhexlify
from multiprocessing import current_process
from threading import current_thread, enumerate

from debug import logger
import shared

def powQueueSize():
    curWorkerQueue = shared.workerQueue.qsize()
    for thread in enumerate():
        try:
            if thread.name == "singleWorker":
                curWorkerQueue += thread.busy
        except:
            pass
    return curWorkerQueue

def invQueueSize():
    curInvQueue = 0
    for thread in enumerate():
        try:
            if thread.name == "objectHashHolder":
                curInvQueue += thread.hashCount()
        except:
            pass
    return curInvQueue

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
    logger.error("Got signal %i in %s/%s", signal, current_process().name, current_thread().name)
    if current_process().name == "RegExParser":
        # on Windows this isn't triggered, but it's fine, it has its own process termination thing
        raise SystemExit
    if "PoolWorker" in current_process().name:
        raise SystemExit
    if current_thread().name != "MainThread":
        return
    logger.error("Got signal %i", signal)
    if shared.safeConfigGetBoolean('bitmessagesettings', 'daemon'):
        shared.doCleanShutdown()
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
