import ctypes
import hashlib
from multiprocessing import current_process
import os
import signal
from struct import unpack, pack
from threading import current_thread

shutdown = 0


def signal_handler(signal, frame):
    global shutdown
    print "Got signal %i in %s/%s" % (signal, current_process().name, current_thread().name)
    if current_process().name != "MainProcess":
        raise StopIteration("Interrupted")
    if current_thread().name != "PyBitmessage":
        return
    shutdown = 1


def _doCPoW(target, initialHash):
#    global shutdown
    h = initialHash
    m = target
    out_h = ctypes.pointer(ctypes.create_string_buffer(h, 64))
    out_m = ctypes.c_ulonglong(m)
    print "C PoW start"
    for c in range(0, 200000):
        print "Iter: %i" % (c)
        nonce = bmpow(out_h, out_m)
        if shutdown:
            break
    trialValue, = unpack('>Q', hashlib.sha512(hashlib.sha512(pack('>Q', nonce) + initialHash).digest()).digest()[0:8])
    if shutdown != 0:
        raise StopIteration("Interrupted")
    print "C PoW done"
    return [trialValue, nonce]


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

bso = ctypes.CDLL(os.path.join("bitmsghash", "bitmsghash.so"))

bmpow = bso.BitmessagePOW
bmpow.restype = ctypes.c_ulonglong

_doCPoW(2**44, "")
