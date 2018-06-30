import multiprocessing
import os
import struct

import dumbsolver

def setIdle():
    if hasattr(os, "nice"):
        os.nice(40)

        return

    try:
        import psutil

        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)

        return
    except:
        pass

    try:
        import win32api
        import win32con
        import win32process

        PID = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, PID)

        win32process.SetPriorityClass(handle, win32process.IDLE_PRIORITY_CLASS)
    except:
        pass

def threadFunction(local, remote, codePath, threadNumber):
    remote.close()
    setIdle()

    solver = dumbsolver.DumbSolver(codePath)

    while True:
        received = local.recv()

        command = received[0]
        arguments = received[1: ]

        if command == "search":
            initialHash, target, seed, timeout = arguments
            appendedSeed = seed + struct.pack(">Q", threadNumber)

            nonce, iterationsCount = solver.search(initialHash, target, appendedSeed, timeout)

            local.send(("done", nonce, iterationsCount))
        elif command == "shutdown":
            local.close()

            return

class ForkingSolver(object):
    def __init__(self, codePath):
        self.pipes = []
        self.processes = []

        self.status = 0

        self.codePath = codePath

    def search(self, initialHash, target, seed, timeout):
        for i in self.pipes:
            i.send(("search", initialHash, target, seed, timeout))

        bestNonce, totalIterationsCount = None, 0

        for i in self.pipes:
            event, nonce, iterationsCount = i.recv()

            if nonce is not None:
                bestNonce = nonce

            totalIterationsCount += iterationsCount

        return bestNonce, totalIterationsCount

    def setConfiguration(self, configuration):
        if configuration is None:
            parallelism = 0
        else:
            parallelism = min(4096, configuration)

        for i in xrange(len(self.processes), parallelism):
            local, remote = multiprocessing.Pipe()

            process = multiprocessing.Process(
                target = threadFunction,
                args = (remote, local, self.codePath, i),
                name = "ForkingSolver"
            )

            process.start()

            remote.close()

            self.pipes.append(local)
            self.processes.append(process)

        for i in xrange(parallelism, len(self.processes)):
            pipe = self.pipes.pop()

            pipe.send(("shutdown", ))
            pipe.close()

        for i in xrange(parallelism, len(self.processes)):
            self.processes.pop().join()

        self.status = parallelism
