#import shared
#import time
#from multiprocessing import Pool, cpu_count
import hashlib
from struct import unpack, pack
from subprocess import call
import sys
import time
from bmconfigparser import BMConfigParser
from debug import logger
import paths
import openclpow
import queues
import tr
import os
import ctypes

import state

bitmsglib = 'bitmsghash.so'

bmpow = None

def _set_idle():
    if 'linux' in sys.platform:
        os.nice(20)
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
    while trialValue > target:
        nonce += pool_size
        trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    return [trialValue, nonce]

def _doSafePoW(target, initialHash):
    logger.debug("Safe PoW start")
    nonce = 0
    trialValue = float('inf')
    while trialValue > target and state.shutdown == 0:
        nonce += 1
        trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    if state.shutdown != 0:
        raise StopIteration("Interrupted")
    logger.debug("Safe PoW done")
    return [trialValue, nonce]

def _doFastPoW(target, initialHash):
    logger.debug("Fast PoW start")
    from multiprocessing import Pool, cpu_count
    try:
        pool_size = cpu_count()
    except:
        pool_size = 4
    try:
        maxCores = BMConfigParser().getint('bitmessagesettings', 'maxcores')
    except:
        maxCores = 99999
    if pool_size > maxCores:
        pool_size = maxCores

    pool = Pool(processes=pool_size)
    result = []
    for i in range(pool_size):
        result.append(pool.apply_async(_pool_worker, args=(i, initialHash, target, pool_size)))

    while True:
        if state.shutdown > 0:
            try:
                pool.terminate()
                pool.join()
            except:
                pass
            raise StopIteration("Interrupted")
        for i in range(pool_size):
            if result[i].ready():
                try:
                    result[i].successful()
                except AssertionError:
                    pool.terminate()
                    pool.join()
                    raise StopIteration("Interrupted")
                result = result[i].get()
                pool.terminate()
                pool.join()
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
    if state.shutdown != 0:
        raise StopIteration("Interrupted")
    logger.debug("C PoW done")
    return [trialValue, nonce]

def _doGPUPoW(target, initialHash):
    logger.debug("GPU PoW start")
    nonce = openclpow.do_opencl_pow(initialHash.encode("hex"), target)
    trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    #print "{} - value {} < {}".format(nonce, trialValue, target)
    if trialValue > target:
        deviceNames = ", ".join(gpu.name for gpu in openclpow.enabledGpus)
        queues.UISignalQueue.put(('updateStatusBar', (tr._translate("MainWindow",'Your GPU(s) did not calculate correctly, disabling OpenCL. Please report to the developers.'), 1)))
        logger.error("Your GPUs (%s) did not calculate correctly, disabling OpenCL. Please report to the developers.", deviceNames)
        openclpow.enabledGpus = []
        raise Exception("GPU did not calculate correctly.")
    if state.shutdown != 0:
        raise StopIteration("Interrupted")
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

def getPowType():
    if openclpow.openclEnabled():
        return "OpenCL"
    if bmpow:
        return "C"
    return "python"

def notifyBuild(tried=False):
    if bmpow:
        queues.UISignalQueue.put(('updateStatusBar', (tr._translate("proofofwork", "C PoW module built successfully."), 1)))
    elif tried:
        queues.UISignalQueue.put(('updateStatusBar', (tr._translate("proofofwork", "Failed to build C PoW module. Please build it manually."), 1)))
    else:
        queues.UISignalQueue.put(('updateStatusBar', (tr._translate("proofofwork", "C PoW module unavailable. Please build it."), 1)))

def buildCPoW():
    if bmpow is not None:
        return
    if paths.frozen is not None:
        notifyBuild(False)
        return
    if sys.platform in ["win32", "win64"]:
        notifyBuild(False)
        return
    try:
        if "bsd" in sys.platform:
            # BSD make
            call(["make", "-C", os.path.join(paths.codePath(), "bitmsghash"), '-f', 'Makefile.bsd'])
        else:
            # GNU make
            call(["make", "-C", os.path.join(paths.codePath(), "bitmsghash")])
        if os.path.exists(os.path.join(paths.codePath(), "bitmsghash", "bitmsghash.so")):
            init()
            notifyBuild(True)
        else:
            notifyBuild(True)
    except:
        notifyBuild(True)

def run(target, initialHash):
    if state.shutdown != 0:
        raise
    target = int(target)
    if openclpow.openclEnabled():
#        trialvalue1, nonce1 = _doGPUPoW(target, initialHash)
#        trialvalue, nonce = _doFastPoW(target, initialHash)
#        print "GPU: %s, %s" % (trialvalue1, nonce1)
#        print "Fast: %s, %s" % (trialvalue, nonce)
#        return [trialvalue, nonce]
        try:
            return _doGPUPoW(target, initialHash)
        except StopIteration:
            raise
        except:
            pass # fallback
    if bmpow:
        try:
            return _doCPoW(target, initialHash)
        except StopIteration:
            raise
        except:
            pass # fallback
    if paths.frozen == "macosx_app" or not paths.frozen:
        # on my (Peter Surda) Windows 10, Windows Defender
        # does not like this and fights with PyBitmessage
        # over CPU, resulting in very slow PoW
        # added on 2015-11-29: multiprocesing.freeze_support() doesn't help
        try:
            return _doFastPoW(target, initialHash)
        except StopIteration:
            logger.error("Fast PoW got StopIteration")
            raise
        except:
            logger.error("Fast PoW got exception:", exc_info=True)
            pass #fallback
    try:
        return _doSafePoW(target, initialHash)
    except StopIteration:
        raise
    except:
        pass #fallback

def resetPoW():
    openclpow.initCL()

# init
def init():
    global bitmsglib, bso, bmpow

    openclpow.initCL()

    if "win32" == sys.platform:
        if ctypes.sizeof(ctypes.c_voidp) == 4:
            bitmsglib = 'bitmsghash32.dll'
        else:
            bitmsglib = 'bitmsghash64.dll'
        try:
            # MSVS
            bso = ctypes.WinDLL(os.path.join(paths.codePath(), "bitmsghash", bitmsglib))
            logger.info("Loaded C PoW DLL (stdcall) %s", bitmsglib)
            bmpow = bso.BitmessagePOW
            bmpow.restype = ctypes.c_ulonglong
            _doCPoW(2**63, "")
            logger.info("Successfully tested C PoW DLL (stdcall) %s", bitmsglib)
        except:
            logger.error("C PoW test fail.", exc_info=True)
            try:
                # MinGW
                bso = ctypes.CDLL(os.path.join(paths.codePath(), "bitmsghash", bitmsglib))
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
            bso = ctypes.CDLL(os.path.join(paths.codePath(), "bitmsghash", bitmsglib))
        except OSError:
            import glob
            try:
                bso = ctypes.CDLL(glob.glob(os.path.join(
                    paths.codePath(), "bitmsghash", "bitmsghash*.so"
                ))[0])
            except (OSError, IndexError):
                bso = None
        except:
            bso = None
        else:
            logger.info("Loaded C PoW DLL %s", bitmsglib)
    if bso:
        try:
            bmpow = bso.BitmessagePOW
            bmpow.restype = ctypes.c_ulonglong
        except:
            bmpow = None
    else:
        bmpow = None
    if bmpow is None:
        buildCPoW()
