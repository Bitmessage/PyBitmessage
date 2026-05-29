"""
Proof of work calculation
"""
# pylint: disable=import-outside-toplevel

import ctypes
import hashlib
import os
import subprocess  # nosec B404
import sys
import tempfile
import time
from struct import pack, unpack

import highlevelcrypto
import openclpow
import paths
import queues
import state
from bmconfigparser import config
from debug import logger
from defaults import (
    networkDefaultProofOfWorkNonceTrialsPerByte,
    networkDefaultPayloadLengthExtraBytes)
from tr import _translate


BITMSGLIB = 'bitmsghash.so'
BMPOW = None


class LogOutput(object):  # pylint: disable=too-few-public-methods
    """
    A context manager that block stdout for its scope
    and appends it's content to log before exit. Usage::

    with LogOutput():
        os.system('ls -l')

    https://stackoverflow.com/questions/5081657
    """

    def __init__(self, prefix='PoW'):
        self.prefix = prefix
        try:
            sys.stdout.flush()
            self._stdout = sys.stdout
            self._stdout_fno = os.dup(sys.stdout.fileno())
        except AttributeError:
            # NullWriter instance has no attribute 'fileno' on Windows
            self._stdout = None
        else:
            self._dst, self._filepath = tempfile.mkstemp()

    def __enter__(self):
        if not self._stdout:
            return
        stdout = os.dup(1)
        os.dup2(self._dst, 1)
        os.close(self._dst)
        sys.stdout = os.fdopen(stdout, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._stdout:
            return
        sys.stdout.close()
        sys.stdout = self._stdout
        sys.stdout.flush()
        os.dup2(self._stdout_fno, 1)

        with open(self._filepath) as out:
            for line in out:
                logger.info('%s: %s', self.prefix, line)
        os.remove(self._filepath)


def _set_idle():
    if 'linux' in sys.platform:
        os.nice(20)
    else:
        try:
            # pylint: disable=no-member,import-error
            sys.getwindowsversion()
            import win32api
            import win32process
            import win32con

            handle = win32api.OpenProcess(
                win32con.PROCESS_ALL_ACCESS, True,
                win32api.GetCurrentProcessId())
            win32process.SetPriorityClass(
                handle, win32process.IDLE_PRIORITY_CLASS)
        except:  # nosec B110 # noqa:E722 pylint:disable=bare-except
            # Windows 64-bit
            pass


def trial_value(nonce, initialHash):
    """Calculate PoW trial value"""
    trialValue, = unpack(
        '>Q', highlevelcrypto.double_sha512(
            pack('>Q', nonce) + initialHash)[0:8])
    return trialValue


def _pool_worker(nonce, initialHash, target, pool_size):
    _set_idle()
    trialValue = float('inf')
    while trialValue > target:
        nonce += pool_size
        trialValue = trial_value(nonce, initialHash)
    return trialValue, nonce


def _doSafePoW(target, initialHash):
    logger.debug('Safe PoW start')
    nonce = 0
    trialValue = float('inf')
    while trialValue > target and state.shutdown == 0:
        nonce += 1
        trialValue = trial_value(nonce, initialHash)
    if state.shutdown != 0:
        raise StopIteration("Interrupted")
    logger.debug('Safe PoW done')
    return trialValue, nonce


def _doFastPoW(target, initialHash):
    # pylint:disable=bare-except
    logger.debug('Fast PoW start')
    from multiprocessing import Pool, cpu_count
    try:
        pool_size = cpu_count()
    except:  # noqa:E722
        pool_size = 4
    maxCores = config.safeGetInt('bitmessagesettings', 'maxcores', 99999)
    pool_size = min(pool_size, maxCores)

    pool = Pool(processes=pool_size)
    result = []
    for i in range(pool_size):
        result.append(pool.apply_async(
            _pool_worker, args=(i, initialHash, target, pool_size)))

    while True:
        if state.shutdown != 0:
            try:
                pool.terminate()
                pool.join()
            except:  # nosec B110 # noqa:E722
                pass
            raise StopIteration("Interrupted")
        for i in range(pool_size):
            if result[i].ready():
                try:
                    result[i].successful()
                except AssertionError:
                    pool.terminate()
                    pool.join()
                    raise StopIteration("Interrupted")
                result = result[i].get()
                pool.terminate()
                pool.join()
                logger.debug('Fast PoW done')
                return result[0], result[1]
        time.sleep(0.2)


def _doCPoW(target, initialHash):
    with LogOutput():
        h = initialHash
        m = target
        out_h = ctypes.pointer(ctypes.create_string_buffer(h, 64))
        out_m = ctypes.c_ulonglong(m)
        logger.debug('C PoW start')
        nonce = BMPOW(out_h, out_m)

    trialValue = trial_value(nonce, initialHash)
    if state.shutdown != 0:
        raise StopIteration("Interrupted")
    logger.debug('C PoW done')
    return trialValue, nonce


def _doGPUPoW(target, initialHash):
    logger.debug('GPU PoW start')
    nonce = openclpow.do_opencl_pow(initialHash.encode("hex"), target)
    trialValue = trial_value(nonce, initialHash)
    if trialValue > target:
        deviceNames = ", ".join(gpu.name for gpu in openclpow.enabledGpus)
        queues.UISignalQueue.put((
            'updateStatusBar', (
                _translate(
                    "MainWindow",
                    "Your GPU(s) did not calculate correctly,"
                    " disabling OpenCL. Please report to the developers."
                ), 1)
        ))
        logger.error(
            'Your GPUs (%s) did not calculate correctly, disabling OpenCL.'
            ' Please report to the developers.', deviceNames)
        openclpow.enabledGpus = []
        raise RuntimeError("GPU did not calculate correctly.")
    if state.shutdown != 0:
        raise StopIteration("Interrupted")
    logger.debug('GPU PoW done')
    return trialValue, nonce


# def estimate(difficulty, fmt=False):
#     ret = difficulty / 10
#     if ret < 1:
#         ret = 1
#
#     if fmt:
#         out = str(int(ret)) + " seconds"
#         if ret > 60:
#             ret /= 60
#             out = str(int(ret)) + " minutes"
#         if ret > 60:
#             ret /= 60
#             out = str(int(ret)) + " hours"
#         if ret > 24:
#             ret /= 24
#             out = str(int(ret)) + " days"
#         if ret > 7:
#             out = str(int(ret)) + " weeks"
#         if ret > 31:
#             out = str(int(ret)) + " months"
#         if ret > 366:
#             ret /= 366
#             out = str(int(ret)) + " years"
#         ret = None  # Ensure legacy behaviour
#
#     return ret


def getPowType():
    """Get the proof of work implementation"""

    if openclpow.openclEnabled():
        return "OpenCL"
    if BMPOW:
        return "C"
    return "python"


def notifyBuild(tried=False):
    """
    Notify the user of the success or otherwise of building the PoW C module
    """

    if BMPOW:
        queues.UISignalQueue.put(('updateStatusBar', (_translate(
            "proofofwork", "C PoW module built successfully."), 1)))
    elif tried:
        queues.UISignalQueue.put(('updateStatusBar', (_translate(
            "proofofwork",
            "Failed to build C PoW module. Please build it manually."), 1)))
    else:
        queues.UISignalQueue.put(('updateStatusBar', (_translate(
            "proofofwork", "C PoW module unavailable. Please build it."), 1)))


def buildCPoW():
    """Attempt to build the PoW C module"""
    if BMPOW is not None:
        return
    if paths.frozen or sys.platform.startswith('win'):
        notifyBuild(False)
        return

    try:
        # GNU make
        make_cmd = ['make', '-C', os.path.join(paths.codePath(), 'bitmsghash')]
        if "bsd" in sys.platform:
            # BSD make
            make_cmd += ['-f', 'Makefile.bsd']

        subprocess.check_call(make_cmd)  # nosec B603
        if os.path.exists(
                os.path.join(paths.codePath(),
                             'bitmsghash',
                             'bitmsghash.so')
        ):
            init()
    except (OSError, subprocess.CalledProcessError):
        pass
    except:  # noqa:E722
        logger.warning(
            'Unexpected exception rised when tried to build bitmsghash lib',
            exc_info=True)
    notifyBuild(True)


def run(target, initialHash):
    """Run the proof of work calculation"""

    if state.shutdown != 0:
        raise StopIteration("Interrupted")
    target = int(target)
    if openclpow.openclEnabled():
        return _doGPUPoW(target, initialHash)
    if BMPOW:
        return _doCPoW(target, initialHash)
    if paths.frozen == "macosx_app" or not paths.frozen:
        # on my (Peter Surda) Windows 10, Windows Defender
        # does not like this and fights with PyBitmessage
        # over CPU, resulting in very slow PoW
        # added on 2015-11-29: multiprocesing.freeze_support() doesn't help
        return _doFastPoW(target, initialHash)

    return _doSafePoW(target, initialHash)


def getTarget(payloadLength, ttl, nonceTrialsPerByte, payloadLengthExtraBytes):
    """Get PoW target for given length, ttl and difficulty params"""
    return 2 ** 64 / (
        nonceTrialsPerByte * (
            payloadLength + 8 + payloadLengthExtraBytes + ((
                ttl * (
                    payloadLength + 8 + payloadLengthExtraBytes
                )) / (2 ** 16))
        ))


def calculate(
        payload, ttl,
        nonceTrialsPerByte=networkDefaultProofOfWorkNonceTrialsPerByte,
        payloadLengthExtraBytes=networkDefaultPayloadLengthExtraBytes
):
    """Do the PoW for the payload and TTL with optional difficulty params"""
    return run(getTarget(len(payload), ttl, nonceTrialsPerByte,
                         payloadLengthExtraBytes),
               hashlib.sha512(payload).digest())


def resetPoW():
    """Initialise the OpenCL PoW"""
    openclpow.initCL()


# init


def init():
    """Initialise PoW"""
    # pylint: disable=broad-exception-caught,global-statement
    global BITMSGLIB, BMPOW

    openclpow.initCL()
    if sys.platform.startswith('win'):
        BITMSGLIB = (
            'bitmsghash32.dll' if ctypes.sizeof(ctypes.c_voidp) == 4 else
            'bitmsghash64.dll')
        libfile = os.path.join(paths.codePath(), 'bitmsghash', BITMSGLIB)
        try:
            # MSVS
            bso = ctypes.WinDLL(
                os.path.join(paths.codePath(), 'bitmsghash', BITMSGLIB))
            logger.info('Loaded C PoW DLL (stdcall) %s', BITMSGLIB)
            BMPOW = bso.BitmessagePOW
            BMPOW.restype = ctypes.c_ulonglong
            _doCPoW(2**63, "")
            logger.info(
                'Successfully tested C PoW DLL (stdcall) %s', BITMSGLIB)
        except ValueError:
            try:
                # MinGW
                # pylint: disable=redefined-variable-type
                bso = ctypes.CDLL(libfile)
                logger.info('Loaded C PoW DLL (cdecl) %s', BITMSGLIB)
                BMPOW = bso.BitmessagePOW
                BMPOW.restype = ctypes.c_ulonglong
                _doCPoW(2**63, "")
                logger.info(
                    'Successfully tested C PoW DLL (cdecl) %s', BITMSGLIB)
            except Exception as e:
                logger.error('Error: %s', e, exc_info=True)
        except Exception as e:
            logger.error('Error: %s', e, exc_info=True)
    else:
        try:
            bso = ctypes.CDLL(
                os.path.join(paths.codePath(), 'bitmsghash', BITMSGLIB))
        except OSError:
            import glob
            try:
                bso = ctypes.CDLL(glob.glob(os.path.join(
                    paths.codePath(), 'bitmsghash', 'bitmsghash*.so'
                ))[0])
            except (OSError, IndexError):
                bso = None
        except Exception:
            bso = None
        else:
            logger.info('Loaded C PoW DLL %s', BITMSGLIB)
        if bso:
            try:
                BMPOW = bso.BitmessagePOW
                BMPOW.restype = ctypes.c_ulonglong
            except Exception:
                logger.warning(
                    'Failed to setup BMPOW lib %s', bso, exc_info=True)
                return

    if BMPOW is None:
        buildCPoW()
