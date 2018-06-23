#!/usr/bin/env python2.7

import binascii
import ctypes
import ctypes.util
import os.path
import struct
import sys
import unittest

import __init__
import dumbsolver
import fastsolver
import forkingsolver
import gpusolver
import utils

codePath = os.path.dirname(__file__)

if hasattr(sys, "winver"):
    dumbsolver.libcrypto = ctypes.WinDLL("libcrypto.dll")
else:
    dumbsolver.libcrypto = ctypes.CDLL(ctypes.util.find_library("crypto"))

nonce = binascii.unhexlify("9ca6790a249679f8")
expiryTime = 1525845600

headlessPayload = binascii.unhexlify("000000000001")
initialPayload = struct.pack(">Q", expiryTime) + headlessPayload
payload = nonce + initialPayload

initialHash = binascii.unhexlify(
    "1e87a288a10454dea0d3a9b606cc538db1b8b47fe8a21a37b8e57da3db6928eb"
    "d854fd22aed3e1849c4a1c596fe0bfec266c05900a862c5b356a6b7e51a4b510"
)

doubleHash = binascii.unhexlify(
    "16cdf04b739412bea1bf58d6c5a53ec92e7d4aab180213405bf10d615354d417"
    "00f8b1510d0844a4b7c7b7434e6c115b52fcec5c591e96c31f4b8769ee683552"
)

TTL = 3600
byteDifficulty = 1000
lengthExtension = 1000

target = 0x00000f903320b7f6

seed = binascii.unhexlify("3941c24a1256660a8f65d962954c406dab7bc449317fa087c4a3f1a3ca7d95fd")
timeout = .5

class TestUtils(unittest.TestCase):
    def testCalculateInitialHash(self):
        self.assertEqual(utils.calculateInitialHash(initialPayload), initialHash)

    def testCalculateDoubleHash(self):
        self.assertEqual(utils.calculateDoubleHash(payload), doubleHash)

    def testCalculateTarget(self):
        self.assertEqual(utils.calculateTarget(1000, 1015, 1000, 1000), 0x00000843bf57fed2)
        self.assertEqual(utils.calculateTarget(1000, 1016, 1000, 1000), 0x00000842b4a960c2)

    def testCheckProof(self):
        self.assertFalse(utils.checkProof(nonce, initialHash, 0x000002fe91eba355))
        self.assertTrue(utils.checkProof(nonce, initialHash, 0x000002fe91eba356))

    def testCheckWorkSufficient(self):
        originalTime = utils.time.time

        utils.time.time = lambda: expiryTime - 293757.5
        self.assertFalse(utils.checkWorkSufficient(payload, byteDifficulty, lengthExtension))

        utils.time.time = lambda: expiryTime - 293757
        self.assertTrue(utils.checkWorkSufficient(payload, byteDifficulty, lengthExtension))

        utils.time.time = originalTime

    def testEstimateMaximumIterationsCount(self):
        self.assertEqual(utils.estimateMaximumIterationsCount(0x000fffffffffffff, .1), 512)
        self.assertEqual(utils.estimateMaximumIterationsCount(target, .8), 1735168)

class TestSolver(unittest.TestCase):
    def setUp(self):
        self.solver = self.Solver(codePath)
        self.solver.setParallelism(1)

    def testSearch(self):
        nonce = None

        i = 0

        while nonce is None:
            appendedSeed = seed + struct.pack(">Q", i)
            i += 1

            nonce, iterationsCount = self.solver.search(initialHash, target, appendedSeed, timeout)

        self.assertTrue(utils.checkProof(nonce, initialHash, target))

    def tearDown(self):
        self.solver.setParallelism(0)

class TestDumbSolver(TestSolver):
    Solver = dumbsolver.DumbSolver

class TestForkingSolver(TestSolver):
    Solver = forkingsolver.ForkingSolver

class TestFastSolver(TestSolver):
    Solver = fastsolver.FastSolver

class TestGPUSolver(TestSolver):
    Solver = gpusolver.GPUSolver

class TestWorkProver(unittest.TestCase):
    def setUp(self):
        self.thread = __init__.WorkProver(codePath, None, seed, None)
        self.thread.start()

    def checkTaskLinks(self):
        IDs = set(self.thread.tasks.keys())

        if len(IDs) == 0:
            return

        self.assertIn(self.thread.currentTaskID, IDs)

        linkID = next(iter(IDs))

        for i in xrange(len(IDs)):
            self.assertIn(linkID, IDs)

            IDs.remove(linkID)

            nextLinkID = self.thread.tasks[linkID].next

            self.assertEqual(self.thread.tasks[nextLinkID].previous, linkID)

            linkID = nextLinkID

    def testTasks(self):
        self.thread.addTask(0, headlessPayload, TTL, None, byteDifficulty, lengthExtension)

        self.checkTaskLinks()

        self.thread.addTask(1, headlessPayload, TTL, None, byteDifficulty, lengthExtension)
        self.thread.addTask(2, headlessPayload, TTL, None, byteDifficulty, lengthExtension)

        self.checkTaskLinks()

        self.thread.cancelTask(self.thread.currentTaskID)
        self.thread.nextTask()
        self.thread.nextTask()
        self.thread.nextTask()
        self.thread.addTask(3, headlessPayload, TTL, None, byteDifficulty, lengthExtension)

        self.checkTaskLinks()

    def testSearch(self):
        self.thread.commandsQueue.put((
            "addTask", 0,
            headlessPayload, TTL, None, byteDifficulty, lengthExtension
        ))

        self.thread.commandsQueue.put((
            "addTask", 1,
            headlessPayload, TTL, None, byteDifficulty, lengthExtension
        ))

        self.thread.commandsQueue.put((
            "addTask", 2,
            headlessPayload, TTL * 100, expiryTime, byteDifficulty, lengthExtension
        ))

        self.thread.commandsQueue.put(("setSolver", "dumb", 1))

        for i in xrange(3):
            event, ID, nonce, localExpiryTime = self.thread.resultsQueue.get()

            initialPayload = struct.pack(">Q", localExpiryTime) + headlessPayload
            initialHash = utils.calculateInitialHash(initialPayload)

            self.assertTrue(utils.checkProof(nonce, initialHash, target))

    def tearDown(self):
        self.thread.commandsQueue.put(("shutdown", ))
        self.thread.join()

def load_tests(loader, tests, pattern):
    return unittest.TestSuite([
        loader.loadTestsFromTestCase(TestUtils),
        loader.loadTestsFromTestCase(TestDumbSolver),
        loader.loadTestsFromTestCase(TestForkingSolver),
        loader.loadTestsFromTestCase(TestFastSolver),
        loader.loadTestsFromTestCase(TestGPUSolver),
        loader.loadTestsFromTestCase(TestWorkProver)
    ])

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    runner.run(load_tests(loader, [], None))
