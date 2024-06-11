"""
Network subsystem package
"""
from .dandelion import Dandelion
from .threads import StoppableThread

dandelion_ins = Dandelion()

__all__ = ["StoppableThread"]


def start(config, state):
    """Start network threads"""
    import state
    from .announcethread import AnnounceThread
    import connectionpool  # pylint: disable=relative-import
    from .addrthread import AddrThread
    from .downloadthread import DownloadThread
    from .invthread import InvThread
    from .networkthread import BMNetworkThread
    from .knownnodes import readKnownNodes
    from .receivequeuethread import ReceiveQueueThread
    from .uploadthread import UploadThread

    # check and set dandelion enabled value at network startup
    dandelion_ins.init_dandelion_enabled(config)
    # pass pool instance into dandelion class instance
    dandelion_ins.init_pool(connectionpool.pool)

    readKnownNodes()
    connectionpool.pool.connectToStream(1)
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
