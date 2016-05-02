#!/usr/bin/env python2.7
from struct import pack, unpack
import time
import hashlib
import random
import os

from shared import codePath, safeConfigGetBoolean, shutdown
from debug import logger

libAvailable = True
ctx = False
queue = False
program = False
gpus = []
hash_dt = None

try:
    import numpy
    import pyopencl as cl
except:
    libAvailable = False

def initCL():
    global ctx, queue, program, gpus, hash_dt
    try:
        hash_dt = numpy.dtype([('target', numpy.uint64), ('v', numpy.str_, 73)])
        for platform in cl.get_platforms():
            gpus.extend(platform.get_devices(device_type=cl.device_type.GPU))
        if (len(gpus) > 0):
            ctx = cl.Context(devices=gpus)
            queue = cl.CommandQueue(ctx)
            f = open(os.path.join(codePath(), "bitmsghash", 'bitmsghash.cl'), 'r')
            fstr = ''.join(f.readlines())
            program = cl.Program(ctx, fstr).build(options="")
            logger.info("Loaded OpenCL kernel")
        else:
            logger.info("No OpenCL GPUs found")
            ctx = False
    except Exception as e:
        logger.error("OpenCL fail: ", exc_info=True)
        ctx = False

def has_opencl():
	global ctx
	return (ctx != False)

def do_opencl_pow(hash, target):
	global ctx, queue, program, gpus, hash_dt

	output = numpy.zeros(1, dtype=[('v', numpy.uint64, 1)])
	if (ctx == False):
		return output[0][0]
	
	data = numpy.zeros(1, dtype=hash_dt, order='C')
	data[0]['v'] = ("0000000000000000" + hash).decode("hex")
	data[0]['target'] = target
	
	hash_buf = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=data)
	dest_buf = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, output.nbytes)
	
	kernel = program.kernel_sha512
	worksize = kernel.get_work_group_info(cl.kernel_work_group_info.WORK_GROUP_SIZE, gpus[0])

	kernel.set_arg(0, hash_buf)
	kernel.set_arg(1, dest_buf)

	start = time.time()
	progress = 0
	globamt = worksize*2000

	while output[0][0] == 0 and shutdown == 0:
		kernel.set_arg(2, pack("<Q", progress))
		cl.enqueue_nd_range_kernel(queue, kernel, (globamt,), (worksize,))
		cl.enqueue_read_buffer(queue, dest_buf, output)
		queue.finish()
		progress += globamt
		sofar = time.time() - start
#		logger.debug("Working for %.3fs, %.2f Mh/s", sofar, (progress / sofar) / 1000000)
	if shutdown != 0:
		raise Exception ("Interrupted")
	taken = time.time() - start
#	logger.debug("Took %d tries.", progress)
	return output[0][0]

if libAvailable:
    initCL()

if __name__ == "__main__":
	target = 54227212183L
	initialHash = "3758f55b5a8d902fd3597e4ce6a2d3f23daff735f65d9698c270987f4e67ad590b93f3ffeba0ef2fd08a8dc2f87b68ae5a0dc819ab57f22ad2c4c9c8618a43b3".decode("hex")
	nonce = do_opencl_pow(initialHash.encode("hex"), target)
	trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
	print "{} - value {} < {}".format(nonce, trialValue, target)
	
