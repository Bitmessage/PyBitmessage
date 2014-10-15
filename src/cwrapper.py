# -*- coding: utf-8 -*-
import ctypes
import os
from debug import logger

#Return values for test() from C library 
LIBRARYVERSION = 1
UNSUPPORTED = -1

lib = None

def openLib():
    global lib
    global LIBRARYVERSION
    global UNSUPPORTED

    if ('win' in os.sys.platform):
        libPath = "pybitmessage.dll"
    else:
        libPath = "./pybitmessage.so"

    if not os.access(libPath, os.F_OK):
        return False

    try:
        lib = ctypes.CDLL(libPath)
        return lib.test()
    except:
        lib = None
        return False

def buildLibUnix() :
    logger.debug("Tring to build C library")
    dirChanged = False
    try:
        os.chdir("./c")
        dirChanged = True
        os.system("cc -c -fpic -std=c99 proofofwork.c sha512.c test.c")
        os.system("cc -shared -o pybitmessage.so -std=c99 proofofwork.o sha512.o test.o")
        os.rename("./pybitmessage.so", "./../pybitmessage.so")
        os.chdir("./..")
        logger.debug("Builded C library successfully")
    except:
        if dirChanged:
            os.chdir("./..")
        logger.debug("Faild to build C library")

def init():
    global lib
    global LIBRARYVERSION
    global UNSUPPORTED

    test = openLib()
    if (test == LIBRARYVERSION):
        logger.debug("Using C library")
        return True
    elif (test == UNSUPPORTED):
        logger.debug("No C library support for your platform")
        return False
    else:
        if ('win' in os.sys.platform):
            logger.debug("Can't build C library automatically on windows")
            return False
        else:
            buildLibUnix()
            if (openLib() == LIBRARYVERSION):
                return True
                logger.debug("Using C library")
            else:
                logger.debug("No C library support for your platform or failed to build it")
                return False

def doPoW(_target, _initialHash, _nonce, _poolSize):
    global lib

    #This is needed on windows, because for some reason the variables 
    #are lost in the threads created in _doFastPow().
    if not lib:
        openLib()
    
    target = ctypes.c_uint64(_target)

    chararray = ctypes.c_char * 64
    initialHash = chararray()
    for i in range(0, 63):
        initialHash[i] = _initialHash[i]

    trialValue = ctypes.c_uint64(0)
    nonce = ctypes.c_uint64(_nonce)
    poolSize = ctypes.c_uint(_poolSize)

    lib.doPoW(target, ctypes.byref(initialHash), ctypes.byref(trialValue), ctypes.byref(nonce), poolSize)

    return [trialValue.value, nonce.value]
