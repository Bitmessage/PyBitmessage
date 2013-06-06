#import shared
#import time
#from multiprocessing import Pool, cpu_count
import hashlib
from struct import unpack, pack
import sys
#import os

def _set_idle():
    if 'linux' in sys.platform:
      import os
      os.nice(20)
    else:
      try:
        sys.getwindowsversion()
        import win32api,win32process,win32con
        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, win32process.IDLE_PRIORITY_CLASS)
      except:
        #Windows 64-bit
        pass

def _pool_worker(nonce, initialHash, target, pool_size):
    _set_idle()
    trialValue = 99999999999999999999
    while trialValue > target:
        nonce += pool_size
        trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    return [trialValue, nonce]

def _doSafePoW(target, initialHash):
    nonce = 0
    trialValue = 99999999999999999999
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
        if shared.shutdown:
            pool.terminate()
            pool.join() #Don't return anything (doing so will cause exceptions because we'll return an unusable response). Sit here and wait for this thread to close.
            return
        for i in range(pool_size):
            if result[i].ready():
                result = result[i].get()
                pool.terminate()
                pool.join() #Wait for the workers to exit...
                return result[0], result[1]
        time.sleep(0.2)

def run(target, initialHash):
    if 'linux' in sys.platform:
      return _doFastPoW(target, initialHash)
    else:
      return _doSafePoW(target, initialHash)
