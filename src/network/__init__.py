"""
Network subsystem package
"""

from .threads import StoppableThread


__all__ = ["StoppableThread"]


def start(config, state):
    """Start network threads"""
    import state
    from .announcethread import AnnounceThread
    import network.connectionpool  # pylint: disable=relative-import
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
