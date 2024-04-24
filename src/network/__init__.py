"""
Network subsystem package
"""

try:
    from .announcethread import AnnounceThread
    from .connectionpool import BMConnectionPool
except ImportError:
    AnnounceThread = None
    BMConnectionPool = None
from .threads import StoppableThread


__all__ = ["AnnounceThread", "BMConnectionPool", "StoppableThread"]


def start(config, state):
    """Start network threads"""
    import state
    from .addrthread import AddrThread
    from .dandelion import Dandelion
    from .downloadthread import DownloadThread
    from .invthread import InvThread
    from .networkthread import BMNetworkThread
    from .knownnodes import readKnownNodes
    from .receivequeuethread import ReceiveQueueThread
    from .uploadthread import UploadThread

    readKnownNodes()
    # init, needs to be early because other thread may access it early
    state.Dandelion = Dandelion()
    state.BMConnectionPool = BMConnectionPool()
    state.BMConnectionPool.connectToStream(1)
    for thread in (
        BMNetworkThread(), InvThread(), AddrThread(),
        DownloadThread(), UploadThread()
    ):
        thread.daemon = True
        thread.start()

    # Optional components
    for i in range(config.getint('threads', 'receive')):
        thread = ReceiveQueueThread(i)
        thread.daemon = True
        thread.start()
    if config.safeGetBoolean('bitmessagesettings', 'udp'):
        state.announceThread = AnnounceThread()
        state.announceThread.daemon = True
        state.announceThread.start()
