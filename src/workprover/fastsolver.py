import sys
import os.path
import platform
import subprocess
import ctypes

class FastSolverError(Exception):
    pass

def loadFastSolver(codePath):
    if hasattr(sys, "winver"):
        suffix = "-32"

        if platform.architecture()[0] == "64bit":
            suffix = "-64"

        path = os.path.join(codePath, "fastsolver/libfastsolver{}.dll".format(suffix))

        try:
            return ctypes.WinDLL(path)
        except:
            raise FastSolverError()

    makePath = os.path.join(codePath, "fastsolver")
    path = os.path.join(codePath, "fastsolver/libfastsolver.so")

    try:
        return ctypes.CDLL(path)
    except:
        if hasattr(sys, "frozen"):
            raise FastSolverError()

        try:
            subprocess.call(["make", "-C", makePath])

            return ctypes.CDLL(path)
        except:
            raise FastSolverError()

class FastSolver(object):
    def __init__(self, codePath):
        self.libfastsolver = loadFastSolver(codePath)

        self.libfastsolver.fastsolver_add.restype = ctypes.c_size_t
        self.libfastsolver.fastsolver_add.argtypes = []

        self.libfastsolver.fastsolver_remove.restype = ctypes.c_size_t
        self.libfastsolver.fastsolver_remove.argtypes = [ctypes.c_size_t]

        self.libfastsolver.fastsolver_search.restype = ctypes.c_int

        self.libfastsolver.fastsolver_search.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_ulonglong, ctypes.c_void_p, ctypes.c_ulonglong
        ]

        self.nonce = ctypes.create_string_buffer(8)
        self.iterationsCount = ctypes.c_ulonglong()

        self.parallelism = 0

    def search(self, initialHash, target, seed, timeout):
        found = self.libfastsolver.fastsolver_search(
            self.nonce, ctypes.byref(self.iterationsCount),
            initialHash, target, seed, long(1000000000 * timeout)
        )

        if found == 1:
            return self.nonce.raw, self.iterationsCount.value
        else:
            return None, self.iterationsCount.value

    def setParallelism(self, parallelism):
        parallelism = min(4096, parallelism)

        for i in xrange(self.parallelism, parallelism):
            self.parallelism = self.libfastsolver.fastsolver_add()

        if parallelism < self.parallelism:
            self.parallelism = self.libfastsolver.fastsolver_remove(self.parallelism - parallelism)
