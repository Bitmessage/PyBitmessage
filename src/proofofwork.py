#import shared
#import time
#from multiprocessing import Pool, cpu_count
import hashlib
from struct import unpack, pack
import sys
from shared import config, frozen
#import os

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
    while trialValue > target:
        nonce += pool_size
        trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    return [trialValue, nonce]

def _doSafePoW(target, initialHash):
    nonce = 0
    trialValue = float('inf')
    while trialValue > target:
        nonce += 1
        trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    return [trialValue, nonce]

def _doFastPoW(target, initialHash):
    import shared
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
        if shared.shutdown >= 1:
            pool.terminate()
            while True:
                time.sleep(10) # Don't let this thread return here; it will return nothing and cause an exception in bitmessagemain.py
            return
        for i in range(pool_size):
            if result[i].ready():
                result = result[i].get()
                pool.terminate()
                pool.join() #Wait for the workers to exit...
                return result[0], result[1]
        time.sleep(0.2)

def run(target, initialHash):
    if frozen == "macosx_app" or not frozen:
        return _doFastPoW(target, initialHash)
    else:
        return _doSafePoW(target, initialHash)
