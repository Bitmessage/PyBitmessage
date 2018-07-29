import hashlib
import os.path
import struct

import utils

pyopencl = None
numpy = None

class GPUSolverError(Exception):
    pass

class GPUSolver(object):
    def __init__(self, codePath):
        global pyopencl

        try:
            import pyopencl
        except ImportError:
            raise GPUSolverError()

        self.vendors = {}

        for i in pyopencl.get_platforms():
            devices = i.get_devices(device_type = pyopencl.device_type.GPU)

            if len(devices) != 0:
                self.vendors[i.vendor] = devices[0]

        if len(self.vendors) == 0:
            raise GPUSolverError()

        with open(os.path.join(codePath, "gpusolver.cl")) as file:
            self.source = file.read()

        self.status = None

    def search(self, initialHash, target, seed, timeout):
        startTime = utils.getTimePoint()

        self.hostOutput[0] = 0

        for i in xrange(8):
            self.hostInput[1 + i], = struct.unpack(">Q", initialHash[8 * i: 8 * (i + 1)])

        self.hostInput[9] = target

        pyopencl.enqueue_copy(self.queue, self.output, self.hostOutput[: 1])

        i = 0

        while True:
            randomness = hashlib.sha512(seed + struct.pack(">Q", i)).digest()
            i += 1

            self.hostInput[0], = struct.unpack(">Q", randomness[: 8])

            pyopencl.enqueue_copy(self.queue, self.input, self.hostInput)
            pyopencl.enqueue_nd_range_kernel(self.queue, self.kernel, (self.batchSize, ), None)
            self.queue.finish()
            pyopencl.enqueue_copy(self.queue, self.hostOutput[: 1], self.output)

            solutionsCount = long(self.hostOutput[0])

            if solutionsCount != 0:
                pyopencl.enqueue_copy(self.queue, self.hostOutput[0: 1 + solutionsCount], self.output)

                index, = struct.unpack(">Q", randomness[8: 16])
                threadNumber = self.hostOutput[1 + index % solutionsCount]

                nonce = struct.pack(">Q", long(self.hostInput[0]) + threadNumber)

                if not utils.checkProof(nonce, initialHash, target):
                    raise GPUSolverError()

                return nonce, self.batchSize * i

            if utils.getTimePoint() - startTime >= timeout:
                return None, self.batchSize * i

    def setConfiguration(self, configuration):
        global numpy

        if numpy is not None:
            return

        import numpy

        if configuration is None:
            configuration = self.vendors.keys()[0]

        if configuration not in self.vendors:
            raise GPUSolverError()

        device = self.vendors[configuration]
        context = pyopencl.Context(devices = [device])

        computeUnitsCount = device.get_info(pyopencl.device_info.MAX_COMPUTE_UNITS)
        workGroupSize = device.get_info(pyopencl.device_info.MAX_WORK_GROUP_SIZE)

        self.batchSize = workGroupSize * computeUnitsCount * 256

        self.queue = pyopencl.CommandQueue(context, device)

        program = pyopencl.Program(context, self.source).build()

        self.hostOutput = numpy.zeros(1 + self.batchSize, numpy.uint32)
        self.hostInput = numpy.zeros(1 + 8 + 1, numpy.uint64)

        self.output = pyopencl.Buffer(context, pyopencl.mem_flags.READ_WRITE, 4 * (1 + self.batchSize))
        self.input = pyopencl.Buffer(context, pyopencl.mem_flags.READ_ONLY, 8 * (1 + 8 + 1))

        self.kernel = program.search
        self.kernel.set_args(self.output, self.input)

        self.status = self.batchSize
