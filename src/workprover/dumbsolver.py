import ctypes
import struct
import hashlib

import utils

libcrypto = None

class DumbSolver(object):
    def __init__(self, codePath):
        libcrypto.SHA512.restype = ctypes.c_void_p

        self.prefixes = [chr(i) for i in xrange(256)]

        if ctypes.c_size_t is ctypes.c_uint:
            self.proofLength = 8 + 64
            self.hashLength = 64
        else:
            # Using the wrapper instead of a clear number slows the work down, but otherwise seems to be unsafe

            self.proofLength = ctypes.c_size_t(8 + 64)
            self.hashLength = ctypes.c_size_t(64)

        self.firstHash = ctypes.create_string_buffer(64)
        self.secondHash = ctypes.create_string_buffer(64)

        self.parallelism = 1

    def search(self, initialHash, target, seed, timeout):
        startTime = utils.getTimePoint()

        sha512 = libcrypto.SHA512

        prefixes = self.prefixes
        proofLength = self.proofLength
        hashLength = self.hashLength
        firstHash = self.firstHash
        secondHash = self.secondHash

        encodedTarget = struct.pack(">Q", target)

        solutions = []
        i = 0

        while True:
            randomness = hashlib.sha512(seed + struct.pack(">Q", i)).digest()
            i += 1

            suffix = randomness[: 7] + initialHash

            for j in prefixes:
                proof = j + suffix

                sha512(j + suffix, proofLength, firstHash)
                sha512(firstHash, hashLength, secondHash)

                if secondHash[: 8] <= encodedTarget:
                    solutions.append(proof[: 8])

            if len(solutions) != 0:
                index, = struct.unpack(">Q", randomness[7: 15])
                nonce = solutions[index % len(solutions)]

                return nonce, 256 * i

            if utils.getTimePoint() - startTime >= timeout:
                return None, 256 * i

    def setParallelism(self, parallelism):
        pass
