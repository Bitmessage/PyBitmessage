import hashlib
import struct
import time
import math
import sys
import os

def calculateInitialHash(initialPayload):
    return hashlib.sha512(initialPayload).digest()

def calculateDoubleHash(data):
    return hashlib.sha512(hashlib.sha512(data).digest()).digest()

# Length including nonce

def calculateTarget(length, TTL, byteDifficulty, lengthExtension):
    adjustedLength = length + lengthExtension
    timeEquivalent = TTL * adjustedLength / 2 ** 16

    difficulty = byteDifficulty * (adjustedLength + timeEquivalent)

    return 2 ** 64 / difficulty

def checkProof(nonce, initialHash, target):
    proof = nonce + initialHash
    trial, = struct.unpack(">Q", calculateDoubleHash(proof)[: 8])

    return trial <= target

def checkWorkSufficient(payload, byteDifficulty, lengthExtension):
    expiryTime, = struct.unpack(">Q", payload[8: 16])
    minimumTTL = max(300, expiryTime - int(time.time()))

    nonce = payload[: 8]
    initialHash = calculateInitialHash(payload[8: ])

    target = calculateTarget(len(payload), minimumTTL, byteDifficulty, lengthExtension)

    return checkProof(nonce, initialHash, target)

def estimateMaximumIterationsCount(target, probability):
    coefficient = -math.log(1 - probability)
    difficulty = 2. ** 64 / target

    return int(coefficient * difficulty + 255) / 256 * 256

if hasattr(sys, "winver"):
    getTimePoint = time.clock
else:
    def getTimePoint():
        return os.times()[4]
