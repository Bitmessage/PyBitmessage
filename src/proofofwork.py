def _set_idle():
    import sys
    try:
        sys.getwindowsversion()
        import win32api,win32process,win32con
        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, win32process.IDLE_PRIORITY_CLASS)
    except:
        import os
        os.nice(20)

def _pool_worker(nonce, initialHash, target, pool_size):
    import hashlib
    import sys
    import os
    from struct import unpack, pack
    _set_idle()
    trialValue = 99999999999999999999
    while trialValue > target:
      nonce += pool_size
      trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    return [trialValue, nonce]

def run(target, initialHash):
    from multiprocessing import Pool, cpu_count
    import time
    try:
      pool_size = cpu_count()
    except:
      pool_size = 4
    pool = Pool(processes=pool_size)
    result = []
    for i in range(pool_size):
      result.append(pool.apply_async(_pool_worker, args = (i, initialHash, target, pool_size)))
    while True:
      for i in range(pool_size):
        if result[i].ready():
          result = result[i].get()
          pool.terminate()
          return result[0], result[1]
      time.sleep(1)
