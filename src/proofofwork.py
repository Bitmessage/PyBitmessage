#import shared
#import time
#from multiprocessing import Pool, cpu_count
import hashlib
from struct import unpack, pack
import sys
from debug import logger
from shared import config, frozen, codePath, shutdown, safeConfigGetBoolean, UISignalQueue
import openclpow
import tr
import os
import ctypes

def _set_idle():
    if 'linux' in sys.platform:
        import os
        os.nice(20)  # @UndefinedVariable
    else:
        try:
            sys.getwindowsversion()
            import win32api,win32process,win32con  # @UnresolvedImport
            pid = win32api.GetCurrentProcessId()
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
            win32process.SetPriorityClass(handle, win32process.IDLE_PRIORITY_CLASS)
        except:
            #Windows 64-bit
            pass

def _pool_worker(nonce, initialHash, target, pool_size):
    _set_idle()
    trialValue = float('inf')
    while trialValue > target and shutdown == 0:
        nonce += pool_size
        trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    return [trialValue, nonce]

def _doSafePoW(target, initialHash):
    logger.debug("Safe PoW start")
    nonce = 0
    trialValue = float('inf')
    while trialValue > target and shutdown == 0:
        nonce += 1
        trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    if shutdown != 0:
        raise Exception("Interrupted")
    logger.debug("Safe PoW done")
    return [trialValue, nonce]

def _doFastPoW(target, initialHash):
    logger.debug("Fast PoW start")
    import time
    from multiprocessing import Pool, cpu_count
    try:
        pool_size = cpu_count()
    except:
        pool_size = 4
    try:
        maxCores = config.getint('bitmessagesettings', 'maxcores')
    except:
        maxCores = 99999
    if pool_size > maxCores:
        pool_size = maxCores
    pool = Pool(processes=pool_size)
    result = []
    for i in range(pool_size):
        result.append(pool.apply_async(_pool_worker, args = (i, initialHash, target, pool_size)))
    while True:
        if shutdown >= 1:
            pool.terminate()
            raise Exception("Interrupted")
        for i in range(pool_size):
            if result[i].ready():
                result = result[i].get()
                pool.terminate()
                pool.join() #Wait for the workers to exit...
                logger.debug("Fast PoW done")
                return result[0], result[1]
        time.sleep(0.2)
        
def _doCPoW(target, initialHash):
    h = initialHash
    m = target
    out_h = ctypes.pointer(ctypes.create_string_buffer(h, 64))
    out_m = ctypes.c_ulonglong(m)
    logger.debug("C PoW start")
    nonce = bmpow(out_h, out_m)
    trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    if shutdown != 0:
        raise Exception("Interrupted")
    logger.debug("C PoW done")
    return [trialValue, nonce]

def _doGPUPoW(target, initialHash):
    logger.debug("GPU PoW start")
    nonce = openclpow.do_opencl_pow(initialHash.encode("hex"), target)
    trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    #print "{} - value {} < {}".format(nonce, trialValue, target)
    if trialValue > target:
        deviceNames = ", ".join(gpu.name for gpu in openclpow.gpus)
        UISignalQueue.put(('updateStatusBar', tr.translateText("MainWindow",'Your GPU(s) did not calculate correctly, disabling OpenCL. Please report to the developers.')))
        logger.error("Your GPUs (%s) did not calculate correctly, disabling OpenCL. Please report to the developers.", deviceNames)
        openclpow.ctx = False
        raise Exception("GPU did not calculate correctly.")
    if shutdown != 0:
        raise Exception("Interrupted")
    logger.debug("GPU PoW done")
    return [trialValue, nonce]
    
def estimate(difficulty, format = False):
    ret = difficulty / 10
    if ret < 1:
        ret = 1
    if format:
        out = str(int(ret)) + " seconds"
        if ret > 60:
            ret /= 60
            out = str(int(ret)) + " minutes"
        if ret > 60:
            ret /= 60
            out = str(int(ret)) + " hours"
        if ret > 24:
            ret /= 24
            out = str(int(ret)) + " days"
        if ret > 7:
            out = str(int(ret)) + " weeks"
        if ret > 31:
            out = str(int(ret)) + " months"
        if ret > 366:
            ret /= 366
            out = str(int(ret)) + " years"
    else:
        return ret

def run(target, initialHash):
    target = int(target)
    if safeConfigGetBoolean('bitmessagesettings', 'opencl') and openclpow.has_opencl():
#        trialvalue1, nonce1 = _doGPUPoW(target, initialHash)
#        trialvalue, nonce = _doFastPoW(target, initialHash)
#        print "GPU: %s, %s" % (trialvalue1, nonce1)
#        print "Fast: %s, %s" % (trialvalue, nonce)
#        return [trialvalue, nonce]
        try:
            return _doGPUPoW(target, initialHash)
        except:
            if shutdown != 0:
                raise
            pass # fallback
    if bmpow:
        try:
            return _doCPoW(target, initialHash)
        except:
            if shutdown != 0:
                raise
            pass # fallback
    if frozen == "macosx_app" or not frozen:
        # on my (Peter Surda) Windows 10, Windows Defender
        # does not like this and fights with PyBitmessage
        # over CPU, resulting in very slow PoW
        # added on 2015-11-29: multiprocesing.freeze_support() doesn't help
        try:
            return _doFastPoW(target, initialHash)
        except:
            if shutdown != 0:
                raise
            pass #fallback
    try:
        return _doSafePoW(target, initialHash)
    except:
        if shutdown != 0:
            raise
        pass #fallback

# init
bitmsglib = 'bitmsghash.so'
if "win32" == sys.platform:
    if ctypes.sizeof(ctypes.c_voidp) == 4:
        bitmsglib = 'bitmsghash32.dll'
    else:
        bitmsglib = 'bitmsghash64.dll'
    try:
        # MSVS
        bso = ctypes.WinDLL(os.path.join(codePath(), "bitmsghash", bitmsglib))
        logger.info("Loaded C PoW DLL (stdcall) %s", bitmsglib)
        bmpow = bso.BitmessagePOW
        bmpow.restype = ctypes.c_ulonglong
        _doCPoW(2**63, "")
        logger.info("Successfully tested C PoW DLL (stdcall) %s", bitmsglib)
    except:
        logger.error("C PoW test fail.", exc_info=True)
        try:
            # MinGW
            bso = ctypes.CDLL(os.path.join(codePath(), "bitmsghash", bitmsglib))
            logger.info("Loaded C PoW DLL (cdecl) %s", bitmsglib)
            bmpow = bso.BitmessagePOW
            bmpow.restype = ctypes.c_ulonglong
            _doCPoW(2**63, "")
            logger.info("Successfully tested C PoW DLL (cdecl) %s", bitmsglib)
        except:
            logger.error("C PoW test fail.", exc_info=True)
            bso = None
else:
    try:
        bso = ctypes.CDLL(os.path.join(codePath(), "bitmsghash", bitmsglib))
        logger.info("Loaded C PoW DLL %s", bitmsglib)
    except:
        bso = None
if bso:
    try:
        bmpow = bso.BitmessagePOW
        bmpow.restype = ctypes.c_ulonglong
    except:
        bmpow = None
else:
    bmpow = None

