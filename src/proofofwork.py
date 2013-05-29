def _pool_worker(nonce, initialHash, target, pool_size):
    import hashlib
    from struct import unpack, pack
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

