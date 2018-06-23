import sys
import multiprocessing
import time
import struct
import threading
import Queue
import collections

import utils
import dumbsolver
import forkingsolver
import fastsolver
import gpusolver

timeout = .5

class Stop(Exception):
    pass

class Task(object):
    previous = None
    next = None

    def __init__(self, headlessPayload, TTL, expiryTime, target):
        self.headlessPayload = headlessPayload
        self.TTL = TTL
        self.expiryTime = expiryTime
        self.target = target

class WorkProver(threading.Thread):
    def __init__(self, codePath, GPUVendors, seed, statusUpdated):
        super(self.__class__, self).__init__()

        self.availableSolvers = {
            "dumb": dumbsolver.DumbSolver(codePath)
        }

        # Comment from the previous version:

        # on my (Peter Surda) Windows 10, Windows Defender
        # does not like this and fights with PyBitmessage
        # over CPU, resulting in very slow PoW
        # added on 2015-11-29: multiprocesing.freeze_support() doesn't help

        if not hasattr(sys, "frozen") or sys.frozen == "macosx_app":
            self.availableSolvers["forking"] = forkingsolver.ForkingSolver(codePath)

        try:
            self.availableSolvers["fast"] = fastsolver.FastSolver(codePath)
        except:
            pass

        try:
            self.availableSolvers["gpu"] = gpusolver.GPUSolver(codePath, GPUVendors)
        except:
            pass

        try:
            self.defaultParallelism = multiprocessing.cpu_count()
        except NotImplementedError:
            self.defaultParallelism = 1

        self.seed = seed
        self.roundsCounter = 0
        self.statusUpdated = statusUpdated

        self.commandsQueue = Queue.Queue()
        self.resultsQueue = Queue.Queue()

        self.solverName = None
        self.solver = None

        self.lastTime = utils.getTimePoint()
        self.timedIntervals = collections.deque()
        self.speed = 0

        self.tasks = {}
        self.currentTaskID = None

    def notifyStatus(self):
        if self.statusUpdated is None:
            return

        if self.solver is None:
            parallelism = 0
        else:
            parallelism = self.solver.parallelism

        self.statusUpdated((self.solverName, parallelism, self.speed))

    def setSolver(self, name, parallelism):
        if name is None and self.solverName is None:
            pass
        elif name == self.solverName:
            if self.solver.parallelism != parallelism:
                self.solver.setParallelism(parallelism)
        else:
            if self.solver is not None:
                self.solver.setParallelism(0)
                self.solverName = None
                self.solver = None

            if name is not None:
                if name not in self.availableSolvers:
                    name, parallelism = "dumb", 1

                self.solverName = name
                self.solver = self.availableSolvers[name]
                self.solver.setParallelism(parallelism)

        self.notifyStatus()

    def updateSpeed(self, iterationsCount):
        currentTime = utils.getTimePoint()
        duration = currentTime - self.lastTime
        self.lastTime = currentTime

        self.timedIntervals.append((currentTime, iterationsCount, duration))

        for i in xrange(len(self.timedIntervals)):
            time, iterationsCount, duration = self.timedIntervals[0]

            if time + duration < currentTime - 3:
                self.timedIntervals.popleft()

        totalDuration = 0
        totalIterationsCount = 0

        for time, iterationsCount, duration in self.timedIntervals:
            totalIterationsCount += iterationsCount
            totalDuration += duration

        if totalDuration < .25:
            self.speed = 0
        else:
            self.speed = totalIterationsCount / totalDuration

        self.notifyStatus()

    def addTask(self, ID, headlessPayload, TTL, expiryTime, byteDifficulty, lengthExtension):
        target = utils.calculateTarget(8 + 8 + len(headlessPayload), TTL, byteDifficulty, lengthExtension)

        task = Task(headlessPayload, TTL, expiryTime, target)

        self.tasks[ID] = task

        if self.currentTaskID is None:
            task.previous = ID
            task.next = ID

            self.currentTaskID = ID
        else:
            task.previous = self.currentTaskID
            task.next = self.tasks[self.currentTaskID].next

            self.tasks[task.previous].next = ID
            self.tasks[task.next].previous = ID

    def cancelTask(self, ID):
        if ID not in self.tasks:
            return

        task = self.tasks.pop(ID)

        if len(self.tasks) == 0:
            self.currentTaskID = None
        else:
            self.tasks[task.previous].next = task.next
            self.tasks[task.next].previous = task.previous

            if self.currentTaskID == ID:
                self.currentTaskID = task.next

    def nextTask(self):
        self.currentTaskID = self.tasks[self.currentTaskID].next

    def shutdown(self):
        self.setSolver(None, 0)

        for i in self.tasks.keys():
            self.cancelTask(i)

        raise Stop()

    def processCommand(self, command, *arguments):
        getattr(self, command)(*arguments)

    def round(self):
        while True:
            try:
                self.processCommand(*self.commandsQueue.get_nowait())
            except Queue.Empty:
                break

        while self.solver is None or self.currentTaskID is None:
            try:
                self.processCommand(*self.commandsQueue.get(True, timeout))
            except Queue.Empty:
                self.updateSpeed(0)

        task = self.tasks[self.currentTaskID]

        if task.expiryTime is None:
            expiryTime = int(time.time() + task.TTL)
        else:
            expiryTime = task.expiryTime

        initialPayload = struct.pack(">Q", expiryTime) + task.headlessPayload
        initialHash = utils.calculateInitialHash(initialPayload)

        appendedSeed = self.seed + struct.pack(">Q", self.roundsCounter)
        self.roundsCounter += 1

        try:
            nonce, iterationsCount = self.solver.search(initialHash, task.target, appendedSeed, timeout)
        except gpusolver.GPUSolverError:
            self.setSolver("dumb", 1)
            self.availableSolvers.pop("gpu")

            nonce, iterationsCount = None, 0

        self.updateSpeed(iterationsCount)

        if nonce is None:
            self.nextTask()
        else:
            self.resultsQueue.put(("taskDone", self.currentTaskID, nonce, expiryTime))

            self.cancelTask(self.currentTaskID)

    def run(self):
        try:
            while True:
                self.round()
        except Stop:
            return
        except Exception as exception:
            self.resultsQueue.put(exception)
