"""
Module for Proof of Work using OpenCL
"""
import logging
import os
from struct import pack

import paths
from bmconfigparser import config
from state import shutdown

try:
    import numpy
    import pyopencl as cl
    libAvailable = True
except ImportError:
    libAvailable = False


logger = logging.getLogger('default')

ctx = False
queue = False
program = False
gpus = []
enabledGpus = []
vendors = []
hash_dt = None


def initCL():
    """Initlialise OpenCL engine"""
    global ctx, queue, program, hash_dt  # pylint: disable=global-statement
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
                if config.safeGet("bitmessagesettings", "opencl") == platform.vendor:
                    enabledGpus.extend(platform.get_devices(
                        device_type=cl.device_type.GPU))
                if platform.vendor not in vendors:
                    vendors.append(platform.vendor)
        except:  # noqa:E722
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
