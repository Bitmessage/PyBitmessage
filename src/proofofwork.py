import shared
import time
from multiprocessing import Pool, cpu_count
import hashlib
from struct import unpack, pack

def _pool_worker(nonce, initialHash, target, pool_size):
    trialValue = 99999999999999999999
    while trialValue > target:
        nonce += pool_size
        trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
    return [trialValue, nonce]

def run(target, initialHash):
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
        for i in range(pool_size):
            if shared.shutdown:
                pool.terminate()
                time.sleep(5) #Don't return anything (doing so will cause exceptions because we'll return an unusable response). Sit here and wait for this thread to close.
                return
            if result[i].ready():
                result = result[i].get()
                pool.terminate()
                return result[0], result[1]
        time.sleep(0.2)

