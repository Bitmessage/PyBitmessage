#!/usr/bin/env python2.7
"""
Module for Proof of Work using OpenCL
"""
import hashlib
import os
from struct import pack, unpack

import paths
from bmconfigparser import BMConfigParser
from debug import logger
from state import shutdown

libAvailable = True
ctx = False
queue = False
program = False
gpus = []
enabledGpus = []
vendors = []
hash_dt = None

try:
    import pyopencl as cl
    import numpy
except ImportError:
    libAvailable = False


def initCL():
    """Initlialise OpenCL engine"""
    # pylint: disable=global-statement
    global ctx, queue, program, hash_dt, libAvailable
    if libAvailable is False:
        return
    del enabledGpus[:]
    del vendors[:]
    del gpus[:]
    ctx = False
    try:
        hash_dt = numpy.dtype([('target', numpy.uint64), ('v', numpy.str_, 73)])
        try:
            for platform in cl.get_platforms():
                gpus.extend(platform.get_devices(device_type=cl.device_type.GPU))
                if BMConfigParser().safeGet("bitmessagesettings", "opencl") == platform.vendor:
                    enabledGpus.extend(platform.get_devices(
                        device_type=cl.device_type.GPU))
                if platform.vendor not in vendors:
                    vendors.append(platform.vendor)
        except:
            pass
        if enabledGpus:
            ctx = cl.Context(devices=enabledGpus)
            queue = cl.CommandQueue(ctx)
            f = open(os.path.join(paths.codePath(), "bitmsghash", 'bitmsghash.cl'), 'r')
            fstr = ''.join(f.readlines())
            program = cl.Program(ctx, fstr).build(options="")
            logger.info("Loaded OpenCL kernel")
        else:
            logger.info("No OpenCL GPUs found")
            del enabledGpus[:]
    except Exception:
        logger.error("OpenCL fail: ", exc_info=True)
        del enabledGpus[:]


def openclAvailable():
    """Are there any OpenCL GPUs available?"""
    return bool(gpus)


def openclEnabled():
    """Is OpenCL enabled (and available)?"""
    return bool(enabledGpus)


def do_opencl_pow(hash_, target):
    """Perform PoW using OpenCL"""
    output = numpy.zeros(1, dtype=[('v', numpy.uint64, 1)])
    if not enabledGpus:
        return output[0][0]

    data = numpy.zeros(1, dtype=hash_dt, order='C')
    data[0]['v'] = ("0000000000000000" + hash_).decode("hex")
    data[0]['target'] = target

    hash_buf = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=data)
    dest_buf = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, output.nbytes)

    kernel = program.kernel_sha512
    worksize = kernel.get_work_group_info(cl.kernel_work_group_info.WORK_GROUP_SIZE, enabledGpus[0])

    kernel.set_arg(0, hash_buf)
    kernel.set_arg(1, dest_buf)

    progress = 0
    globamt = worksize * 2000

    while output[0][0] == 0 and shutdown == 0:
        kernel.set_arg(2, pack("<Q", progress))
        cl.enqueue_nd_range_kernel(queue, kernel, (globamt,), (worksize,))
        try:
            cl.enqueue_read_buffer(queue, dest_buf, output)
        except AttributeError:
            cl.enqueue_copy(queue, output, dest_buf)
        queue.finish()
        progress += globamt
    if shutdown != 0:
        raise Exception("Interrupted")
#   logger.debug("Took %d tries.", progress)
    return output[0][0]


if __name__ == "__main__":
    initCL()
    target_ = 54227212183
    initialHash = ("3758f55b5a8d902fd3597e4ce6a2d3f23daff735f65d9698c270987f4e67ad590"
                   "b93f3ffeba0ef2fd08a8dc2f87b68ae5a0dc819ab57f22ad2c4c9c8618a43b3").decode("hex")
    nonce = do_opencl_pow(initialHash.encode("hex"), target_)
    trialValue, = unpack(
        '>Q', hashlib.sha512(hashlib.sha512(pack('>Q', nonce) + initialHash).digest()).digest()[0:8])
    print "{} - value {} < {}".format(nonce, trialValue, target_)
