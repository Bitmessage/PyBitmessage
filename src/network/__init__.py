"""
Network subsystem package
"""
from six.moves import queue
from .dandelion import Dandelion
from .threads import StoppableThread
from .multiqueue import MultiQueue

dandelion_ins = Dandelion()

# network queues
invQueue = MultiQueue()
addrQueue = MultiQueue()
portCheckerQueue = queue.Queue()
receiveDataQueue = queue.Queue()

__all__ = ["StoppableThread"]


def start(config, state):
    """Start network threads"""
    from .announcethread import AnnounceThread
    from . import connectionpool
    from .connectionpool import BMConnectionPool
    from .addrthread import AddrThread
    from .downloadthread import DownloadThread
    from .invthread import InvThread
    from .networkthread import BMNetworkThread
    from .knownnodes import readKnownNodes
    from .receivequeuethread import ReceiveQueueThread
    from .uploadthread import UploadThread
    from . import stats

    # create the connection pool
    pool = BMConnectionPool()
    connectionpool.pool = pool

    # check and set dandelion enabled value at network startup
    dandelion_ins.init_dandelion_enabled(config)
    # pass pool instance into dandelion class instance
    dandelion_ins.init_pool(pool)

    # init stats with pool reference
    stats.init(pool)

    readKnownNodes()
    pool.connectToStream(1)
    for thread in (
        BMNetworkThread(pool), InvThread(pool), AddrThread(pool),
        DownloadThread(pool), UploadThread(pool)
    ):
        thread.daemon = True
        thread.start()

    # Optional components
    for i in range(config.getint('threads', 'receive')):
        thread = ReceiveQueueThread(i, pool)
        thread.daemon = True
        thread.start()
    if config.safeGetBoolean('bitmessagesettings', 'udp'):
        state.announceThread = AnnounceThread(pool)
        state.announceThread.daemon = True
        state.announceThread.start()
