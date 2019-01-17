"""
Helper Generic perform generic operations for threading.

Also perform some conversion operations.
"""

import socket
import sys
import threading
import traceback
try:
    import multiprocessing
except Exception as e:
    pass
from binascii import hexlify, unhexlify

import shared
import state
import queues
import shutdown
from debug import logger


def powQueueSize():
    curWorkerQueue = queues.workerQueue.qsize()
    for thread in threading.enumerate():
        try:
            if thread.name == "singleWorker":
                curWorkerQueue += thread.busy
        except Exception as err:
            logger.info('Thread error %s', err)
    return curWorkerQueue


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


def allThreadTraceback(frame):
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append(
            '\n# Thread: %s(%d)' % (id2name.get(threadId, ''), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append(
                'File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append('  %s' % (line.strip()))
    print('\n'.join(code))


def signal_handler(signal, frame):
    try:
        process = multiprocessing.current_process()
    except Exception as e:
        process = threading.current_thread()
    logger.error(
        'Got signal %i in %s/%s',
        signal, process.name, threading.current_thread().name
    )
    if process.name == "RegExParser":
        # on Windows this isn't triggered, but it's fine,
        # it has its own process termination thing
        raise SystemExit
    if "PoolWorker" in process.name:
        raise SystemExit
    if threading.current_thread().name not in ("PyBitmessage", "MainThread"):
        return
    logger.error("Got signal %i", signal)
    if shared.thisapp.daemon or not state.enableGUI:  # FIXME redundant?
        shutdown.doCleanShutdown()
    else:
        allThreadTraceback(frame)
        print('Unfortunately you cannot use Ctrl+C when running the UI'
              ' because the UI captures the signal.')


def isHostInPrivateIPRange(host):
    if ":" in host:  # IPv6
        hostAddr = socket.inet_pton(socket.AF_INET6, host)
        if hostAddr == ('\x00' * 15) + '\x01':
            return False
        if hostAddr[0] == '\xFE' and (ord(hostAddr[1]) & 0xc0) == 0x80:
            return False
        if (ord(hostAddr[0]) & 0xfe) == 0xfc:
            return False
    elif ".onion" not in host:
        if host[:3] == '10.':
            return True
        if host[:4] == '172.':
            if host[6] == '.':
                if int(host[4:6]) >= 16 and int(host[4:6]) <= 31:
                    return True
        if host[:8] == '192.168.':
            return True
        # Multicast
        if host[:3] >= 224 and host[:3] <= 239 and host[4] == '.':
            return True
    return False


def addDataPadding(data, desiredMsgLength=12, paddingChar='\x00'):
    return data + paddingChar * (desiredMsgLength - len(data))
